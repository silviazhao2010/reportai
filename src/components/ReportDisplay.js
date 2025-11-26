import React, { useState, useMemo } from 'react';
import { Table, Alert, Empty, Card, Typography, Radio } from 'antd';
import { BarChartOutlined, BulbOutlined, PieChartOutlined, LineChartOutlined, TableOutlined } from '@ant-design/icons';
import { Pie, Line } from '@ant-design/charts';

const { Paragraph } = Typography;

function ReportDisplay({ result, compact = false }) {
  const [viewType, setViewType] = useState('table'); // 'table', 'pie', 'line'

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

  // 检测数值列和分类列
  const { numericColumns, categoryColumns } = useMemo(() => {
    if (!result.data || result.data.length === 0) {
      return { numericColumns: [], categoryColumns: [] };
    }

    const numericCols = [];
    const categoryCols = [];

    result.columns.forEach((col) => {
      const sampleValues = result.data.slice(0, Math.min(10, result.data.length)).map((row) => row[col]);
      const allNumeric = sampleValues.every((val) => {
        if (val === null || val === undefined || val === '') {
          return false;
        }
        return typeof val === 'number' || (!isNaN(Number(val)) && val !== '');
      });

      if (allNumeric && sampleValues.some((val) => val !== null && val !== undefined && val !== '')) {
        numericCols.push(col);
      } else {
        categoryCols.push(col);
      }
    });

    return { numericColumns: numericCols, categoryColumns: categoryCols };
  }, [result.data, result.columns]);

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

  // 准备图表数据
  const chartData = useMemo(() => {
    if (viewType === 'table' || !result.data || result.data.length === 0) {
      return null;
    }

    // 饼图：需要分类列 + 数值列
    if (viewType === 'pie') {
      if (categoryColumns.length === 0 || numericColumns.length === 0) {
        return null;
      }
      const categoryCol = categoryColumns[0];
      const valueCol = numericColumns[0];

      return result.data.map((row) => ({
        type: String(row[categoryCol] || '未知'),
        value: Number(row[valueCol]) || 0,
      }));
    }

    // 折线图：需要分类列（或时间列）+ 数值列
    if (viewType === 'line') {
      if (numericColumns.length === 0) {
        return null;
      }
      const xCol = categoryColumns.length > 0 ? categoryColumns[0] : result.columns[0];
      const yCol = numericColumns[0];

      return result.data.map((row, index) => ({
        x: String(row[xCol] || index),
        y: Number(row[yCol]) || 0,
      }));
    }

    return null;
  }, [viewType, result.data, result.columns, categoryColumns, numericColumns]);

  // 检查是否可以显示图表
  const canShowPie = categoryColumns.length > 0 && numericColumns.length > 0;
  const canShowLine = numericColumns.length > 0;

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
      
      {/* 视图类型选择器 */}
      <div style={{ 
        marginBottom: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '8px',
      }}>
        <div style={{ 
          color: '#666',
          fontSize: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
        }}>
          <BarChartOutlined /> 查询结果
          <span style={{ marginLeft: '8px', fontSize: '12px' }}>
            （共 {result.data.length} 条记录）
          </span>
        </div>
        <Radio.Group
          value={viewType}
          onChange={(e) => setViewType(e.target.value)}
          size="small"
          buttonStyle="solid"
        >
          <Radio.Button value="table" disabled={false}>
            <TableOutlined /> 表格
          </Radio.Button>
          <Radio.Button value="pie" disabled={!canShowPie}>
            <PieChartOutlined /> 饼图
          </Radio.Button>
          <Radio.Button value="line" disabled={!canShowLine}>
            <LineChartOutlined /> 折线图
          </Radio.Button>
        </Radio.Group>
      </div>

      {/* 表格视图 */}
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

      {/* 饼图视图 */}
      {viewType === 'pie' && chartData && (
        <div style={{ 
          padding: '16px',
          background: '#fff',
          borderRadius: '4px',
          minHeight: '300px',
        }}>
          <Pie
            data={chartData}
            angleField="value"
            colorField="type"
            radius={0.8}
            label={{
              type: 'outer',
              content: '{name}: {percentage}',
            }}
            interactions={[{ type: 'element-active' }]}
          />
        </div>
      )}

      {/* 折线图视图 */}
      {viewType === 'line' && chartData && (
        <div style={{ 
          padding: '16px',
          background: '#fff',
          borderRadius: '4px',
          minHeight: '300px',
        }}>
          <Line
            data={chartData}
            xField="x"
            yField="y"
            point={{
              size: 5,
              shape: 'circle',
            }}
            label={{
              style: {
                fill: '#aaa',
              },
            }}
            smooth={true}
          />
        </div>
      )}

      {/* 图表不可用提示 */}
      {viewType === 'pie' && !chartData && (
        <Alert
          message="无法显示饼图"
          description="饼图需要至少一个分类列和一个数值列"
          type="warning"
          showIcon
        />
      )}
      {viewType === 'line' && !chartData && (
        <Alert
          message="无法显示折线图"
          description="折线图需要至少一个数值列"
          type="warning"
          showIcon
        />
      )}
    </div>
  );
}

export default ReportDisplay;

