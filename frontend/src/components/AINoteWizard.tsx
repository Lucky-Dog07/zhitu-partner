import React, { useState, useEffect } from 'react';
import {
  Modal,
  Steps,
  Form,
  Select,
  Checkbox,
  Input,
  Button,
  Spin,
  Alert,
  Tabs,
  message,
  Space
} from 'antd';
import { BulbOutlined, SaveOutlined, EditOutlined, EyeOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { aiNoteAPI, type NoteGenerationRequest, type NoteDraft } from '../services/aiNoteAPI';
import { learningPathAPI, type LearningPath } from '../services/api';
import MarkdownEditor from './MarkdownEditor';

const { Step } = Steps;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

interface AINoteWizardProps {
  visible: boolean;
  onClose: () => void;
  onSave: (note: {
    notebook_id: number;
    title: string;
    content: string;
    learning_path_id?: number;
  }) => Promise<void>;
  notebooks: Array<{ id: number; name: string; icon?: string }>;
}

const AINoteWizard: React.FC<AINoteWizardProps> = ({
  visible,
  onClose,
  onSave,
  notebooks
}) => {
  const [step, setStep] = useState(1); // 1: 选择, 2: 生成中, 3: 预览编辑
  const [form] = Form.useForm();
  const [draft, setDraft] = useState<NoteDraft | null>(null);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [selectedNotebook, setSelectedNotebook] = useState<number | undefined>();
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);

  // 加载用户的学习路线
  useEffect(() => {
    if (visible) {
      loadLearningPaths();
    }
  }, [visible]);

  const loadLearningPaths = async () => {
    try {
      const result = await learningPathAPI.list(0, 50);
      setLearningPaths(result.items);
    } catch (error) {
      console.error('加载学习路线失败:', error);
    }
  };

  const handleGenerate = async () => {
    try {
      const values = await form.validateFields();
      setGenerating(true);
      setStep(2);

      const request: NoteGenerationRequest = {
        source_type: values.source_type,
        source_id: values.learning_path_id,
        options: {
          include_weak_points: values.content_options?.includes('weak_points') ?? true,
          include_study_plan: values.content_options?.includes('study_plan') ?? true,
          include_interview_tips: values.content_options?.includes('interview_tips') ?? true,
          custom_requirements: values.custom_requirements || undefined
        }
      };

      const result = await aiNoteAPI.generateDraft(request);
      setDraft(result);
      
      // 自动选择建议的笔记本
      const suggestedNotebook = notebooks.find(
        nb => nb.name === result.suggested_notebook
      );
      if (suggestedNotebook) {
        setSelectedNotebook(suggestedNotebook.id);
      }

      setStep(3);
      message.success('笔记生成成功！');
    } catch (error: any) {
      message.error('生成失败：' + (error.response?.data?.detail || error.message || '未知错误'));
      setStep(1);
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!draft || !selectedNotebook) {
      message.error('请选择保存到哪个笔记本');
      return;
    }

    try {
      setSaving(true);
      await onSave({
        notebook_id: selectedNotebook,
        title: draft.title,
        content: draft.content,
        learning_path_id: draft.metadata.learning_path_id
      });
      message.success('笔记保存成功！');
      handleClose();
    } catch (error: any) {
      message.error('保存失败：' + (error.response?.data?.detail || error.message || '未知错误'));
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    setStep(1);
    setDraft(null);
    setSelectedNotebook(undefined);
    form.resetFields();
    onClose();
  };

  // Step 1: 选择数据源和选项
  const SelectionStep = () => (
    <Form
      form={form}
      layout="vertical"
      initialValues={{
        content_options: ['weak_points', 'study_plan', 'interview_tips']
      }}
    >
      <Form.Item
        name="source_type"
        label="数据源"
        rules={[{ required: true, message: '请选择数据源' }]}
      >
        <Select
          placeholder="选择生成笔记的数据来源"
          size="large"
        >
          <Option value="mistakes">我的错题</Option>
          <Option value="interview">面试题库</Option>
          <Option value="learning_path">学习路径</Option>
        </Select>
      </Form.Item>

      <Form.Item
        name="learning_path_id"
        label="选择学习路线"
        rules={[{ required: true, message: '请选择学习路线' }]}
      >
        <Select
          placeholder="选择一个学习路线"
          size="large"
          showSearch
          optionFilterProp="children"
        >
          {learningPaths.map(path => (
            <Option key={path.id} value={path.id}>
              {path.position}
            </Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item
        name="content_options"
        label="生成内容"
      >
        <Checkbox.Group style={{ width: '100%' }}>
          <Space direction="vertical">
            <Checkbox value="weak_points">薄弱知识点分析</Checkbox>
            <Checkbox value="study_plan">个性化学习计划</Checkbox>
            <Checkbox value="interview_tips">面试技巧与策略</Checkbox>
          </Space>
        </Checkbox.Group>
      </Form.Item>

      <Form.Item
        name="custom_requirements"
        label="特殊要求（可选）"
      >
        <TextArea
          rows={3}
          placeholder="例如：重点分析算法题、关注前端框架、强化数据结构..."
        />
      </Form.Item>

      <Form.Item>
        <Button
          type="primary"
          icon={<BulbOutlined />}
          onClick={handleGenerate}
          size="large"
          block
        >
          开始生成
        </Button>
      </Form.Item>
    </Form>
  );

  // Step 2: 生成中
  const GeneratingStep = () => (
    <div style={{ textAlign: 'center', padding: '60px 40px' }}>
      <Spin size="large" />
      <p style={{ marginTop: 24, fontSize: 16, color: '#666' }}>
        AI 正在根据您的职业和数据生成个性化笔记...
      </p>
      <p style={{ fontSize: 14, color: '#999' }}>
        这可能需要 10-30 秒，请稍候
      </p>
    </div>
  );

  // Step 3: 预览和编辑
  const PreviewStep = () => (
    <div>
      <Alert
        message="AI 生成完成"
        description={
          <div>
            <div>职业：{draft?.metadata.position}</div>
            <div>数据来源：{draft?.metadata.source === 'mistakes' ? '错题' : draft?.metadata.source === 'interview' ? '面试题' : '学习路径'}</div>
            <div>建议保存到：{draft?.suggested_notebook}</div>
          </div>
        }
        type="success"
        style={{ marginBottom: 16 }}
        showIcon
      />

      <Input
        value={draft?.title}
        onChange={(e) => setDraft(draft ? { ...draft, title: e.target.value } : null)}
        placeholder="笔记标题"
        size="large"
        style={{ marginBottom: 16 }}
        prefix={<EditOutlined />}
      />

      <Tabs defaultActiveKey="preview">
        <TabPane
          tab={
            <span>
              <EyeOutlined />
              预览
            </span>
          }
          key="preview"
        >
          <div
            style={{
              maxHeight: 400,
              overflowY: 'auto',
              padding: 16,
              border: '1px solid #f0f0f0',
              borderRadius: 4,
              backgroundColor: '#fafafa'
            }}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {draft?.content || ''}
            </ReactMarkdown>
          </div>
        </TabPane>
        <TabPane
          tab={
            <span>
              <EditOutlined />
              编辑
            </span>
          }
          key="edit"
        >
          <div style={{ maxHeight: 400, overflowY: 'auto' }}>
            <MarkdownEditor
              value={draft?.content || ''}
              onChange={(val) => setDraft(draft ? { ...draft, content: val || '' } : null)}
            />
          </div>
        </TabPane>
      </Tabs>

      <div style={{ marginTop: 24 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Select
            placeholder="选择保存到哪个笔记本"
            style={{ width: 250 }}
            value={selectedNotebook}
            onChange={setSelectedNotebook}
            size="large"
          >
            {notebooks.map(nb => (
              <Option key={nb.id} value={nb.id}>
                {nb.icon} {nb.name}
              </Option>
            ))}
          </Select>

          <Space>
            <Button onClick={() => setStep(1)}>
              重新生成
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={saving}
              size="large"
            >
              保存笔记
            </Button>
          </Space>
        </Space>
      </div>
    </div>
  );

  return (
    <Modal
      title="AI 生成笔记"
      open={visible}
      onCancel={handleClose}
      width={900}
      footer={null}
      destroyOnClose
    >
      <Steps current={step - 1} style={{ marginBottom: 32 }}>
        <Step title="选择" description="数据源和选项" />
        <Step title="生成" description="AI 生成笔记" />
        <Step title="保存" description="预览和保存" />
      </Steps>

      {step === 1 && <SelectionStep />}
      {step === 2 && <GeneratingStep />}
      {step === 3 && <PreviewStep />}
    </Modal>
  );
};

export default AINoteWizard;

