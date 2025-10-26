import React, { useEffect, useRef } from 'react';
import { Transformer } from 'markmap-lib';
import { Markmap } from 'markmap-view';

interface MindMapProps {
  markdown: string;
  height?: number;
}

const MindMapComponent: React.FC<MindMapProps> = ({ markdown, height = 600 }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const mmRef = useRef<Markmap | null>(null);

  useEffect(() => {
    if (!svgRef.current || !markdown) return;

    try {
      // 转换Markdown为思维导图数据
      const transformer = new Transformer();
      const { root } = transformer.transform(markdown);

      // 创建或更新思维导图
      if (!mmRef.current) {
        mmRef.current = Markmap.create(svgRef.current, {
          duration: 500,
          maxWidth: 300,
          initialExpandLevel: 2,
          spacingHorizontal: 80,
          spacingVertical: 10,
          paddingX: 20,
          autoFit: true,
          color: (node: any) => {
            // 根据层级设置不同颜色
            const colors = [
              '#1677ff', // 一级节点 - 蓝色
              '#52c41a', // 二级节点 - 绿色
              '#faad14', // 三级节点 - 橙色
              '#f5222d', // 四级节点 - 红色
              '#722ed1', // 五级节点 - 紫色
              '#13c2c2', // 六级节点 - 青色
            ];
            return colors[node.depth % colors.length];
          }
        });
      }

      // 渲染思维导图
      mmRef.current.setData(root);
      mmRef.current.fit();

      // 添加双击事件监听器，支持链接跳转
      const handleDoubleClick = (e: MouseEvent) => {
        const target = e.target as HTMLElement;
        
        // 查找最近的a标签
        const link = target.closest('a');
        
        if (link && link.getAttribute('href')) {
          e.preventDefault();
          e.stopPropagation();
          
          const href = link.getAttribute('href');
          if (href && (href.startsWith('http://') || href.startsWith('https://'))) {
            // 在新标签页打开链接
            window.open(href, '_blank', 'noopener,noreferrer');
          }
        }
      };

      // 添加事件监听
      svgRef.current.addEventListener('dblclick', handleDoubleClick);

      // 保存当前的svgRef用于清理
      const currentSvg = svgRef.current;

      // 清理函数
      return () => {
        if (currentSvg) {
          currentSvg.removeEventListener('dblclick', handleDoubleClick);
        }
        if (mmRef.current) {
          mmRef.current.destroy();
          mmRef.current = null;
        }
      };
    } catch (error) {
      console.error('思维导图渲染失败:', error);
    }
  }, [markdown]);

  return (
    <div style={{ 
      width: '100%', 
      height: `${height}px`, 
      border: '1px solid #e8e8e8', 
      borderRadius: 8,
      background: '#fafafa',
      overflow: 'hidden'
    }}>
      <style>{`
        /* 思维导图节点圆点样式 - 使用更通用的选择器 */
        svg g[data-type="node"] circle {
          fill: #333 !important;
          stroke: #666 !important;
          stroke-width: 1.5px !important;
        }
        
        /* 展开/折叠状态的圆点 */
        svg circle[fill="#fff"],
        svg circle[fill="white"],
        svg circle[fill="rgb(255, 255, 255)"] {
          fill: #888 !important;
          stroke: #666 !important;
        }
        
        /* hover状态 */
        svg g[data-type="node"]:hover circle {
          fill: #555 !important;
          stroke: #333 !important;
        }
      `}</style>
      <svg
        ref={svgRef}
        style={{ 
          width: '100%', 
          height: '100%',
          cursor: 'move'
        }}
      />
    </div>
  );
};

export default MindMapComponent;

