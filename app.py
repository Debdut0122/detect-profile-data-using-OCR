from flask import Flask, request, redirect, url_for, send_from_directory, render_template, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename
import subprocess
import shutil
import zipfile
from io import BytesIO

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['EXPORT_FOLDER'] = 'exports/'

def recreate_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

recreate_folder(app.config['UPLOAD_FOLDER'])
recreate_folder(app.config['EXPORT_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        files = request.files.getlist('file')
        
        if len(files) == 0 or files[0].filename == '':
            return redirect(request.url)
        
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Execute the processing task (update task.py to handle multiple files if necessary)
        subprocess.run(['python', 'task.py'])
        
        # Redirect to the page that shows all files in the export folder
        return redirect(url_for('list_export_files'))
    
    return render_template('index.html')

@app.route('/exports')
def list_export_files():
    # List all files in the EXPORT_FOLDER
    export_files = os.listdir(app.config['EXPORT_FOLDER'])
    
    # Render a template with the list of files and download option
    return render_template('list_files.html', export_files=export_files)

@app.route('/view/<filename>')
def view_excel(filename):
    file_path = os.path.join(app.config['EXPORT_FOLDER'], filename)
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        table_html = df.to_html(classes='table table-striped', index=False)
        return render_template('view_excel.html', table_html=table_html, filename=filename)
    else:
        return "File not found", 404

@app.route('/exports/<filename>')
def export_file(filename):
    return send_from_directory(app.config['EXPORT_FOLDER'], filename)

@app.route('/download_all')
def download_all():
    # Create a zip of all files in the EXPORT_FOLDER
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for filename in os.listdir(app.config['EXPORT_FOLDER']):
            file_path = os.path.join(app.config['EXPORT_FOLDER'], filename)
            zip_file.write(file_path, arcname=filename)
    
    zip_buffer.seek(0)
    
    # Serve the zip file as a download
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='export_files.zip')

if __name__ == "__main__":
    app.run(debug=True)
