import React, { useState } from 'react';
import { Card, Input, Button, Space, message } from 'antd';
import { SearchOutlined, ClearOutlined, QuestionCircleOutlined } from '@ant-design/icons';

const { TextArea } = Input;

const EXAMPLE_QUERIES = [
  '查询所有用户',
  '查询年龄大于30的用户',
  '统计每个城市的用户数量',
  '查询订单总金额',
  '查询订单金额大于1000的订单',
  '按订单金额降序排列前10条订单',
];

function QueryInput({ onQuery, loading }) {
  const [queryText, setQueryText] = useState('');

  const handleQuery = () => {
    if (!queryText.trim()) {
      message.warning('请输入查询内容');
      return;
    }
    onQuery(queryText);
  };

  const handleClear = () => {
    setQueryText('');
  };

  const handleExample = (example) => {
    setQueryText(example);
  };

  return (
    <Card
      title="自然语言查询"
      style={{ marginBottom: 0 }}
      extra={
        <Button
          type="link"
          icon={<QuestionCircleOutlined />}
          onClick={() => {
            message.info('在输入框中输入自然语言查询，例如：查询所有用户、统计订单总金额等');
          }}
        >
          使用帮助
        </Button>
      }
    >
      <TextArea
        rows={4}
        placeholder="请输入您的查询需求，例如：查询所有用户、统计每个城市的用户数量、查询订单金额大于1000的订单..."
        value={queryText}
        onChange={(e) => {
          setQueryText(e.target.value);
        }}
        onPressEnter={(e) => {
          if (e.ctrlKey || e.metaKey) {
            handleQuery();
          }
        }}
        style={{ marginBottom: '16px' }}
      />
      <Space>
        <Button
          type="primary"
          icon={<SearchOutlined />}
          onClick={handleQuery}
          loading={loading}
        >
          查询
        </Button>
        <Button icon={<ClearOutlined />} onClick={handleClear}>
          清空
        </Button>
      </Space>
      <div style={{ marginTop: '16px' }}>
        <div style={{ marginBottom: '8px', color: '#666' }}>示例查询：</div>
        <Space wrap>
          {EXAMPLE_QUERIES.map((example, index) => (
            <Button
              key={index}
              size="small"
              type="dashed"
              onClick={() => {
                handleExample(example);
              }}
            >
              {example}
            </Button>
          ))}
        </Space>
      </div>
    </Card>
  );
}

export default QueryInput;

