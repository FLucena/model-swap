from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import trimesh
import tempfile
import shutil
from werkzeug.utils import secure_filename
import uuid
from pathlib import Path

app = Flask(__name__)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max request size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_FILES_PER_REQUEST'] = 10

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Supported formats (import and export)
SUPPORTED_FORMATS = {
    'obj': 'obj',
    'stl': 'stl',
    'ply': 'ply',
    'dae': 'dae',
    'gltf': 'gltf',
    'glb': 'glb',
    'off': 'off',
}

def allowed_file(filename):
    """Check if file extension is supported"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in SUPPORTED_FORMATS

def convert_model(input_path, output_format):
    """Convert 3D model to specified format"""
    try:
        # Load the mesh
        mesh = trimesh.load(input_path)
        
        # Create temporary file for output
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}')
        temp_output.close()
        
        # Export to desired format
        if output_format == 'obj':
            # For OBJ, we need to handle materials
            mesh.export(temp_output.name, file_type='obj')
        else:
            mesh.export(temp_output.name, file_type=output_format)
        
        return temp_output.name
    except Exception as e:
        raise Exception(f"Conversion failed: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limit uploads
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files[]')
    output_format = request.form.get('output_format', 'obj')
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    # Check file count limit
    if len(files) > app.config['MAX_FILES_PER_REQUEST']:
        return jsonify({'error': f'Maximum {app.config["MAX_FILES_PER_REQUEST"]} files allowed per request'}), 400
    
    if output_format not in SUPPORTED_FORMATS:
        return jsonify({'error': 'Unsupported output format'}), 400
    
    converted_files = []
    errors = []
    
    for file in files:
        if file and allowed_file(file.filename):
            # Per-file size check (100MB)
            file.seek(0, 2)  # Seek to end
            file_length = file.tell()
            file.seek(0)  # Reset pointer
            if file_length > 100 * 1024 * 1024:
                errors.append(f"File too large: {file.filename} (max 100MB per file)")
                continue
            try:
                # Secure filename and save
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                
                # Convert the file
                output_path = convert_model(filepath, output_format)
                
                # Move to outputs folder
                output_filename = f"{Path(filename).stem}.{output_format}"
                final_output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                shutil.move(output_path, final_output_path)
                
                converted_files.append({
                    'original_name': filename,
                    'converted_name': output_filename,
                    'download_url': url_for('download_file', filename=output_filename)
                })
                
                # Clean up uploaded file
                os.remove(filepath)
                
            except Exception as e:
                errors.append(f"Error converting {file.filename}: {str(e)}")
                # Clean up on error
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            errors.append(f"Invalid file format: {file.filename}")
    
    return jsonify({
        'success': True,
        'converted_files': converted_files,
        'errors': errors
    })

@app.route('/download/<filename>')
def download_file(filename):
    """Download converted file"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up temporary files"""
    try:
        # Clean uploads folder
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # Clean outputs folder
        for filename in os.listdir(app.config['OUTPUT_FOLDER']):
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        return jsonify({'success': True, 'message': 'Cleanup completed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 