import React, { useState, useEffect } from 'react';
import { Layout, Card, Button, Select, Form, Input, Modal, message, Row, Col, Space, Divider } from 'antd';
import { PlusOutlined, DeleteOutlined, SaveOutlined, PlayCircleOutlined, DatabaseOutlined } from '@ant-design/icons';
import GridLayout from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { reportApi } from '../utils/api';
import ReportDisplay from './ReportDisplay';

const { Content, Sider } = Layout;
const { Option } = Select;
const { TextArea } = Input;

function ReportBuilder({ reportId = null, onSave = null }) {
  const [form] = Form.useForm();
  const [tables, setTables] = useState([]);
  const [columns, setColumns] = useState({});
  const [selectedTable, setSelectedTable] = useState(null);
  const [selectedFields, setSelectedFields] = useState([]);
  const [filters, setFilters] = useState([]);
  const [layout, setLayout] = useState([]);
  const [widgets, setWidgets] = useState([]);
  const [dataSource, setDataSource] = useState('default');
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewVisible, setPreviewVisible] = useState(false);
  
  // 加载报表数据
  useEffect(() => {
    if (reportId) {
      loadReport(reportId);
    } else {
      loadTables();
    }
  }, [reportId]);
  
  // 加载表列表
  const loadTables = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/tables');
      const result = await response.json();
      if (result.success) {
        setTables(result.data);
      }
    } catch (error) {
      message.error('加载表列表失败');
    }
  };
  
  // 加载报表配置
  const loadReport = async (id) => {
    try {
      setLoading(true);
      const result = await reportApi.getReport(id);
      if (result.success && result.data) {
        const report = result.data;
        form.setFieldsValue({
          name: report.name,
          description: report.description,
        });
        setDataSource(report.data_source);
        if (report.layout_config) {
          setLayout(report.layout_config.layout || []);
          setWidgets(report.layout_config.widgets || []);
        }
        if (report.query_config) {
          setSelectedTable(report.query_config.table);
          setSelectedFields(report.query_config.fields || []);
          setFilters(report.query_config.filters || []);
          if (report.query_config.table) {
            loadColumns(report.query_config.table);
          }
        }
      }
    } catch (error) {
      message.error('加载报表失败');
    } finally {
      setLoading(false);
    }
  };
  
  // 加载表字段
  const loadColumns = async (tableName) => {
    if (!tableName) {
      return;
    }
    try {
      const response = await fetch(`http://localhost:5000/api/tables/${tableName}/columns`);
      const result = await response.json();
      if (result.success) {
        setColumns({ ...columns, [tableName]: result.data });
      }
    } catch (error) {
      message.error('加载字段列表失败');
    }
  };
  
  // 处理表选择
  const handleTableChange = (value) => {
    setSelectedTable(value);
    setSelectedFields([]);
    loadColumns(value);
  };
  
  // 添加字段
  const handleAddField = () => {
    if (!selectedTable) {
      message.warning('请先选择数据表');
      return;
    }
    const tableColumns = columns[selectedTable] || [];
    if (tableColumns.length === 0) {
      message.warning('该表没有可用字段');
      return;
    }
    // 显示字段选择对话框
    Modal.confirm({
      title: '选择字段',
      content: (
        <Select
          style={{ width: '100%', marginTop: 16 }}
          placeholder="请选择字段"
          onChange={(value) => {
            const field = tableColumns.find((col) => col.name === value);
            if (field && !selectedFields.find((f) => f.name === value)) {
              setSelectedFields([...selectedFields, {
                name: field.name,
                alias: field.naturalName || field.name,
                table: selectedTable,
                type: field.type,
              }]);
              Modal.destroyAll();
            }
          }}
        >
          {tableColumns.map((col) => (
            <Option key={col.name} value={col.name}>
              {col.naturalName || col.name} ({col.name})
            </Option>
          ))}
        </Select>
      ),
      onOk: () => {},
    });
  };
  
  // 删除字段
  const handleRemoveField = (index) => {
    setSelectedFields(selectedFields.filter((_, i) => i !== index));
  };
  
  // 添加筛选条件
  const handleAddFilter = () => {
    if (!selectedTable) {
      message.warning('请先选择数据表');
      return;
    }
    const tableColumns = columns[selectedTable] || [];
    setFilters([...filters, {
      field: '',
      operator: '=',
      value: '',
    }]);
  };
  
  // 更新筛选条件
  const handleUpdateFilter = (index, key, value) => {
    const newFilters = [...filters];
    newFilters[index][key] = value;
    setFilters(newFilters);
  };
  
  // 删除筛选条件
  const handleRemoveFilter = (index) => {
    setFilters(filters.filter((_, i) => i !== index));
  };
  
  // 添加组件
  const handleAddWidget = (type) => {
    const newWidget = {
      i: `widget-${Date.now()}`,
      type: type,
      title: type === 'table' ? '数据表格' : type === 'chart' ? '图表' : '文本',
      x: 0,
      y: layout.length * 4,
      w: type === 'table' ? 12 : 6,
      h: type === 'table' ? 8 : 6,
    };
    setWidgets([...widgets, newWidget]);
    setLayout([...layout, {
      i: newWidget.i,
      x: newWidget.x,
      y: newWidget.y,
      w: newWidget.w,
      h: newWidget.h,
    }]);
  };
  
  // 删除组件
  const handleRemoveWidget = (widgetId) => {
    setWidgets(widgets.filter((w) => w.i !== widgetId));
    setLayout(layout.filter((l) => l.i !== widgetId));
  };
  
  // 布局变化
  const handleLayoutChange = (newLayout) => {
    setLayout(newLayout);
  };
  
  // 预览报表
  const handlePreview = async () => {
    if (!selectedTable || selectedFields.length === 0) {
      message.warning('请先配置数据源和字段');
      return;
    }
    try {
      setLoading(true);
      const queryConfig = {
        tables: [selectedTable],
        fields: selectedFields.map((f) => ({
          table: f.table,
          field: f.name,
          alias: f.alias,
        })),
        filters: filters.filter((f) => f.field && f.value),
      };
      const result = await reportApi.executeReport(queryConfig);
      if (result.success) {
        setPreviewData(result);
        setPreviewVisible(true);
      } else {
        message.error(result.message || '查询失败');
      }
    } catch (error) {
      message.error('预览失败: ' + (error.message || '未知错误'));
    } finally {
      setLoading(false);
    }
  };
  
  // 保存报表
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (!selectedTable || selectedFields.length === 0) {
        message.warning('请先配置数据源和字段');
        return;
      }
      
      const reportData = {
        name: values.name,
        description: values.description || '',
        data_source: dataSource,
        layout_config: {
          layout: layout,
          widgets: widgets,
        },
        query_config: {
          table: selectedTable,
          fields: selectedFields,
          filters: filters.filter((f) => f.field && f.value),
        },
      };
      
      setLoading(true);
      let result;
      if (reportId) {
        result = await reportApi.updateReport(reportId, reportData);
      } else {
        result = await reportApi.createReport(reportData);
      }
      
      if (result.success) {
        message.success(reportId ? '更新成功' : '创建成功');
        if (onSave) {
          onSave(result.data);
        }
      } else {
        message.error(result.message || '保存失败');
      }
    } catch (error) {
      message.error('保存失败: ' + (error.message || '未知错误'));
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Layout style={{ height: '100vh' }}>
      <Sider width={300} style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}>
        <div style={{ padding: '16px' }}>
          <Form form={form} layout="vertical">
            <Form.Item label="报表名称" name="name" rules={[{ required: true, message: '请输入报表名称' }]}>
              <Input placeholder="请输入报表名称" />
            </Form.Item>
            <Form.Item label="报表描述" name="description">
              <TextArea rows={2} placeholder="请输入报表描述" />
            </Form.Item>
          </Form>
          
          <Divider>数据源配置</Divider>
          
          <Form.Item label="数据源">
            <Select value={dataSource} onChange={setDataSource} disabled>
              <Option value="default">默认SQLite数据库</Option>
            </Select>
          </Form.Item>
          
          <Form.Item label="数据表">
            <Select
              value={selectedTable}
              onChange={handleTableChange}
              placeholder="请选择数据表"
              style={{ width: '100%' }}
            >
              {tables.map((table) => (
                <Option key={table.name} value={table.name}>
                  {table.naturalName || table.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item label="字段配置">
            <Space direction="vertical" style={{ width: '100%' }}>
              {selectedFields.map((field, index) => (
                <Card key={index} size="small" style={{ marginBottom: 8 }}>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <span>{field.alias || field.name}</span>
                      <span style={{ color: '#999', marginLeft: 8 }}>({field.name})</span>
                    </Col>
                    <Col>
                      <Button
                        type="link"
                        danger
                        size="small"
                        icon={<DeleteOutlined />}
                        onClick={() => handleRemoveField(index)}
                      />
                    </Col>
                  </Row>
                </Card>
              ))}
              <Button
                type="dashed"
                block
                icon={<PlusOutlined />}
                onClick={handleAddField}
              >
                添加字段
              </Button>
            </Space>
          </Form.Item>
          
          <Form.Item label="筛选条件">
            <Space direction="vertical" style={{ width: '100%' }}>
              {filters.map((filter, index) => (
                <Card key={index} size="small" style={{ marginBottom: 8 }}>
                  <Row gutter={8}>
                    <Col span={8}>
                      <Select
                        value={filter.field}
                        onChange={(value) => handleUpdateFilter(index, 'field', value)}
                        placeholder="字段"
                        style={{ width: '100%' }}
                      >
                        {(columns[selectedTable] || []).map((col) => (
                          <Option key={col.name} value={col.name}>
                            {col.naturalName || col.name}
                          </Option>
                        ))}
                      </Select>
                    </Col>
                    <Col span={6}>
                      <Select
                        value={filter.operator}
                        onChange={(value) => handleUpdateFilter(index, 'operator', value)}
                        style={{ width: '100%' }}
                      >
                        <Option value="=">=</Option>
                        <Option value="!=">!=</Option>
                        <Option value=">">&gt;</Option>
                        <Option value="<">&lt;</Option>
                        <Option value=">=">&gt;=</Option>
                        <Option value="<=">&lt;=</Option>
                        <Option value="LIKE">LIKE</Option>
                      </Select>
                    </Col>
                    <Col span={8}>
                      <Input
                        value={filter.value}
                        onChange={(e) => handleUpdateFilter(index, 'value', e.target.value)}
                        placeholder="值"
                      />
                    </Col>
                    <Col span={2}>
                      <Button
                        type="link"
                        danger
                        size="small"
                        icon={<DeleteOutlined />}
                        onClick={() => handleRemoveFilter(index)}
                      />
                    </Col>
                  </Row>
                </Card>
              ))}
              <Button
                type="dashed"
                block
                icon={<PlusOutlined />}
                onClick={handleAddFilter}
              >
                添加筛选条件
              </Button>
            </Space>
          </Form.Item>
          
          <Divider>组件库</Divider>
          
          <Space direction="vertical" style={{ width: '100%' }}>
            <Button
              block
              onClick={() => handleAddWidget('table')}
              icon={<DatabaseOutlined />}
            >
              数据表格
            </Button>
            <Button
              block
              onClick={() => handleAddWidget('chart')}
            >
              图表
            </Button>
            <Button
              block
              onClick={() => handleAddWidget('text')}
            >
              文本
            </Button>
          </Space>
          
          <Divider />
          
          <Space direction="vertical" style={{ width: '100%' }}>
            <Button
              type="primary"
              block
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={loading}
            >
              保存报表
            </Button>
            <Button
              block
              icon={<PlayCircleOutlined />}
              onClick={handlePreview}
              loading={loading}
            >
              预览报表
            </Button>
          </Space>
        </div>
      </Sider>
      
      <Content style={{ background: '#f0f2f5', padding: '16px', overflow: 'auto' }}>
        <div style={{ background: '#fff', minHeight: '100%', padding: '16px' }}>
          {layout.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '100px 0', color: '#999' }}>
              <p>从左侧组件库拖拽组件到此处开始设计报表</p>
            </div>
          ) : (
            <GridLayout
              className="layout"
              layout={layout}
              cols={12}
              rowHeight={30}
              width={1200}
              onLayoutChange={handleLayoutChange}
            >
              {widgets.map((widget) => (
                <div key={widget.i} style={{ border: '1px solid #d9d9d9', borderRadius: '4px', padding: '8px' }}>
                  <Card
                    size="small"
                    title={widget.title}
                    extra={
                      <Button
                        type="link"
                        danger
                        size="small"
                        icon={<DeleteOutlined />}
                        onClick={() => handleRemoveWidget(widget.i)}
                      />
                    }
                  >
                    {widget.type === 'table' && (
                      <div style={{ padding: '16px', textAlign: 'center', color: '#999' }}>
                        数据表格组件
                      </div>
                    )}
                    {widget.type === 'chart' && (
                      <div style={{ padding: '16px', textAlign: 'center', color: '#999' }}>
                        图表组件
                      </div>
                    )}
                    {widget.type === 'text' && (
                      <div style={{ padding: '16px', textAlign: 'center', color: '#999' }}>
                        文本组件
                      </div>
                    )}
                  </Card>
                </div>
              ))}
            </GridLayout>
          )}
        </div>
      </Content>
      
      <Modal
        title="报表预览"
        visible={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={1200}
      >
        {previewData && (
          <ReportDisplay result={previewData} />
        )}
      </Modal>
    </Layout>
  );
}

export default ReportBuilder;

