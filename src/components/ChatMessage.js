import React from 'react';
import { Avatar, Typography, Spin } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import ReportDisplay from './ReportDisplay';
import SQLPreview from './SQLPreview';

const { Text } = Typography;

function ChatMessage({ message, isUser }) {
  const renderContent = () => {
    if (isUser) {
      return (
        <div style={{ 
          padding: '12px 16px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '12px 12px 4px 12px',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}>
          <Text style={{ color: '#fff' }}>{message.content}</Text>
        </div>
      );
    } else {
      // AI回复内容
      const { content, sql, result } = message;
      const isLoading = content === '正在处理您的查询...' && !sql && !result;
      
      return (
        <div style={{ 
          padding: '12px 16px',
          background: '#fff',
          borderRadius: '12px 12px 12px 4px',
          border: '1px solid #e8e8e8',
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        }}>
          {isLoading ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Spin size="small" />
              <Text type="secondary">{content}</Text>
            </div>
          ) : (
            <>
              {content && content !== '查询完成' && (
                <div style={{ marginBottom: sql || result ? '12px' : '0' }}>
                  <Text>{content}</Text>
                </div>
              )}
              {sql && (
                <div style={{ marginBottom: result ? '12px' : '0' }}>
                  <SQLPreview sql={sql} compact={true} />
                </div>
              )}
              {result && (
                <div>
                  <ReportDisplay result={result} compact={true} />
                </div>
              )}
            </>
          )}
        </div>
      );
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: isUser ? 'row-reverse' : 'row',
      marginBottom: '20px',
      alignItems: 'flex-start',
      animation: 'fadeIn 0.3s ease-in',
    }}>
      <Avatar
        style={{
          backgroundColor: isUser ? '#1890ff' : '#52c41a',
          marginLeft: isUser ? '12px' : '0',
          marginRight: isUser ? '0' : '12px',
          flexShrink: 0,
        }}
        size="large"
        icon={isUser ? <UserOutlined /> : <RobotOutlined />}
      />
      <div style={{ 
        flex: 1,
        maxWidth: '75%',
        minWidth: 0,
      }}>
        {renderContent()}
      </div>
    </div>
  );
}

export default ChatMessage;

