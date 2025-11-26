import React from 'react';
import { Table, Alert, Empty } from 'antd';
import { BarChartOutlined } from '@ant-design/icons';

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

