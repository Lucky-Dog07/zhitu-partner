import React from 'react';
import { Empty, Alert } from 'antd';
import { BookOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import GenerateContentButton from './GenerateContentButton';

interface KnowledgeTabProps {
  pathId: number;
  content?: string;
  onContentGenerated: (content: any) => void;
}

const KnowledgeTab: React.FC<KnowledgeTabProps> = ({
  pathId,
  content,
  onContentGenerated
}) => {
  if (!content) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <Empty
          image={<BookOutlined style={{ fontSize: 64, color: '#1677ff' }} />}
          description={
            <div>
              <p style={{ fontSize: 16, marginBottom: 20 }}>
                知识点详解尚未生成
              </p>
              <p style={{ color: '#666', marginBottom: 30 }}>
                点击下方按钮，AI将为您生成详细的知识点讲解，包括：<br/>
                • 核心概念说明<br/>
                • 技术要点分析<br/>
                • 学习路径建议<br/>
                • 实践应用指导
              </p>
            </div>
          }
        >
          <GenerateContentButton
            pathId={pathId}
            contentType="knowledge"
            onGenerated={onContentGenerated}
          />
        </Empty>
      </div>
    );
  }

  return (
    <div>
      <Alert
        message="知识点详解"
        description="以下是AI为您生成的详细知识点讲解，建议结合思维导图和实际项目进行学习"
        type="info"
        showIcon
        style={{ marginBottom: 20 }}
      />
      
      <div
        style={{
          background: '#fafafa',
          padding: 24,
          borderRadius: 8,
          border: '1px solid #e8e8e8'
        }}
        className="markdown-content"
      >
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default KnowledgeTab;

