import connexion
from flask import request, jsonify
from Src.start_service import start_service
from Src.Dtos.complex_filter_dto import complex_filter_dto
from Src.Dtos.filter_dto import filter_dto
from Src.Core.prototype import prototype
from Src.Core.validator import operation_exception
from Src.Logics.response_markdown import response_markdown
from Src.Logics.response_csv import response_scv
from Src.Core.response_formats import response_formats
from Src.Logics.factory_entities import factory_entities
from Src.filter_types import filter_types

app = connexion.FlaskApp(__name__)

service = start_service()
service.start()

@app.route("/api/accessibility", methods=['GET'])
def accessibility():
    """
    Проверить доступность REST API
    """
    return "SUCCESS"

@app.route("/api/test/nomenclature", methods=['GET'])
def test_nomenclature():
    try:
        complex_filter = complex_filter_dto()
        filter_item = filter_dto()
        filter_item.field_name = "name"
        filter_item.value = "мука"
        filter_item.filter_type = filter_types.LIKE
        complex_filter.filters = [filter_item]
        complex_filter.model_type = "nomenclature"
        
        repo_data = service.data
        data_to_filter = repo_data.get('nomenclature_model', [])
        filtered_data = prototype.complex_filter(data_to_filter, complex_filter)
        
        result = []
        for item in filtered_data:
            result.append({
                'name': item.name,
                'id': item.unique_code,
                'group': item.group.name if item.group else None,
                'range': item.range.name if item.range else None
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/test/groups", methods=['GET'])
def test_groups():
    """Быстрый тест получения групп"""
    try:
        repo_data = service.data
        groups = repo_data.get('group_model', [])
        
        result = []
        for item in groups:
            result.append({
                'name': item.name,
                'id': item.unique_code
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/test/ranges", methods=['GET'])
def test_ranges():
    try:
        repo_data = service.data
        ranges = repo_data.get('range_model', [])
        
        result = []
        for item in ranges:
            result.append({
                'name': item.name,
                'id': item.unique_code,
                'base': item.base.name if item.base else None,
                'value': item.value
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/test/storages", methods=['GET'])
def test_storages():
    try:
        repo_data = service.data
        storages = repo_data.get('storage_key', [])
        
        result = []
        for item in storages:
            result.append({
                'name': item.name,
                'id': item.unique_code,
                'address': item.address
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/test/transactions", methods=['GET'])
def test_transactions():
    try:
        repo_data = service.data
        transactions = repo_data.get('transaction_key', [])
        
        result = []
        for item in transactions[:10]:  
            result.append({
                'id': item.unique_code,
                'nomenclature': item.nomenclature.name if item.nomenclature else None,
                'storage': item.storage.name if item.storage else None,
                'range': item.range.name if item.range else None,
                'value': item.value,
                'period': str(item.period)
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/test/osv", methods=['GET'])
def test_osv():
    try:
        repo_data = service.data
        transactions = repo_data.get('transaction_key', [])
        osv_data = prototype.generate_osv(transactions)
        return jsonify(osv_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/filter/nomenclature/<search_term>", methods=['GET'])
def filter_nomenclature_simple(search_term):
    try:
        complex_filter = complex_filter_dto()
        filter_item = filter_dto()
        filter_item.field_name = "name"
        filter_item.value = search_term
        filter_item.filter_type = filter_types.LIKE
        complex_filter.filters = [filter_item]
        complex_filter.model_type = "nomenclature"
        
        repo_data = service.data
        data_to_filter = repo_data.get('nomenclature_model', [])
        filtered_data = prototype.complex_filter(data_to_filter, complex_filter)
        
        result = []
        for item in filtered_data:
            result.append({
                'name': item.name,
                'id': item.unique_code,
                'group': item.group.name if item.group else None,
                'range': item.range.name if item.range else None
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/filter/range/<search_term>", methods=['GET'])
def filter_range_simple(search_term):
    try:
        complex_filter = complex_filter_dto()
        filter_item = filter_dto()
        filter_item.field_name = "name"
        filter_item.value = search_term
        filter_item.filter_type = filter_types.LIKE
        complex_filter.filters = [filter_item]
        complex_filter.model_type = "range"
        
        repo_data = service.data
        data_to_filter = repo_data.get('range_model', [])
        filtered_data = prototype.complex_filter(data_to_filter, complex_filter)
        
        result = []
        for item in filtered_data:
            result.append({
                'name': item.name,
                'id': item.unique_code,
                'base': item.base.name if item.base else None,
                'value': item.value
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/filter/<model_type>", methods=['POST'])
def filter_data(model_type: str):
    try:
        filter_data = request.get_json()
        if not filter_data:
            return jsonify({"error": "No filter data provided"}), 400
            
        complex_filter = complex_filter_dto().create(filter_data)
        complex_filter.model_type = model_type
        
        repo_data = service.data
        model_key = _get_model_key(model_type)
        
        if model_key not in repo_data:
            return jsonify({"error": f"Model type {model_type} not found"}), 404
            
        data_to_filter = repo_data[model_key]
        
        filtered_data = prototype.complex_filter(data_to_filter, complex_filter)
        
        response_format = filter_data.get('format', response_formats.json())
        factory = factory_entities()
        response_builder = factory.create(response_format)()
        
        dto_data = []
        for item in filtered_data:
            if hasattr(item, 'to_dto'):
                dto_data.append(item.to_dto())
            else:
                dto_data.append(item)
                
        result = response_builder.build(dto_data)
        
        return result, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/osv", methods=['POST'])
def generate_osv():
    try:
        filter_data = request.get_json() or {}
        
        complex_filter = None
        if 'filters' in filter_data:
            complex_filter = complex_filter_dto().create(filter_data)
        
        repo_data = service.data
        transactions = repo_data.get('transaction_key', [])
        
        osv_data = prototype.generate_osv(transactions, complex_filter)
        
        response_format = filter_data.get('format', response_formats.json())
        factory = factory_entities()
        response_builder = factory.create(response_format)()
        
        result = response_builder.build(osv_data)
        
        return result, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/osv/simple", methods=['GET'])
def generate_osv_simple():
    try:
        repo_data = service.data
        transactions = repo_data.get('transaction_key', [])
        osv_data = prototype.generate_osv(transactions)
        
        return jsonify(osv_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _get_model_key(model_type: str) -> str:
    model_mapping = {
        'nomenclature': 'nomenclature_model',
        'group': 'group_model', 
        'range': 'range_model',
        'receipt': 'receipt_model',
        'storage': 'storage_key',
        'transaction': 'transaction_key'
    }
    return model_mapping.get(model_type.lower(), model_type.lower())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)