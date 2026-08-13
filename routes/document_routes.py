import os
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename

document_bp = Blueprint('document', __name__)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@document_bp.route('/documents')
def documents():
    return render_template('documents.html')

@document_bp.route('/api/documents', methods=['GET'])
def api_list_documents():
    doc_loader = current_app.document_loader
    summaries = doc_loader.get_document_summary()
    return jsonify({'documents': summaries, 'total': len(summaries)})

@document_bp.route('/api/upload', methods=['POST'])
def api_upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        dest_path = os.path.join(current_app.config['DOCUMENTS_DIR'], filename)
        
        try:
            file.save(dest_path)
            
            # Re-index document passages in IR Engine
            passages = current_app.document_loader.load_all_documents()
            current_app.ir_engine.build_index(passages)
            
            return jsonify({
                'status': 'success',
                'message': f'Document "{filename}" uploaded and indexed successfully.',
                'filename': filename,
                'passages_count': len(passages)
            })
        except Exception as e:
            return jsonify({'error': f'Failed to process uploaded file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Unsupported file format. Allowed: .txt, .pdf, .csv'}), 400

@document_bp.route('/api/documents/delete', methods=['POST'])
def api_delete_document():
    data = request.get_json() or {}
    filename = data.get('filename', '')
    if not filename:
        return jsonify({'error': 'Filename is required.'}), 400

    filepath = os.path.join(current_app.config['DOCUMENTS_DIR'], secure_filename(filename))
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            # Re-index documents
            passages = current_app.document_loader.load_all_documents()
            current_app.ir_engine.build_index(passages)
            return jsonify({'status': 'success', 'message': f'Document "{filename}" deleted and index rebuilt.'})
        except Exception as e:
            return jsonify({'error': f'Could not delete file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'File not found.'}), 404
