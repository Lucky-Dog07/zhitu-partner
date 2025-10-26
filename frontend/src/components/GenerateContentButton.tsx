import React, { useState } from 'react';
import { Button, message } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';
import { learningPathAPI } from '../services/api';

interface GenerateContentButtonProps {
  pathId: number;
  contentType: string;
  label?: string;
  buttonText?: string;
  icon?: React.ReactNode;
  onGenerated?: (content: any) => void;
  disabled?: boolean;
}

// 内容类型的中文名称映射
const CONTENT_TYPE_NAMES: Record<string, string> = {
  knowledge: '知识点详解',
  interview: '面试题库',
  courses: '课程推荐',
  books: '书籍推荐',
  certifications: '证书推荐'
};

// 预计生成时间（秒）
const ESTIMATED_TIME: Record<string, number> = {
  knowledge: 30,
  interview: 25,
  courses: 5,
  books: 5,
  certifications: 5
};

const GenerateContentButton: React.FC<GenerateContentButtonProps> = ({
  pathId,
  contentType,
  label,
  buttonText,
  icon,
  onGenerated,
  disabled = false
}) => {
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    const typeName = CONTENT_TYPE_NAMES[contentType] || contentType;
    const estimatedTime = ESTIMATED_TIME[contentType] || 20;

    try {
      message.loading({
        content: `正在生成${typeName}，预计需要${estimatedTime}秒...`,
        key: 'generate',
        duration: 0
      });

      const result = await learningPathAPI.generateContent(pathId, contentType);
      
      console.log('[DEBUG] API返回结果:', result);
      console.log('[DEBUG] 内容长度:', result.content?.length);

      message.destroy('generate');

      if (result.success) {
        if (result.from_cache) {
          message.info(`${typeName}已存在，从缓存加载`);
        } else {
          message.success(`${typeName}生成成功！`);
        }

        // 调用回调函数，传递生成的内容
        if (onGenerated) {
          console.log('[DEBUG] 调用onGenerated回调');
          console.log('[DEBUG] 传递的内容:', result.content);
          console.log('[DEBUG] 内容是数组吗?', Array.isArray(result.content));
          console.log('[DEBUG] 内容数量:', result.content?.length);
          onGenerated(result.content);
        }
      } else {
        // 检查是否是"没有更多资源"的情况
        if (result.no_more_resources) {
          message.warning(result.message || '暂无更多推荐');
          // 仍然调用回调，确保前端显示现有资源
          if (onGenerated && result.content) {
            onGenerated(result.content);
          }
        } else {
          message.error(result.message || '生成失败');
        }
      }
    } catch (error: any) {
      message.destroy('generate');
      message.error(error.response?.data?.detail || '生成失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const defaultText = label || buttonText || `生成${CONTENT_TYPE_NAMES[contentType] || '内容'}`;
  const buttonIcon = icon || <ThunderboltOutlined />;

  return (
    <Button
      type="primary"
      size="large"
      icon={buttonIcon}
      loading={loading}
      disabled={disabled}
      onClick={handleGenerate}
      block
      style={{ height: 48 }}
    >
      {loading ? '正在生成...' : defaultText}
    </Button>
  );
};

export default GenerateContentButton;

