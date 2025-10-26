import React, { useState, useEffect } from 'react';
import { Layout, Menu, List, Button, Input, Tag, Space, Modal, message, Empty, Spin, Tabs } from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  FolderOutlined,
  SearchOutlined,
  SaveOutlined,
  EyeOutlined,
  BulbOutlined,
} from '@ant-design/icons';
import { notebookAPI } from '../services/notebookAPI';
import { noteAPI } from '../services/api';
import type { Notebook, Note, NoteCreate, NotebookCreate } from '../types/note';
import DualModeEditor from '../components/DualModeEditor';
import NoteMindMap from '../components/NoteMindMap';
import AINoteWizard from '../components/AINoteWizard';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const { Sider, Content } = Layout;
const { TextArea } = Input;

const NotesPage: React.FC = () => {
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedNotebook, setSelectedNotebook] = useState<number | null>(null);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  
  // 编辑状态
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [editTags, setEditTags] = useState<string[]>([]);
  const [editMode, setEditMode] = useState<'markdown' | 'rich_text'>('markdown');
  const [viewMode, setViewMode] = useState<'edit' | 'preview' | 'mindmap'>('edit');
  
  // 新建笔记本
  const [newNotebookModal, setNewNotebookModal] = useState(false);
  const [newNotebookName, setNewNotebookName] = useState('');
  const [newNotebookDesc, setNewNotebookDesc] = useState('');
  const [newNotebookIcon, setNewNotebookIcon] = useState('📓');
  
  // 搜索
  const [searchTerm, setSearchTerm] = useState('');
  
  // AI 生成笔记
  const [aiWizardVisible, setAiWizardVisible] = useState(false);

  // 加载笔记本列表
  useEffect(() => {
    loadNotebooks();
  }, []);

  // 加载笔记列表
  useEffect(() => {
    if (selectedNotebook) {
      loadNotes(selectedNotebook);
    }
  }, [selectedNotebook]);

  const loadNotebooks = async () => {
    try {
      const data = await notebookAPI.list();
      setNotebooks(data);
      if (data.length > 0 && !selectedNotebook) {
        setSelectedNotebook(data[0].id);
      }
    } catch (error: any) {
      message.error('加载笔记本失败');
    }
  };

  const loadNotes = async (notebookId: number) => {
    setLoading(true);
    try {
      const data = await noteAPI.list(0, 100);
      // 筛选属于当前笔记本的笔记
      const filtered = data.filter(note => note.notebook_id === notebookId);
      setNotes(filtered);
    } catch (error: any) {
      message.error('加载笔记失败');
    } finally {
      setLoading(false);
    }
  };

  const createNewNotebook = async () => {
    if (!newNotebookName.trim()) {
      message.warning('请输入笔记本名称');
      return;
    }

    try {
      const data: NotebookCreate = {
        name: newNotebookName,
        description: newNotebookDesc,
        icon: newNotebookIcon,
      };
      await notebookAPI.create(data);
      message.success('笔记本创建成功');
      setNewNotebookModal(false);
      setNewNotebookName('');
      setNewNotebookDesc('');
      setNewNotebookIcon('📓');
      loadNotebooks();
    } catch (error: any) {
      message.error('创建失败');
    }
  };

  const deleteNotebook = async (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个笔记本吗？笔记将移动到"日常笔记"。',
      okText: '确认',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          await notebookAPI.delete(id);
          message.success('删除成功');
          loadNotebooks();
          if (selectedNotebook === id) {
            setSelectedNotebook(null);
            setNotes([]);
          }
        } catch (error: any) {
          message.error(error.response?.data?.detail || '删除失败');
        }
      },
    });
  };

  const createNewNote = () => {
    setIsEditing(true);
    setSelectedNote(null);
    setEditTitle('');
    setEditContent('');
    setEditTags([]);
    setEditMode('markdown');
    setViewMode('edit');
  };

  const selectNote = (note: Note) => {
    // 如果点击的是已经选中的笔记，不改变状态
    if (selectedNote?.id === note.id) {
      return;
    }
    
    setSelectedNote(note);
    setEditTitle(note.title || '');
    setEditContent(note.content);
    setEditTags(note.tags || []);
    setEditMode(note.editor_mode);
    setIsEditing(false);
    setViewMode('preview');
  };

  const saveNote = async () => {
    if (!editContent.trim()) {
      message.warning('笔记内容不能为空');
      return;
    }

    setSaving(true);
    try {
      if (selectedNote) {
        // 更新笔记
        await noteAPI.update(selectedNote.id, {
          title: editTitle,
          content: editContent,
          tags: editTags,
          editor_mode: editMode,
        });
        message.success('保存成功');
      } else {
        // 创建笔记
        const data: NoteCreate = {
          notebook_id: selectedNotebook!,
          title: editTitle,
          content: editContent,
          tags: editTags,
          editor_mode: editMode,
        };
        await noteAPI.create(data);
        message.success('笔记创建成功');
      }
      setIsEditing(false);
      if (selectedNotebook) {
        loadNotes(selectedNotebook);
      }
      // 重新加载笔记本列表以更新笔记数量
      loadNotebooks();
    } catch (error: any) {
      message.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const deleteNote = async (noteId: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这篇笔记吗？删除后不可恢复。',
      okText: '确认',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          await noteAPI.delete(noteId);
          message.success('删除成功');
          if (selectedNote?.id === noteId) {
            setSelectedNote(null);
            setIsEditing(false);
          }
          if (selectedNotebook) {
            loadNotes(selectedNotebook);
          }
          // 重新加载笔记本列表以更新笔记数量
          loadNotebooks();
        } catch (error: any) {
          message.error('删除失败');
        }
      },
    });
  };

  const handleSaveAINote = async (note: {
    notebook_id: number;
    title: string;
    content: string;
    learning_path_id?: number;
  }) => {
    try {
      const data: NoteCreate = {
        notebook_id: note.notebook_id,
        title: note.title,
        content: note.content,
        tags: [],
        editor_mode: 'markdown',
        learning_path_id: note.learning_path_id,
      };
      const createdNote = await noteAPI.create(data);
      
      // 切换到目标笔记本
      setSelectedNotebook(note.notebook_id);
      
      // 重新加载笔记列表并选中新创建的笔记
      const allNotes = await noteAPI.list(0, 100);
      const filtered = allNotes.filter(n => n.notebook_id === note.notebook_id);
      setNotes(filtered);
      
      // 选中新创建的笔记
      selectNote(createdNote);
      
      // 重新加载笔记本列表以更新笔记数量
      loadNotebooks();
    } catch (error: any) {
      throw error;
    }
  };

  const filteredNotes = notes.filter(note =>
    note.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    note.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout style={{ height: 'calc(100vh - 112px)', background: '#fff' }}>
      {/* 左侧：笔记本列表 */}
      <Sider width={250} style={{ background: '#fafafa', borderRight: '1px solid #f0f0f0' }}>
        <div style={{ padding: '16px' }}>
          <Button
            type="primary"
            block
            icon={<PlusOutlined />}
            onClick={() => setNewNotebookModal(true)}
          >
            新建笔记本
          </Button>
        </div>
        <Menu
          mode="inline"
          selectedKeys={selectedNotebook ? [String(selectedNotebook)] : []}
          style={{ border: 'none', background: 'transparent' }}
        >
          {notebooks.map(notebook => (
            <Menu.Item
              key={notebook.id}
              icon={<span style={{ fontSize: 18 }}>{notebook.icon}</span>}
              onClick={() => setSelectedNotebook(notebook.id)}
            >
              <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                <span>{notebook.name}</span>
                <span style={{ fontSize: 12, color: '#999' }}>({notebook.note_count})</span>
              </Space>
              {!notebook.is_default && (
                <DeleteOutlined
                  style={{ fontSize: 12, marginLeft: 8, color: '#999' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteNotebook(notebook.id);
                  }}
                />
              )}
            </Menu.Item>
          ))}
        </Menu>
      </Sider>

      {/* 中间：笔记列表 */}
      <Sider width={300} style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}>
        <div style={{ padding: '16px' }}>
          <Input
            placeholder="搜索笔记..."
            prefix={<SearchOutlined />}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ marginBottom: 12 }}
          />
          <Space direction="vertical" style={{ width: '100%' }}>
            <Button
              type="dashed"
              block
              icon={<PlusOutlined />}
              onClick={createNewNote}
              disabled={!selectedNotebook}
            >
              新建笔记
            </Button>
            <Button
              type="primary"
              ghost
              block
              icon={<BulbOutlined />}
              onClick={() => setAiWizardVisible(true)}
            >
              AI 生成笔记
            </Button>
          </Space>
        </div>
        <Spin spinning={loading}>
          <List
            dataSource={filteredNotes}
            renderItem={(note) => (
              <List.Item
                key={note.id}
                onClick={() => selectNote(note)}
                style={{
                  cursor: 'pointer',
                  background: selectedNote?.id === note.id ? '#e6f7ff' : 'transparent',
                  padding: '12px 16px',
                }}
              >
                <List.Item.Meta
                  title={note.title || '无标题'}
                  description={
                    <div>
                      <div style={{ marginBottom: 4 }}>
                        {note.content.substring(0, 50)}...
                      </div>
                      <Space size={4}>
                        {note.tags.slice(0, 3).map(tag => (
                          <Tag key={tag} color="blue" style={{ fontSize: 11 }}>
                            {tag}
                          </Tag>
                        ))}
                      </Space>
                    </div>
                  }
                />
              </List.Item>
            )}
            locale={{ emptyText: selectedNotebook ? '暂无笔记' : '请选择笔记本' }}
          />
        </Spin>
      </Sider>

      {/* 右侧：笔记详情/编辑 */}
      <Content style={{ padding: '24px', overflow: 'auto' }}>
        {!selectedNote && !isEditing ? (
          <Empty
            description="选择或创建一篇笔记"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <div>
            {/* 标题 */}
            <Input
              placeholder="笔记标题"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              disabled={viewMode !== 'edit'}
              style={{ fontSize: 20, fontWeight: 'bold', marginBottom: 16, border: 'none', borderBottom: '1px solid #f0f0f0' }}
            />

            {/* 操作按钮 */}
            <Space style={{ marginBottom: 16 }}>
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={saveNote}
                loading={saving}
                disabled={!selectedNote && !isEditing}
              >
                保存
              </Button>
              {selectedNote && (
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => deleteNote(selectedNote.id)}
                >
                  删除
                </Button>
              )}
            </Space>

            {/* 视图切换 */}
            <Tabs
              activeKey={viewMode}
              onChange={(key) => {
                setViewMode(key as any);
                // 切换到编辑模式时，自动进入编辑状态
                if (key === 'edit') {
                  setIsEditing(true);
                }
              }}
              style={{ marginBottom: 16 }}
              items={[
                {
                  key: 'edit',
                  label: '编辑',
                },
                {
                  key: 'preview',
                  label: '预览',
                },
                {
                  key: 'mindmap',
                  label: '思维导图',
                },
              ]}
            />

            {/* 内容区 */}
            {viewMode === 'edit' ? (
              <DualModeEditor
                value={editContent}
                onChange={setEditContent}
                mode={editMode}
                onModeChange={setEditMode}
                height={500}
              />
            ) : viewMode === 'preview' ? (
              <div
                style={{
                  border: '1px solid #d9d9d9',
                  borderRadius: '4px',
                  padding: '16px',
                  minHeight: '500px',
                  background: '#fafafa',
                }}
              >
                {editMode === 'markdown' ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {editContent}
                  </ReactMarkdown>
                ) : (
                  <div dangerouslySetInnerHTML={{ __html: editContent }} />
                )}
              </div>
            ) : (
              <NoteMindMap 
                key={`mindmap-${selectedNote?.id || 'new'}-${editContent.length}`}
                content={editContent} 
                editorMode={editMode} 
              />
            )}

            {/* 标签 */}
            <div style={{ marginTop: 16 }}>
              <Input
                placeholder="添加标签（逗号分隔）"
                value={editTags.join(', ')}
                onChange={(e) => setEditTags(e.target.value.split(',').map(t => t.trim()).filter(Boolean))}
                disabled={viewMode !== 'edit'}
              />
            </div>
          </div>
        )}
      </Content>

      {/* 新建笔记本弹窗 */}
      <Modal
        title="新建笔记本"
        open={newNotebookModal}
        onOk={createNewNotebook}
        onCancel={() => setNewNotebookModal(false)}
        okText="创建"
        cancelText="取消"
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <label>图标：</label>
            <Input
              value={newNotebookIcon}
              onChange={(e) => setNewNotebookIcon(e.target.value)}
              placeholder="📓"
              maxLength={2}
            />
          </div>
          <div>
            <label>名称：</label>
            <Input
              value={newNotebookName}
              onChange={(e) => setNewNotebookName(e.target.value)}
              placeholder="笔记本名称"
            />
          </div>
          <div>
            <label>描述：</label>
            <TextArea
              value={newNotebookDesc}
              onChange={(e) => setNewNotebookDesc(e.target.value)}
              placeholder="笔记本描述"
              rows={3}
            />
          </div>
        </Space>
      </Modal>
      
      {/* AI 生成笔记向导 */}
      <AINoteWizard
        visible={aiWizardVisible}
        onClose={() => setAiWizardVisible(false)}
        onSave={handleSaveAINote}
        notebooks={notebooks}
      />
    </Layout>
  );
};

export default NotesPage;

