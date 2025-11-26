import React from 'react';
import { Card, Table, Alert, Empty } from 'antd';
import { BarChartOutlined } from '@ant-design/icons';

function ReportDisplay({ result }) {
  if (!result) {
    return null;
  }

  if (!result.success) {
    return (
      <Card>
        <Alert
          message="查询失败"
          description={result.message || '未知错误'}
          type="error"
          showIcon
        />
      </Card>
    );
  }

  if (!result.data || result.data.length === 0) {
    return (
      <Card>
        <Empty description="查询结果为空" />
      </Card>
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
  },));

  return (
    <Card
      title={
        <span>
          <BarChartOutlined /> 报表展示
        </span>
      }
      extra={
        <span style={{ color: '#666', fontSize: '14px' }}>
          共 {result.data.length} 条记录
        </span>
      }
    >
      <Table
        dataSource={result.data.map((row, index) => ({
          ...row,
          key: index,
        },))}
        columns={columns}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
        },}
        scroll={{ x: 'max-content' }}
      />
    </Card>
  );
}

export default ReportDisplay;

