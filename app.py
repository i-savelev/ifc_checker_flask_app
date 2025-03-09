from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from ifchelper import Ifc_help

app = Flask(__name__)

app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads/'
REPORTS_FOLDER = 'static/reports/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'ifc', 'ids'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_files(name1, name2):
    return f'Функция выполнена {name1} {name2}'

@app.route('/')
def index():
    # session.clear()
    return render_template('form.html')

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    session.pop('error', None)
    session.pop('file1_path', None)
    session.pop('file2_path', None)
    session.pop('files_names', None)
    session.pop('html_file_name', None)
    session.pop('result', None)
    filename1 = ''
    filename2 = ''
    if request.method == 'POST':
        # Проверяем, переданы ли файлы
        file1 = request.files['file1']
        file2 = request.files['file2']
        # Проверяем, выбраны ли файлы
        if file1.filename == '' or file2.filename == '':
            session['error'] = "Файлы не выбраны"
            return redirect(url_for('index'))
        
        if file1 and file2:
            if not allowed_file(file1.filename) or not allowed_file(file2.filename):
                return "Недопустимое расширение файла"
            filename1 = file1.filename
            filename2 = file2.filename
            session['file1_path'] = f'/data/{filename1}'
            session['file2_path'] = f'/data/{filename2}'
            file1.save(f'/data/{filename1}')
            file2.save(f'/data/{filename2}')
            file_names = f'{filename1}, {filename2}'
            session['files_names'] = file_names
    return redirect(url_for('index'))

@app.route('/process', methods=['POST'])
def process():
    session.pop('result', None)
    session.pop('html_file_name', None)
    if 'file1_path' not in session or 'file2_path' not in session:
        session['error'] = "Сначала загрузите файлы"
        return redirect(url_for('index'))
    try:
        result = Ifc_help.check_ifc_file(session['file1_path'], session['file2_path'], 'data/')
        session['html_file_name'] = result
        session['result'] = result 
        session.pop('error', None)
    except Exception as e:
        session['error'] = f"Ошибка обработки: {str(e)}"
    
    return redirect(url_for('index'))

@app.route('/download')
def dowload():
    UPLOAD_DIR = '/data/'
    return send_from_directory(UPLOAD_DIR, session['html_file_name'], as_attachment=True)


if __name__ == '__main__':
    ...
    # app.run(debug=True)