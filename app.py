from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import tempfile
import shutil
from werkzeug.utils import secure_filename
import uuid
from pathlib import Path
import logging
import gc
import psutil
import time

# Try to import trimesh, but don't fail if it's not available
try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    logging.warning("trimesh not available - 3D conversion features will be disabled")

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
redis_url = os.environ.get('REDIS_URL')
if redis_url:
    try:
        from flask_limiter.util import get_remote_address
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=redis_url,
            strategy="fixed-window-elastic-expiry"
        )
        logger.info("Flask-Limiter configured with Redis storage")
    except Exception as e:
        logger.warning(f"Failed to configure Redis storage for Flask-Limiter: {e}")
        logger.warning("Falling back to in-memory storage")
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
else:
    # Use memory storage for development (not recommended for production)
    logger.warning("No REDIS_URL found - using in-memory storage for rate limiting")
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
    if not TRIMESH_AVAILABLE:
        raise Exception("3D conversion service is not available. Please try again later.")
    
    temp_output = None
    try:
        # Load the mesh
        mesh = trimesh.load(input_path)
        
        # Create temporary file for output
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}')
        temp_output.close()
        
        # Always use a Trimesh object for export
        mesh_to_export = None
        if hasattr(mesh, 'export'):
            mesh_to_export = mesh
        elif isinstance(mesh, list) and len(mesh) > 0 and hasattr(mesh[0], 'export'):
            mesh_to_export = mesh[0]
        else:
            raise Exception("Invalid mesh format")
        
        mesh_to_export.export(temp_output.name, file_type=output_format)  # type: ignore[attr-defined]
        
        # Clear mesh from memory
        del mesh
        gc.collect()
        
        return temp_output.name
    except Exception as e:
        # Clean up temp file on error
        if temp_output and os.path.exists(temp_output.name):
            try:
                os.remove(temp_output.name)
            except:
                pass
        
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
        # Log memory usage before processing
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        logger.info(f"Memory usage before upload: {initial_memory:.2f} MB")
        
        if 'files[]' not in request.files:
            logger.warning("Upload attempt without files")
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        output_format = request.form.get('output_format', 'obj')
        
        if not files or files[0].filename == '':
            logger.warning("Upload attempt with empty files")
            return jsonify({'error': 'No files selected'}), 400
        
        # Only process one file at a time to prevent memory leaks
        if len(files) > 1:
            logger.warning(f"Multiple files received ({len(files)}), only processing first file")
            files = [files[0]]  # Only process the first file
        
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
                
                filepath = None
                try:
                    # Secure filename and save
                    if file.filename is None:
                        error_msg = f"Invalid filename for file"
                        logger.warning(error_msg)
                        errors.append(error_msg)
                        continue
                        
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
                    
                except Exception as e:
                    error_msg = f"Error converting {file.filename}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                finally:
                    # Clean up uploaded file
                    if filepath and os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except Exception as e:
                            logger.warning(f"Failed to clean up {filepath}: {e}")
            else:
                error_msg = f"Invalid file format: {file.filename}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # Force garbage collection after processing
        gc.collect()
        
        # Log memory usage after processing
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_diff = final_memory - initial_memory
        logger.info(f"Memory usage after upload: {final_memory:.2f} MB (diff: {memory_diff:+.2f} MB)")
        
        logger.info(f"Upload completed: {len(converted_files)} successful, {len(errors)} errors")
        return jsonify({
            'success': True,
            'converted_files': converted_files,
            'errors': errors
        })
    except Exception as e:
        logger.error(f"Unexpected error in upload: {str(e)}")
        # Force garbage collection on error
        gc.collect()
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
    try:
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        return jsonify({
            'status': 'healthy', 
            'service': 'modelswap',
            'trimesh_available': TRIMESH_AVAILABLE,
            'memory_usage_mb': round(memory_mb, 2),
            'memory_percent': round(process.memory_percent(), 2)
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'error',
            'service': 'modelswap',
            'error': str(e)
        }), 500

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