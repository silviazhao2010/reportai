import React from 'react';
import { Typography } from 'antd';
import { CodeOutlined } from '@ant-design/icons';

const { Text } = Typography;

function SQLPreview({ sql, compact = false }) {
  if (!sql) {
    return null;
  }

  if (compact) {
    return (
      <div style={{ marginTop: '8px' }}>
        <div style={{ 
          marginBottom: '8px',
          color: '#666',
          fontSize: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
        }}>
          <CodeOutlined /> SQL预览
        </div>
        <pre
          style={{
            background: '#f5f5f5',
            padding: '8px 12px',
            borderRadius: '4px',
            margin: 0,
            overflow: 'auto',
            fontSize: '12px',
            lineHeight: '1.5',
            maxHeight: '200px',
          }}
        >
          <code>{sql}</code>
        </pre>
      </div>
    );
  }

  return (
    <div style={{ marginTop: '8px' }}>
      <div style={{ 
        marginBottom: '8px',
        color: '#666',
        fontSize: '12px',
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
      }}>
        <CodeOutlined /> SQL预览
      </div>
      <pre
        style={{
          background: '#f5f5f5',
          padding: '12px',
          borderRadius: '4px',
          margin: 0,
          overflow: 'auto',
          fontSize: '14px',
          lineHeight: '1.6',
        }}
      >
        <code>{sql}</code>
      </pre>
    </div>
  );
}

export default SQLPreview;

