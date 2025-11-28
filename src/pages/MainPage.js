import React, { useState } from 'react';
import { Layout, Typography, Button } from 'antd';
import { FileTextOutlined } from '@ant-design/icons';
import { useHistory } from 'react-router-dom';
import QueryInput from '../components/QueryInput';
import ChatList from '../components/ChatList';

const { Header, Content } = Layout;
const { Title } = Typography;

function MainPage() {
  const history = useHistory();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleQuery = async (queryText) => {
    // 添加用户消息和AI回复占位符
    const userMessage = {
      isUser: true,
      content: queryText,
    };
    
    const loadingMessage = {
      isUser: false,
      content: '正在处理您的查询...',
      sql: '',
      result: null,
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: queryText,
          showSql: true,
        },),
      });

      const result = await response.json();

      // 更新AI消息（替换loading消息）
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        if (lastIndex >= 0 && !newMessages[lastIndex].isUser) {
          newMessages[lastIndex] = {
            isUser: false,
            content: result.success ? '' : '查询失败',
            sql: result.sql || '',
            result: result.success
              ? result
              : {
                  success: false,
                  message: result.message,
                  data: [],
                  columns: [],
                },
          };
        }
        return newMessages;
      });
    } catch (error) {
      // 更新AI消息为错误状态
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        if (lastIndex >= 0 && !newMessages[lastIndex].isUser) {
          newMessages[lastIndex] = {
            isUser: false,
            content: '请求失败',
            sql: '',
            result: {
              success: false,
              message: `请求失败: ${error.message}`,
              data: [],
              columns: [],
            },
          };
        }
        return newMessages;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header style={{ background: '#001529', padding: '0 24px', flexShrink: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={3} style={{ color: '#fff', margin: '16px 0' }}>
          AI报表生成系统
        </Title>
        <Button
          type="primary"
          icon={<FileTextOutlined />}
          onClick={() => history.push('/reports')}
        >
          报表设计器
        </Button>
      </Header>
      <Content style={{ 
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        background: '#f0f2f5',
        overflow: 'hidden',
      }}>
        <div style={{
          flex: 1,
          overflow: 'hidden',
          background: '#fff',
          margin: '24px',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}>
          <ChatList messages={messages} />
        </div>
        <div style={{ 
          flexShrink: 0,
          padding: '0 24px 24px',
        }}>
          <QueryInput onQuery={handleQuery} loading={loading} />
        </div>
      </Content>
    </Layout>
  );
}

export default MainPage;

