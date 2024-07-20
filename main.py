from flask import Flask , render_template , request  , session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.utils import secure_filename
import json
import os
import  math
from datetime import datetime


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER  = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)

mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

# this class deffines the table of database 
class Contact(db.Model):
    # S_no , Name , Email_Address , Ph_no , Message , Date
    S_no = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)               # nullable=False mtlb ki koi bhi value null nahi ki jaa skti
    Email_Address = db.Column(db.String(20),  nullable=False)
    Ph_no = db.Column(db.String(12),  nullable=False)
    Message = db.Column(db.String(120),  nullable=False)
    Date = db.Column(db.String(12),  nullable=True)


class Posts(db.Model):
    S_no = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)             
    slug = db.Column(db.String(21),  nullable=False)
    Content	 = db.Column(db.String(120),  nullable=False)
    Image = db.Column(db.String(12),  nullable=True)  
    Date = db.Column(db.String(12),  nullable=True)    


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
   # posts=posts[]
    page = request.args.get('page')
    if(not  str(page).isnumeric()):
        page = 1
    page=int(page)
    posts = posts[(page-1)*int(params['no_of_posts']) : (page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]
    #pagination logic
    #first page 
    if (page==1):
        prev = "#"
        next = "/?page=" + str( page + 1 )
    # for last  page
    elif(page==last):
        prev = "/?page=" + str( page - 1 )
        next = "#"
    #for middle page
    else:
        prev = "/?page=" + str( page - 1 )
        next = "/?page=" + str( page + 1 )

   
    return render_template('index.html',params=params,posts=posts,prev=prev,next=next)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


@app.route("/about")
def about():
    return render_template('about.html',params=params)


@app.route("/dashboard", methods = ['GET','POST'])
def dashboard():

    if('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html',params=params,posts=posts)

    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if(username == params['admin_user'] and userpass == params['admin_password']):
            #set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html',params=params,posts=posts)

    #REDIRECT TO ADMIN PANEL
    return render_template('login.html',params=params)

@app.route("/edit/<string:S_no>" , methods=['GET', 'POST'])
def edit(S_no):
    if('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            box_Title = request.form.get('Title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            Content = request.form.get('Content')
            Image = request.form.get('Image')
            Date = datetime.now()

            if S_no=='0':
                post=Posts(Title=box_Title,Date=Date,slug=slug,Content=Content,tagline=tagline,Image=Image)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(S_no=S_no).first()
                post.Title = box_Title
                post.Date = Date
                post.slug = slug
                post.Content = Content
                post.tagline = tagline
                post.Image = Image
                db.session.commit()
                return redirect('/edit/'+  S_no)
        post = Posts.query.filter_by(S_no=S_no).first()
        return render_template('edit.html',params=params,post=post)

@app.route("/uploader", methods=["GET","POST"])        #for uploading files
def uploader():
    if('user' in session and session['user'] == params['admin_user']):
        if (request.method=='POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'] , secure_filename(f.filename)))
            return "File Upload Successfully"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:S_no>" , methods=['GET', 'POST'])
def delete(S_no):
    if('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(S_no = S_no).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route("/contact", methods=["GET","POST"])
def contact():
    if(request.method=='POST'):
       
        # Add entry to the database
       name = request.form.get('name')
       email = request.form.get('email')
       phone = request.form.get('phone')
       message = request.form.get('message')
        # S_no , Name , Email_Address , Ph_no , Message , Date
       entry= Contact(Name=name , Email_Address=email ,  Ph_no=phone , Message=message , Date = datetime.now() )
       db.session.add(entry)
       db.session.commit()
       mail.send_message('new message from ' + name,
                         sender=email,
                         recipients=[params['gmail-user']],
                         body = message + "\n" + phone
                        )
    
    return render_template('contact.html',params=params)

app.run(debug=True)


# 'mysql://username:password@localhost/db_name'