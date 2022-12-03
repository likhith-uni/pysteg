from flask import Flask,request,redirect,url_for,flash,render_template,send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
import subprocess
import glob

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
OUTPUT = os.path.join(os.getcwd(), "output")
IMAGES = os.path.join(UPLOAD_FOLDER,'img')
EXTRACT = os.path.join(UPLOAD_FOLDER,'temp')

TEXTS = os.path.join(UPLOAD_FOLDER,'txt')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = "asdasdiu3020"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/",methods=["GET","POST"])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No cover file"
        if 'to_hide' not in request.files:
            return "No embed file submitted"
        file = request.files['file']
        to_hide = request.files['to_hide']
        password = request.form['password']
        if file.filename == "" or to_hide.filename == "":
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
            new = str(uuid.uuid4())+"."+ext
            subprocess.run(['steghide','embed','-ef',TEXTS+"/"+id+".txt","-cf",IMAGES+"/"+filename,"-sf",new,"-p",password])
            return send_from_directory(os.getcwd(),new,as_attachment=True)
    return render_template('index.html')


@app.route('/decode',methods=["GET","POST"])
def decode():
    if request.method == "POST":
        if 'file' not in request.files:
            return "No cover file"
        file = request.files['file']
        filename = file.filename
        password = request.form['password']
        id = str(uuid.uuid4())
        os.mkdir(id)
        temp_path = os.path.join(os.getcwd(),id)
        file.save(os.path.join(temp_path,filename))
        new1 = str(uuid.uuid4())+".txt"
        subprocess.run(['steghide','extract','-sf',os.path.join(temp_path,filename),"-xf",new1,"-p",password])
        if not os.path.exists(os.path.join(os.getcwd(),new1)):
            flash('Invalid Password')
            return redirect(url_for('decode'))
        return send_from_directory(os.getcwd(),new1,as_attachment=True)
    return render_template('decode.html')
        

if __name__ == "__main__":
    app.run(
        debug=True,
        host = "0.0.0.0",
        port = 8000
    )