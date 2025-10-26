import React from 'react';
import MDEditor from '@uiw/react-md-editor';

interface MarkdownEditorProps {
  value: string;
  onChange: (value?: string) => void;
  height?: number;
}

const MarkdownEditor: React.FC<MarkdownEditorProps> = ({ value, onChange, height = 400 }) => {
  return (
    <div data-color-mode="light">
      <MDEditor
        value={value}
        onChange={onChange}
        height={height}
        preview="edit"
        hideToolbar={false}
        enableScroll={true}
        visibleDragbar={true}
      />
    </div>
  );
};

export default MarkdownEditor;

