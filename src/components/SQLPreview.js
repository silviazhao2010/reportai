import React from 'react';
import { Card, Typography } from 'antd';
import { CodeOutlined } from '@ant-design/icons';

const { Text } = Typography;

function SQLPreview({ sql }) {
  if (!sql) {
    return null;
  }

  return (
    <Card
      title={
        <span>
          <CodeOutlined /> SQL预览
        </span>
      }
      style={{ marginBottom: '24px' }}
    >
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
    </Card>
  );
}

export default SQLPreview;

