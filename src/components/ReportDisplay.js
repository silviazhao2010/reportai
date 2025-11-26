import React from 'react';
import { Table, Alert, Empty, Card, Typography } from 'antd';
import { BarChartOutlined, BulbOutlined } from '@ant-design/icons';

const { Paragraph } = Typography;

function ReportDisplay({ result, compact = false }) {
  if (!result) {
    return null;
  }

  if (!result.success) {
    return (
      <div style={{ marginTop: '8px' }}>
        <Alert
          message="查询失败"
          description={result.message || '未知错误'}
          type="error"
          showIcon
        />
      </div>
    );
  }

  if (!result.data || result.data.length === 0) {
    return (
      <div style={{ marginTop: '8px' }}>
        <Empty description="查询结果为空" />
      </div>
    );
  }

  // 构建表格列
  const columns = result.columns.map((col) => ({
    title: col,
    dataIndex: col,
    key: col,
    sorter: (a, b) => {
      const aVal = a[col];
      const bVal = b[col];
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return aVal - bVal;
      }
      return String(aVal).localeCompare(String(bVal));
    },
  }));

  return (
    <div style={{ marginTop: '8px' }}>
      {/* 结果解读 */}
      {result.interpretation && (
        <Card
          size="small"
          style={{
            marginBottom: '12px',
            background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
            border: 'none',
          }}
          bodyStyle={{ padding: '12px 16px' }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '8px',
          }}>
            <BulbOutlined style={{
              color: '#1890ff',
              fontSize: '16px',
              marginTop: '2px',
              flexShrink: 0,
            }} />
            <div style={{ flex: 1 }}>
              <div style={{
                fontSize: '13px',
                fontWeight: 500,
                color: '#1890ff',
                marginBottom: '6px',
              }}>
                数据解读
              </div>
              <Paragraph
                style={{
                  margin: 0,
                  fontSize: '13px',
                  color: '#333',
                  lineHeight: '1.6',
                  whiteSpace: 'pre-wrap',
                }}
              >
                {result.interpretation}
              </Paragraph>
            </div>
          </div>
        </Card>
      )}
      
      {/* 查询结果表格 */}
      <div style={{ 
        marginBottom: '8px',
        color: '#666',
        fontSize: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '4px',
      }}>
        <span>
          <BarChartOutlined /> 查询结果
        </span>
        <span style={{ fontSize: '12px' }}>
          共 {result.data.length} 条记录
        </span>
      </div>
      <Table
        dataSource={result.data.map((row, index) => ({
          ...row,
          key: index,
        }))}
        columns={columns}
        pagination={{
          pageSize: compact ? 5 : 10,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          size: compact ? 'small' : 'default',
        }}
        scroll={{ x: 'max-content' }}
        size={compact ? 'small' : 'default'}
      />
    </div>
  );
}

export default ReportDisplay;

