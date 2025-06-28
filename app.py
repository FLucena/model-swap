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
import logging

# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass

# Configure logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Production configuration
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Rate limiting with Redis for production (fallback to memory for development)
if os.environ.get('REDIS_URL'):
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.environ.get('REDIS_URL')
    )
else:
    # Use memory storage for development (not recommended for production)
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
        error_msg = str(e)
        if "ptp" in error_msg and "NumPy" in error_msg:
            raise Exception(f"NumPy compatibility issue detected. Please ensure NumPy version 1.26.x is installed. Error: {error_msg}")
        else:
            raise Exception(f"Conversion failed: {error_msg}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limit uploads
def upload_file():
    try:
        if 'files[]' not in request.files:
            logger.warning("Upload attempt without files")
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        output_format = request.form.get('output_format', 'obj')
        
        if not files or files[0].filename == '':
            logger.warning("Upload attempt with empty files")
            return jsonify({'error': 'No files selected'}), 400
        
        # Check file count limit
        if len(files) > app.config['MAX_FILES_PER_REQUEST']:
            logger.warning(f"Upload attempt with too many files: {len(files)}")
            return jsonify({'error': f'Maximum {app.config["MAX_FILES_PER_REQUEST"]} files allowed per request'}), 400
        
        if output_format not in SUPPORTED_FORMATS:
            logger.warning(f"Unsupported output format requested: {output_format}")
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
                    error_msg = f"File too large: {file.filename} (max 100MB per file)"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    continue
                try:
                    # Secure filename and save
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
                    
                    logger.info(f"Converting file: {filename} to {output_format}")
                    
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
                    
                    logger.info(f"Successfully converted: {filename} -> {output_filename}")
                    
                    # Clean up uploaded file
                    os.remove(filepath)
                    
                except Exception as e:
                    error_msg = f"Error converting {file.filename}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    # Clean up on error
                    if os.path.exists(filepath):
                        os.remove(filepath)
            else:
                error_msg = f"Invalid file format: {file.filename}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        logger.info(f"Upload completed: {len(converted_files)} successful, {len(errors)} errors")
        return jsonify({
            'success': True,
            'converted_files': converted_files,
            'errors': errors
        })
    except Exception as e:
        logger.error(f"Unexpected error in upload: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

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

@app.route('/health')
def health_check():
    """Health check endpoint for production monitoring"""
    return jsonify({'status': 'healthy', 'service': 'modelswap'}), 200

@app.errorhandler(413)
def too_large(e):
    logger.warning("File too large error")
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 error: {request.url}")
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting ModelSwap server on port {port}")
    logger.info(f"Environment: {app.config['ENV']}")
    logger.info(f"Debug mode: {debug_mode}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port) 