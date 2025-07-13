import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, jsonify
from werkzeug.utils import secure_filename

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', '7z', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Helper Functions ---
def allowed_file(filename):
    """Checks if a file's extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---

@app.route('/')
def index():
    """Renders the main FileHUB page."""
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

@app.route('/list_files_json')
def list_files_json():
    """Returns a JSON list of all uploaded files."""
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return jsonify(files), 200
    except Exception as e:
        return jsonify({'message': f'[[ERROR]]: Could not list files - {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Allows downloading of an uploaded file."""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'message': f'[[ERROR]]: File "{filename}" not found.'}), 404
    except Exception as e:
        return jsonify({'message': f'[[ERROR]]: Could not download file - {str(e)}'}), 500

@app.route('/delete_file/<filename>', methods=['POST'])
def delete_file(filename):
    """Handles the deletion of an uploaded file."""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return jsonify({'message': f'[[DELETION_SUCCESS]]: File "{filename}" purged.'}), 200
        except Exception as e:
            return jsonify({'message': f'[[DELETION_FAILED]]: Could not purge file "{filename}" - {str(e)}'}), 500
    else:
        return jsonify({'message': f'[[DELETION_FAILED]]: File "{filename}" not found on server.'}), 404

# --- Run the application ---
if __name__ == '__main__':
    # For development, you can set debug=True
    # For production, use a production-ready WSGI server like Gunicorn or Waitress
    app.run()