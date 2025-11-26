from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from services.nl2sql_service import NL2SQLService
from services.database_service import DatabaseService
from services.query_service import QueryService

load_dotenv()

app = Flask(__name__)
CORS(app)

# 初始化服务
db_service = DatabaseService()
nl2sql_service = NL2SQLService(db_service)
query_service = QueryService(db_service, nl2sql_service)

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

if __name__ == '__main__':
  port = int(os.getenv('PORT', 5000))
  debug = os.getenv('DEBUG', 'False').lower() == 'true'
  app.run(host='0.0.0.0', port=port, debug=debug)

