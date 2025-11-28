from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from services.nl2sql_service import NL2SQLService
from services.database_service import DatabaseService
from services.query_service import QueryService
from services.report_service import ReportService

load_dotenv()

app = Flask(__name__)
CORS(app)

# 初始化服务
db_service = DatabaseService()
nl2sql_service = NL2SQLService(db_service)
query_service = QueryService(db_service, nl2sql_service)
report_service = ReportService(db_service)

@app.route('/api/query', methods=['POST'])
def query():
  """自然语言查询接口"""
  try:
    data = request.get_json()
    query_text = data.get('query', '').strip()
    show_sql = data.get('showSql', True)

    if not query_text:
      return jsonify({
        'success': False,
        'message': '查询内容不能为空',
      }), 400

    # 执行查询
    result = query_service.execute_query(query_text, show_sql)

    return jsonify(result)

  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'查询失败: {str(e)}',
    }), 500

@app.route('/api/tables', methods=['GET'])
def get_tables():
  """获取数据库表列表"""
  try:
    tables = db_service.get_tables()
    return jsonify({
      'success': True,
      'data': tables,
    })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'获取表列表失败: {str(e)}',
    }), 500

@app.route('/api/tables/<table_name>/columns', methods=['GET'])
def get_table_columns(table_name):
  """获取表字段信息"""
  try:
    columns = db_service.get_table_columns(table_name)
    return jsonify({
      'success': True,
      'data': columns,
    })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'获取字段信息失败: {str(e)}',
    }), 500

@app.route('/api/health', methods=['GET'])
def health():
  """健康检查接口"""
  return jsonify({
    'success': True,
    'message': '服务运行正常',
  })

# 报表相关接口
@app.route('/api/reports', methods=['GET'])
def list_reports():
  """获取报表列表"""
  try:
    reports = report_service.list_reports()
    return jsonify({
      'success': True,
      'data': reports,
    })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'获取报表列表失败: {str(e)}',
    }), 500

@app.route('/api/reports', methods=['POST'])
def create_report():
  """创建报表"""
  try:
    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    data_source = data.get('data_source', '').strip()
    layout_config = data.get('layout_config', {})
    query_config = data.get('query_config', {})
    
    if not name:
      return jsonify({
        'success': False,
        'message': '报表名称不能为空',
      }), 400
    
    if not data_source:
      return jsonify({
        'success': False,
        'message': '数据源不能为空',
      }), 400
    
    report = report_service.create_report(name, description, data_source, layout_config, query_config)
    return jsonify({
      'success': True,
      'data': report,
    })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'创建报表失败: {str(e)}',
    }), 500

@app.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
  """获取报表详情"""
  try:
    report = report_service.get_report(report_id)
    if not report:
      return jsonify({
        'success': False,
        'message': '报表不存在',
      }), 404
    
    return jsonify({
      'success': True,
      'data': report,
    })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'获取报表失败: {str(e)}',
    }), 500

@app.route('/api/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
  """更新报表"""
  try:
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    layout_config = data.get('layout_config')
    query_config = data.get('query_config')
    
    report = report_service.update_report(
      report_id,
      name=name,
      description=description,
      layout_config=layout_config,
      query_config=query_config,
    )
    
    return jsonify({
      'success': True,
      'data': report,
    })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'更新报表失败: {str(e)}',
    }), 500

@app.route('/api/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
  """删除报表"""
  try:
    deleted = report_service.delete_report(report_id)
    if not deleted:
      return jsonify({
        'success': False,
        'message': '报表不存在',
      }), 404
    
    return jsonify({
      'success': True,
      'message': '删除成功',
    })
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'删除报表失败: {str(e)}',
    }), 500

@app.route('/api/reports/execute', methods=['POST'])
def execute_report():
  """执行报表查询"""
  try:
    data = request.get_json()
    query_config = data.get('query_config', {})
    
    result = report_service.execute_report_query(query_config)
    return jsonify(result)
  except Exception as e:
    return jsonify({
      'success': False,
      'message': f'执行报表查询失败: {str(e)}',
      'data': [],
      'columns': [],
    }), 500

if __name__ == '__main__':
  port = int(os.getenv('PORT', 5000))
  debug = os.getenv('DEBUG', 'False').lower() == 'true'
  app.run(host='0.0.0.0', port=port, debug=debug)

