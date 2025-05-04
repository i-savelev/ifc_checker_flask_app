from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from ifchelper import Ifc_help


app = Flask(__name__)
my_secret_key = ''
amvera_var = os.getenv("AMVERA", '0')
path = ''
if str(amvera_var) == "1":
    app.secret_key = os.environ['MY_SECRET_KEY']
    path = '/data'
else:
    path = os.path.abspath(os.curdir)+'/data'
    app.secret_key = 'your_secret_key'
app.add_url_rule(f'/{path}/<path:filename>', 
                 endpoint='/data', 
                 view_func=lambda filename: send_from_directory(f'{path}', filename))

def allowed_file(filename, extension):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == extension

@app.route('/')
def index():
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
            session['error'] = 'Файлы не выбраны'
            if str(amvera_var) == "1":
                session['error'] = 'Файлы не выбраны!'
            return redirect(url_for('index'))
            
        if file1 and file2:
            if not allowed_file(file1.filename, 'ifc') or not allowed_file(file2.filename, 'ids'):
                session['error'] = 'Недопустимое расширение файлов'
                
            filename1 = file1.filename
            filename2 = file2.filename
            session['file1_path'] = f'{path}/{filename1}'
            session['file2_path'] = f'{path}/{filename2}'
            file1.save(f'{path}/{filename1}')
            file2.save(f'{path}/{filename2}')
            file_names = f'{filename1}, {filename2}'
            session['files_names'] = file_names
    return redirect(url_for('index'))

@app.route('/process', methods=['POST'])
def process():
    session['result_path'] = path
    session.pop('result', None)
    session.pop('html_file_name', None)
    if 'file1_path' not in session or 'file2_path' not in session:
        session['error'] = 'Сначала загрузите файлы'
        return redirect(url_for('index'))
    try:
        result = Ifc_help.check_ifc_file(session['file1_path'], session['file2_path'], f'{path}')
        session['html_file_name'] = result
        session['result'] = result 
        session.pop('error', None)
    except Exception as e:
        session['error'] = f'Ошибка обработки: {str(e)}'
    os.remove(session['file1_path'])
    os.remove(session['file2_path'])

    return redirect(url_for('index'))

@app.route('/download')
def dowload():
    UPLOAD_DIR = f'{path}'
    return send_from_directory(UPLOAD_DIR, session['html_file_name'], as_attachment=True)


if __name__ == '__main__':
    ...
    app.run(debug=True)