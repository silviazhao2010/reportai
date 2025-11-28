import React, { useState, useMemo } from 'react';
import { Table, Alert, Empty, Card, Typography, Radio } from 'antd';
import { BarChartOutlined, BulbOutlined, TableOutlined, PieChartOutlined } from '@ant-design/icons';
import { Column, Pie } from '@ant-design/charts';

const { Paragraph } = Typography;

function ReportDisplay({ result, compact = false }) {
  const [viewType, setViewType] = useState('table'); // 'table' | 'bar' | 'pie'

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

  // 分析数据，判断是否适合图表展示
  const chartData = useMemo(() => {
    if (!result.data || result.data.length === 0) {
      return null;
    }

    // 查找数值列和分类列
    const numericColumns = [];
    const categoryColumns = [];

    result.columns.forEach((col) => {
      const sampleValues = result.data.slice(0, 10).map((row) => row[col]);
      const hasNumbers = sampleValues.some((val) => typeof val === 'number' && !isNaN(val));
      const hasStrings = sampleValues.some((val) => typeof val === 'string' || typeof val === 'number');

      if (hasNumbers) {
        numericColumns.push(col);
      }
      if (hasStrings && !hasNumbers) {
        categoryColumns.push(col);
      }
    });

    // 如果只有两列，且一列是分类，一列是数值，适合图表
    if (result.columns.length === 2) {
      const col1 = result.columns[0];
      const col2 = result.columns[1];
      const isCol1Numeric = numericColumns.includes(col1);
      const isCol2Numeric = numericColumns.includes(col2);

      if (isCol1Numeric && !isCol2Numeric) {
        return {
          categoryField: col2,
          valueField: col1,
          data: result.data.map((row) => ({
            category: String(row[col2]),
            value: Number(row[col1]) || 0,
          })),
        };
      }
      if (!isCol1Numeric && isCol2Numeric) {
        return {
          categoryField: col1,
          valueField: col2,
          data: result.data.map((row) => ({
            category: String(row[col1]),
            value: Number(row[col2]) || 0,
          })),
        };
      }
    }

    // 如果有多列，尝试使用第一列作为分类，第一个数值列作为值
    if (result.columns.length > 2 && numericColumns.length > 0) {
      const categoryCol = categoryColumns[0] || result.columns[0];
      const valueCol = numericColumns[0];

      return {
        categoryField: categoryCol,
        valueField: valueCol,
        data: result.data.map((row) => ({
          category: String(row[categoryCol]),
          value: Number(row[valueCol]) || 0,
        })),
      };
    }

    return null;
  }, [result.data, result.columns]);

  // 渲染图表
  const renderChart = () => {
    if (!chartData) {
      return (
        <Alert
          message="数据格式不支持图表展示"
          description="图表需要至少一个分类字段和一个数值字段"
          type="info"
          style={{ marginTop: '12px' }}
        />
      );
    }

    if (viewType === 'bar') {
      return (
        <div style={{ marginTop: '12px', height: '400px' }}>
          <Column
            data={chartData.data}
            xField="category"
            yField="value"
            columnWidthRatio={0.6}
            label={{
              position: 'top',
              style: {
                fill: '#666',
                fontSize: 12,
              },
            }}
            color="#1890ff"
            meta={{
              category: {
                alias: chartData.categoryField,
              },
              value: {
                alias: chartData.valueField,
              },
            }}
          />
        </div>
      );
    }

    if (viewType === 'pie') {
      return (
        <div style={{ marginTop: '12px', height: '400px' }}>
          <Pie
            data={chartData.data}
            angleField="value"
            colorField="category"
            radius={0.8}
            label={{
              type: 'outer',
              content: '{name}: {value}',
            }}
            interactions={[{ type: 'element-active' }]}
            meta={{
              category: {
                alias: chartData.categoryField,
              },
              value: {
                alias: chartData.valueField,
              },
            }}
          />
        </div>
      );
    }

    return null;
  };

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
      
      {/* 查询结果标题和视图切换 */}
      <div style={{ 
        marginBottom: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '12px',
        flexWrap: 'wrap',
      }}>
        <div style={{
          color: '#666',
          fontSize: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
        }}>
          <BarChartOutlined /> 查询结果
          <span style={{ fontSize: '12px', marginLeft: '8px' }}>
            共 {result.data.length} 条记录
          </span>
        </div>
        <Radio.Group
          value={viewType}
          onChange={(e) => setViewType(e.target.value)}
          size="small"
        >
          <Radio.Button value="table">
            <TableOutlined /> 表格
          </Radio.Button>
          <Radio.Button value="bar" disabled={!chartData}>
            <BarChartOutlined /> 柱状图
          </Radio.Button>
          <Radio.Button value="pie" disabled={!chartData}>
            <PieChartOutlined /> 饼图
          </Radio.Button>
        </Radio.Group>
      </div>

      {/* 根据视图类型渲染内容 */}
      {viewType === 'table' && (
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
      )}

      {(viewType === 'bar' || viewType === 'pie') && renderChart()}
    </div>
  );
}

export default ReportDisplay;

