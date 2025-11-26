import React, { useState } from 'react';
import { Layout, Typography } from 'antd';
import QueryInput from '../components/QueryInput';
import SQLPreview from '../components/SQLPreview';
import ReportDisplay from '../components/ReportDisplay';

const { Header, Content } = Layout;
const { Title } = Typography;

function MainPage() {
  const [queryResult, setQueryResult] = useState(null);
  const [sql, setSql] = useState('');
  const [loading, setLoading] = useState(false);

  const handleQuery = async (queryText) => {
    setLoading(true);
    setQueryResult(null);
    setSql('');

    try {
      const response = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: queryText,
          showSql: true,
        },),
      });

      const result = await response.json();

      if (result.success) {
        setQueryResult(result);
        setSql(result.sql || '');
      } else {
        setQueryResult({
          success: false,
          message: result.message,
          data: [],
          columns: [],
        },);
      }
    } catch (error) {
      setQueryResult({
        success: false,
        message: `请求失败: ${error.message}`,
        data: [],
        columns: [],
      },);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <Title level={3} style={{ color: '#fff', margin: '16px 0' }}>
          AI报表生成系统
        </Title>
      </Header>
      <Content style={{ padding: '24px', background: '#f0f2f5' }}>
        <QueryInput onQuery={handleQuery} loading={loading} />
        {sql && <SQLPreview sql={sql} />}
        {queryResult && <ReportDisplay result={queryResult} />}
      </Content>
    </Layout>
  );
}

export default MainPage;

