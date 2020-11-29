import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import datetime
import pymongo
import dns # required for connecting with SRVt
import map_creator


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'json'}


client = pymongo.MongoClient("mongodb+srv://dbUser:K3aCVDqGjoP9v5U8@themap.74csp.mongodb.net/mapdata?retryWrites=true&w=majority")
data = client.mapdata.datas


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

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            result = map_creator.generate_map( None )
            the_time = datetime.today().strftime(%Y%m%d%H%M%S%f)
            #save_data = { content : os.path.join(app.config['UPLOAD_FOLDER'], filename) , time : the_time }
            return redirect('/uploads/'+filename)
        #redirect(url_for('uploads', filename=filename))
    return render_template('index.html')

'''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
'''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



if __name__=='__main__':
    app.run()
