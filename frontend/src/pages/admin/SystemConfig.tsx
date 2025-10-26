import React, { useState, useEffect } from 'react';
import { Card, Tabs, Form, Input, Button, message, Space, Typography } from 'antd';
import { SaveOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { configAPI, ConfigItem } from '../../services/adminAPI';

const { TabPane } = Tabs;
const { Paragraph } = Typography;

const SystemConfig: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [configs, setConfigs] = useState<ConfigItem[]>([]);
  const [apiForm] = Form.useForm();
  const [n8nForm] = Form.useForm();
  const [systemForm] = Form.useForm();

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      setLoading(true);
      const data = await configAPI.list();
      setConfigs(data);
      
      // 填充表单
      data.forEach(config => {
        let value = config.value;
        try {
          // 尝试解析JSON
          value = JSON.parse(value);
        } catch (e) {
          // 如果不是JSON，保持原值
        }
        
        if (config.category === 'api_keys') {
          apiForm.setFieldValue(config.key, value);
        } else if (config.category === 'n8n') {
          n8nForm.setFieldValue(config.key, value);
        } else if (config.category === 'system') {
          systemForm.setFieldValue(config.key, value);
        }
      });
    } catch (error) {
      message.error('加载配置失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (category: string, form: any) => {
    try {
      const values = await form.validateFields();
      
      for (const key in values) {
        const value = values[key];
        // 将值转换为JSON字符串存储
        await configAPI.update(key, JSON.stringify(value));
      }
      
      message.success('配置保存成功');
      loadConfigs();
    } catch (error) {
      message.error('配置保存失败');
      console.error(error);
    }
  };

  const handleTestConnection = async (service: 'openai' | 'n8n') => {
    try {
      const result = await configAPI.testConnection(service);
      if (result.success) {
        message.success(result.message);
      } else {
        message.error(result.message);
      }
    } catch (error) {
      message.error('连接测试失败');
      console.error(error);
    }
  };

  return (
    <div>
      <h2>系统配置</h2>
      <Card>
        <Tabs defaultActiveKey="api">
          <TabPane tab="API配置" key="api">
            <Form form={apiForm} layout="vertical">
              <Form.Item
                label="OpenAI API密钥"
                name="openai_api_key"
                extra="用于AI功能的OpenAI API密钥"
              >
                <Input.Password placeholder="请输入OpenAI API密钥" />
              </Form.Item>
              <Form.Item
                label="OpenAI API基础URL"
                name="openai_api_base"
                extra="OpenAI API的基础URL，默认使用中转API"
              >
                <Input placeholder="https://api.qingyuntop.top/v1" />
              </Form.Item>
              <Space>
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  onClick={() => handleSave('api_keys', apiForm)}
                >
                  保存配置
                </Button>
                <Button
                  icon={<CheckCircleOutlined />}
                  onClick={() => handleTestConnection('openai')}
                >
                  测试连接
                </Button>
              </Space>
            </Form>
          </TabPane>

          <TabPane tab="n8n配置" key="n8n">
            <Form form={n8nForm} layout="vertical">
              <Form.Item
                label="n8n Webhook URL"
                name="n8n_webhook_url"
                extra="n8n工作流的Webhook URL"
              >
                <Input placeholder="请输入n8n Webhook URL" />
              </Form.Item>
              <Form.Item
                label="n8n API密钥"
                name="n8n_api_key"
                extra="n8n的API访问密钥"
              >
                <Input.Password placeholder="请输入n8n API密钥" />
              </Form.Item>
              <Space>
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  onClick={() => handleSave('n8n', n8nForm)}
                >
                  保存配置
                </Button>
                <Button
                  icon={<CheckCircleOutlined />}
                  onClick={() => handleTestConnection('n8n')}
                >
                  测试连接
                </Button>
              </Space>
            </Form>
          </TabPane>

          <TabPane tab="系统参数" key="system">
            <Form form={systemForm} layout="vertical">
              <Form.Item
                label="系统名称"
                name="system_name"
                extra="显示在页面标题和其他位置的系统名称"
              >
                <Input placeholder="职途伴侣" />
              </Form.Item>
              <Form.Item
                label="每个用户最大学习路线数"
                name="max_learning_paths_per_user"
                extra="限制每个用户可创建的学习路线数量"
              >
                <Input type="number" placeholder="10" />
              </Form.Item>
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={() => handleSave('system', systemForm)}
              >
                保存配置
              </Button>
            </Form>
          </TabPane>
        </Tabs>
      </Card>

      <Card title="配置说明" style={{ marginTop: 16 }}>
        <Paragraph>
          <ul>
            <li><strong>API配置：</strong>配置OpenAI API相关参数，用于AI功能（学习路线生成、AI助手等）</li>
            <li><strong>n8n配置：</strong>配置n8n工作流相关参数，用于自动化任务和AI代理</li>
            <li><strong>系统参数：</strong>配置系统基本参数和限制</li>
          </ul>
        </Paragraph>
        <Paragraph type="warning">
          注意：修改配置后可能需要重启服务才能生效。敏感信息（如API密钥）以加密方式存储。
        </Paragraph>
      </Card>
    </div>
  );
};

export default SystemConfig;

