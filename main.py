import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import pymongo
import dns # required for connecting with SRVt
import map_creator


ALLOWED_EXTENSIONS = {'json'}


client = pymongo.MongoClient("mongodb+srv://dbUser:K3aCVDqGjoP9v5U8@themap.74csp.mongodb.net/mapdata?retryWrites=true&w=majority")
datas = client.mapdata.datas


app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xaa2K\xb4\xc6*\x94u#*\x05\xb1\x9ds\x86\xc6\xde\x05\xb8i\two\x0f' #隨機亂碼
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

"""
@app.route('/')
def index():
    return render_template('index.html')
"""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def delete_hour_ago():
    hour_ago = (datetime.now()-timedelta(hours=1)).strftime('%Y%m%d %H%M%S')
    condition = list(hour_ago.split())
    datas.delete_many( { 'date' : { '$lt' : int(condition[0]) } } )
    datas.delete_many( { 'time' : { '$lt' : int(condition[1]) } } )
    

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global datas
    # 刪除過期資料
    delete_hour_ago()
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('找不到檔案資料')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('未選擇任何檔案')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)
            content = file.read().decode('utf-8')
            result = map_creator.generate_map(content)
            the_date = int(datetime.today().strftime('%Y%m%d'))
            the_time = int(datetime.now().strftime('%H%M%S'))
            data_id = str(datetime.now().strftime('%Y%m%d%H%M%S%f'))
            save_data = { 'content' : result , 'date' : the_date , 'time' : the_time , 'id' : data_id }
            datas.insert_one(save_data)
            return redirect(f'/result/{data_id}')
        #redirect(url_for('uploads', filename=filename))
    return render_template('index.html')


@app.route('/result/<id>')
def complete_file(id):
    global datas
    # 刪除過期資料
    delete_hour_ago()
    thing = datas.find_one({'id': id })
    #return thing['content']
    return render_template('result.html', content=thing['content'] )



if __name__=='__main__':
    app.run()
