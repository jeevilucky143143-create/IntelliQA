from flask import Blueprint, render_template, request, jsonify, current_app

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.route('/knowledge')
def knowledge():
    return render_template('knowledge.html')

@knowledge_bp.route('/graph')
def graph_page():
    return render_template('graph.html')

@knowledge_bp.route('/api/knowledge', methods=['GET'])
def api_list_knowledge():
    engine = current_app.knowledge_engine
    records = engine.get_all_records()
    return jsonify({'records': records, 'total': len(records)})

@knowledge_bp.route('/api/knowledge/add', methods=['POST'])
def api_add_knowledge():
    data = request.get_json() or {}
    entity = data.get('entity', '').strip()
    attribute = data.get('attribute', '').strip()
    value = data.get('value', '').strip()
    category = data.get('category', 'General').strip()
    description = data.get('description', '').strip()

    if not entity or not attribute or not value:
        return jsonify({'error': 'Entity, Attribute, and Value are required fields.'}), 400

    engine = current_app.knowledge_engine
    rec = engine.add_record(entity, attribute, value, category, description, source='User Entry')
    return jsonify({'status': 'success', 'message': 'Record added successfully.', 'record': rec})

@knowledge_bp.route('/api/knowledge/delete', methods=['POST'])
def api_delete_knowledge():
    data = request.get_json() or {}
    record_id = data.get('id')

    if not record_id:
        return jsonify({'error': 'Record ID is required.'}), 400

    engine = current_app.knowledge_engine
    success = engine.delete_record(int(record_id))
    if success:
        return jsonify({'status': 'success', 'message': 'Record deleted successfully.'})
    else:
        return jsonify({'error': 'Record not found or failed to delete.'}), 404

@knowledge_bp.route('/api/graph', methods=['GET'])
def api_graph_data():
    engine = current_app.knowledge_engine
    graph_data = engine.get_graph_data()
    return jsonify(graph_data)
