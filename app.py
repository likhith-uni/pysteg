from flask import Flask,request,redirect,url_for,flash,render_template,send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
import subprocess

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
OUTPUT = os.path.join(os.getcwd(), "output")
IMAGES = os.path.join(UPLOAD_FOLDER,'img')
TEXTS = os.path.join(UPLOAD_FOLDER,'txt')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/",methods=["GET","POST"])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No cover file submitted")
            return redirect(url_for('index'))
        if 'to_hide' not in request.files:
            flash("No embed file submitted")
            return redirect(url_for('index'))
        file = request.files['file']
        to_hide = request.files['to_hide']
        if file.filename == "" or to_hide.filename == "":
            flash("No selected file")
            return redirect(url_for('index'))
        if file and allowed_file(file.filename) and to_hide:
            ext = file.filename.split('.')[-1]
            id = str(uuid.uuid4())
            filename = id+"."+ext
            ###########################
            #Save temp files
            file.save(os.path.join(IMAGES,filename))
            to_hide.save(os.path.join(TEXTS,id+".txt"))
            ############################
            #Hide file
            os.chdir(os.path.join(os.getcwd(), "output"))
            subprocess.run(['steghide','embed','-ef',"../uploads/txt/"+id+".txt","-cf","../uploads/img/"+filename,"-sf",filename,"-p","1234"])
            return redirect(url_for('download_file', name=filename))
    return render_template('index.html')

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(OUTPUT, name)

if __name__ == "__main__":
    app.run(
        debug=True,
        host = "0.0.0.0",
        port = 8000
    )