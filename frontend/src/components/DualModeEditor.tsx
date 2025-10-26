import React, { useState } from 'react';
import { Button, Space, Modal, message } from 'antd';
import { FileMarkdownOutlined, FormOutlined } from '@ant-design/icons';
import MarkdownEditor from './MarkdownEditor';
import RichTextEditor from './RichTextEditor';

interface DualModeEditorProps {
  value: string;
  onChange: (value: string) => void;
  mode: 'markdown' | 'rich_text';
  onModeChange: (mode: 'markdown' | 'rich_text') => void;
  height?: number;
}

const DualModeEditor: React.FC<DualModeEditorProps> = ({
  value,
  onChange,
  mode,
  onModeChange,
  height = 400
}) => {
  const [switchModalVisible, setSwitchModalVisible] = useState(false);
  const [targetMode, setTargetMode] = useState<'markdown' | 'rich_text'>(mode);

  const handleModeSwitch = (newMode: 'markdown' | 'rich_text') => {
    if (newMode === mode) return;
    
    setTargetMode(newMode);
    setSwitchModalVisible(true);
  };

  const confirmModeSwitch = () => {
    onModeChange(targetMode);
    setSwitchModalVisible(false);
    message.warning(`已切换到${targetMode === 'markdown' ? 'Markdown' : '富文本'}模式，内容格式可能已改变`);
  };

  return (
    <div>
      <Space style={{ marginBottom: 12 }}>
        <Button
          type={mode === 'markdown' ? 'primary' : 'default'}
          icon={<FileMarkdownOutlined />}
          onClick={() => handleModeSwitch('markdown')}
        >
          Markdown
        </Button>
        <Button
          type={mode === 'rich_text' ? 'primary' : 'default'}
          icon={<FormOutlined />}
          onClick={() => handleModeSwitch('rich_text')}
        >
          富文本
        </Button>
      </Space>

      {mode === 'markdown' ? (
        <MarkdownEditor
          value={value}
          onChange={(val) => onChange(val || '')}
          height={height}
        />
      ) : (
        <RichTextEditor
          value={value}
          onChange={onChange}
          height={height}
        />
      )}

      <Modal
        title="⚠️ 切换编辑模式警告"
        open={switchModalVisible}
        onOk={confirmModeSwitch}
        onCancel={() => setSwitchModalVisible(false)}
        okText="确认切换"
        cancelText="取消"
        okType="danger"
      >
        <div style={{ color: '#ff4d4f' }}>
          <p><strong>注意：切换编辑模式会导致内容格式发生不可逆的变化！</strong></p>
          <ul>
            <li>从 Markdown 切换到富文本：Markdown 语法将被转换为 HTML</li>
            <li>从富文本切换到 Markdown：HTML 标签将保留，无法自动转换为 Markdown</li>
            <li>切换后，思维导图和预览可能无法正常显示</li>
          </ul>
        </div>
        <p style={{ marginTop: 16 }}>确定要从 <strong>{mode === 'markdown' ? 'Markdown' : '富文本'}</strong> 切换到 <strong>{targetMode === 'markdown' ? 'Markdown' : '富文本'}</strong> 模式吗？</p>
        <p style={{ color: '#8c8c8c', fontSize: 12 }}>建议：创建笔记时选择一种模式后不要切换</p>
      </Modal>
    </div>
  );
};

export default DualModeEditor;

