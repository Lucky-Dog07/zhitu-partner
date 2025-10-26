import React, { useEffect, useRef } from 'react';
import { Transformer } from 'markmap-lib';
import { Markmap } from 'markmap-view';
import { Empty } from 'antd';

interface NoteMindMapProps {
  content: string;
  editorMode: 'markdown' | 'rich_text';
}

const NoteMindMap: React.FC<NoteMindMapProps> = ({ content, editorMode }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const mmRef = useRef<Markmap | null>(null);

  useEffect(() => {
    if (!svgRef.current || !content) return;

    try {
      // 如果是富文本，尝试提取标题结构
      let markdownContent = content;
      if (editorMode === 'rich_text') {
        // 简单的HTML到Markdown转换（提取h1-h6标题）
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;
        const headings = tempDiv.querySelectorAll('h1, h2, h3, h4, h5, h6');
        
        if (headings.length > 0) {
          markdownContent = Array.from(headings).map(h => {
            const level = parseInt(h.tagName.substring(1));
            return '#'.repeat(level) + ' ' + h.textContent;
          }).join('\n');
        } else {
          // 如果没有标题，使用第一行作为根节点
          const lines = content.replace(/<[^>]*>/g, '').split('\n').filter(l => l.trim());
          markdownContent = lines.map((line, idx) => {
            return `${'#'.repeat(idx === 0 ? 1 : 2)} ${line}`;
          }).join('\n');
        }
      }

      const transformer = new Transformer();
      const { root } = transformer.transform(markdownContent);

      if (!mmRef.current) {
        mmRef.current = Markmap.create(svgRef.current, {
          duration: 500,
          maxWidth: 300,
          zoom: true,
          pan: true,
        });
      }

      mmRef.current.setData(root);
      mmRef.current.fit();
    } catch (error) {
      console.error('思维导图渲染错误:', error);
    }
  }, [content, editorMode]);

  if (!content) {
    return <Empty description="暂无内容" />;
  }

  return (
    <div style={{ width: '100%', height: '500px', border: '1px solid #d9d9d9', borderRadius: '4px' }}>
      <svg ref={svgRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
};

export default NoteMindMap;

