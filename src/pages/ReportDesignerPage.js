import React, { useState, useEffect } from 'react';
import { Layout, Typography, Button, Table, Modal, message, Space, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useHistory, useParams } from 'react-router-dom';
import ReportBuilder from '../components/ReportBuilder';
import { reportApi } from '../utils/api';

const { Header, Content } = Layout;
const { Title } = Typography;

function ReportDesignerPage() {
  const history = useHistory();
  const { id } = useParams();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [builderVisible, setBuilderVisible] = useState(false);
  const [editingId, setEditingId] = useState(null);
  
  useEffect(() => {
    if (id) {
      setEditingId(parseInt(id));
      setBuilderVisible(true);
    } else {
      loadReports();
    }
  }, [id]);
  
  const loadReports = async () => {
    try {
      setLoading(true);
      const result = await reportApi.listReports();
      if (result.success) {
        setReports(result.data || []);
      }
    } catch (error) {
      message.error('加载报表列表失败');
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreate = () => {
    setEditingId(null);
    setBuilderVisible(true);
  };
  
  const handleEdit = (record) => {
    setEditingId(record.id);
    setBuilderVisible(true);
  };
  
  const handleDelete = async (record) => {
    try {
      const result = await reportApi.deleteReport(record.id);
      if (result.success) {
        message.success('删除成功');
        loadReports();
      } else {
        message.error(result.message || '删除失败');
      }
    } catch (error) {
      message.error('删除失败: ' + (error.message || '未知错误'));
    }
  };
  
  const handleSave = (report) => {
    setBuilderVisible(false);
    setEditingId(null);
    if (!id) {
      loadReports();
    } else {
      history.push('/reports');
    }
  };
  
  const handleCancel = () => {
    setBuilderVisible(false);
    setEditingId(null);
    if (id) {
      history.push('/reports');
    }
  };
  
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '报表名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '数据源',
      dataIndex: 'data_source',
      key: 'data_source',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个报表吗？"
            onConfirm={() => handleDelete(record)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];
  
  if (builderVisible) {
    return (
      <Layout style={{ height: '100vh' }}>
        <Header style={{ background: '#001529', padding: '0 24px', display: 'flex', alignItems: 'center' }}>
          <Button
            type="link"
            icon={<ArrowLeftOutlined />}
            onClick={handleCancel}
            style={{ color: '#fff', marginRight: 16 }}
          >
            返回
          </Button>
          <Title level={4} style={{ color: '#fff', margin: 0 }}>
            {editingId ? '编辑报表' : '创建报表'}
          </Title>
        </Header>
        <Content style={{ height: 'calc(100vh - 64px)' }}>
          <ReportBuilder reportId={editingId} onSave={handleSave} />
        </Content>
      </Layout>
    );
  }
  
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px', flexShrink: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ color: '#fff', margin: '16px 0' }}>
            报表设计器
          </Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            创建报表
          </Button>
        </div>
      </Header>
      <Content style={{
        flex: 1,
        padding: '24px',
        background: '#f0f2f5',
      }}>
        <div style={{
          background: '#fff',
          padding: '24px',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}>
          <Table
            columns={columns}
            dataSource={reports}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 10,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
          />
        </div>
      </Content>
    </Layout>
  );
}

export default ReportDesignerPage;

