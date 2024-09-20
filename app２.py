from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import pandas as pd
import os
from werkzeug.utils import secure_filename
import subprocess
import shutil


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
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            subprocess.run(['python', 'task.py'])
            return redirect(url_for('view_excel', filename='voter_data.xlsx'))
    return render_template('index.html')

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

if __name__ == "__main__":
    app.run(debug=True)
