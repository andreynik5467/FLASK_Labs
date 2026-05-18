import os
from flask import Flask, request, send_from_directory, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import hashlib
import uuid
import json
from datetime import datetime
from FLASK_Labs.flask2_lab.flask2_lab.utils import load_json, save_json
app = Flask(__name__)

# Настройки
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Максимум 16 МБ
app.secret_key = os.urandom(256)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def loaddata(user_dct, ogdata, uuid):
        base_path = "bdofdata"
        
        
        if not ogdata :
            return 0
        else:
    
            data = ogdata.encode('utf-8')
            md5_hash = hashlib.md5(data).hexdigest()
            for i in user_dct:
                if md5_hash in user_dct[i]["hashed"]:
                    print("Text already in the file! Try again!")
                    return 1
            new_hash = {
                "UUID": uuid,
                "org": ogdata,
                "hashed": md5_hash,
                "date": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            ids = str(len(user_dct) + 1)
            user_dct[ids] = new_hash
            save_json(base_path, "bdofdata.json", user_dct)

        #print(data)
        #print(md5_hash)
        
#print("That`s what is already in the file: ")
#for i in user_dct:
 #   print(user_dct[i]["org"], "-" , user_dct[i]["hashed"])
    #print(user_dct[i]["hashed"])
#ogdata = input("Input your text here:")

@app.route('/', methods=['GET'])
def index():
    user_dct = load_json("bdofdata", "bdofdata.json")
    return render_template('index.html', files=user_dct, upload_dir="bdofdata")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """ Предпросмотр файлов из папки uploads"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or request.files['file'].filename == '':
        flash('Файл не выбран', 'error')
        return redirect(url_for('index'))

    file = request.files['file']
    
    if not allowed_file(file.filename):
        flash('Недопустимый формат файла', 'error')
        return redirect(url_for('index'))

    # 1. Генерируем безопасное имя и UUID для записи
    file_uuid = str(uuid.uuid4())
    safe_name = secure_filename(file.filename)
    ext = safe_name.rsplit('.', 1)[1].lower()
    uuid_name = f"{file_uuid}.{ext}"

    # 2. Загружаем текущую базу
    user_dct = load_json("bdofdata", "bdofdata.json")
    
    # 3. Считаем хеш (опционально: хешируем имя или содержимое)
    md5_hash = hashlib.md5(safe_name.encode('utf-8')).hexdigest()

    # 4. Проверяем дубликаты ПО ИМЕНИ (или по хешу содержимого, если нужно)
    for i in user_dct:
        if user_dct[i]["hashed"] == md5_hash:
            flash(f'Файл "{safe_name}" уже был загружен!', 'warning')
            return redirect(url_for('index'))
            
    # 5. Сохраняем файл на диск
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], uuid_name)
    file.save(filepath)
    

    #loaddata(user_dct, safe_name, uuid)
    # 6. Добавляем запись в словарь и сохраняем JSON
    user_dct[file_uuid] = {
        "UUID": file_uuid,
        "org": safe_name,
        "hashed": md5_hash,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M")

    }
    save_json("bdofdata", "bdofdata.json", user_dct)
    
    flash(f'Файл "{safe_name}" успешно загружен!', 'success')
    return redirect(url_for('index'))
#L
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='127.0.0.1', port=5000)