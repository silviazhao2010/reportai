import React, { useRef, useEffect } from 'react';
import { Empty } from 'antd';
import ChatMessage from './ChatMessage';

function ChatList({ messages }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%',
        color: '#999',
      }}>
        <Empty description="开始对话，输入您的查询需求" />
      </div>
    );
  }

  return (
    <div style={{
      padding: '24px',
      height: '100%',
      overflowY: 'auto',
      background: '#fafafa',
    }}>
      {messages.map((message, index) => (
        <ChatMessage
          key={index}
          message={message}
          isUser={message.isUser}
        />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default ChatList;

