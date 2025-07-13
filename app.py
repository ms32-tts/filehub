import os
from flask import Flask, request, redirect, send_from_directory, render_template, jsonify
from werkzeug.utils import secure_filename

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', '7z', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Max 100MB upload limit

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Helper Function ---
def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---
@app.route('/')
def index():
    """Main upload page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file uploads."""
    if 'file' not in request.files:
        return jsonify({'message': '[[ERROR]]: No file part in the request.'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': '[[ERROR]]: No selected file.'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        try:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({'message': f'[[UPLOAD_SUCCESS]]: File "{filename}" successfully deployed.'}), 200
        except Exception as e:
            return jsonify({'message': f'[[UPLOAD_FAILED]]: Error saving file - {str(e)}'}), 500
    else:
        return jsonify({'message': '[[UPLOAD_FAILED]]: File type not allowed.'}), 400

@app.route('/list_files_json', methods=['GET'])
def list_files_json():
    """Returns list of uploaded files."""
    try:
        files = sorted(f for f in os.listdir(app.config['UPLOAD_FOLDER']) if not f.startswith('.'))
        return jsonify(files), 200
    except Exception as e:
        return jsonify({'message': f'[[ERROR]]: Could not list files - {str(e)}'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download a specific file."""
    try:
        safe_name = secure_filename(filename)
        return send_from_directory(app.config['UPLOAD_FOLDER'], safe_name, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'message': f'[[ERROR]]: File "{filename}" not found.'}), 404
    except Exception as e:
        return jsonify({'message': f'[[ERROR]]: Could not download file - {str(e)}'}), 500

@app.route('/delete_file/<filename>', methods=['POST'])
def delete_file(filename):
    """Delete a file by filename."""
    safe_name = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return jsonify({'message': f'[[DELETION_SUCCESS]]: File "{safe_name}" purged.'}), 200
        except Exception as e:
            return jsonify({'message': f'[[DELETION_FAILED]]: Could not purge file - {str(e)}'}), 500
    else:
        return jsonify({'message': f'[[DELETION_FAILED]]: File "{safe_name}" not found on server.'}), 404

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)
