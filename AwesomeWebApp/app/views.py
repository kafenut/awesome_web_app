#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app,db,login_manager
from flask import render_template,flash,redirect,session,url_for,g,request
from flask_login import login_required,login_user,logout_user,current_user
from datetime import datetime
from app.models import User,Blog,Comment,Sub_Comment
from config import BLOGS_PER_PAGE,UPLOAD_FOLDER
from app.function import valid_profile
from werkzeug import secure_filename

import json,os


@app.route('/')
@app.route('/index')
def index():
    if not g.user.is_authenticated: 
        blogs=Blog.query.order_by(Blog.upload_time.desc()).limit(5)
    else:
        blogs=Blog.query.filter_by(author=g.user).order_by(Blog.upload_time.desc()).limit(5)
    return render_template('index.html',blogs=blogs)

@app.route('/blog_page',methods=['GET','POST'])
def blog_page():
    id=request.args.get('id')
    if id:
        id=int(id)
    blog=Blog.query.filter_by(id=id).first() 
    if blog is None:
            flash('No such blog!')
            return redirect('/index')
    if request.method=='GET':                          
        return render_template('blog_page.html',blog=blog)
    
    if g.user is None: #if method==POST(receiving a commnet)
        flash('You need to log in to commend!')
        return render_template('index')
    Get=request.form.get
    if not Get('under_cmmt_id'):   #if it is a comment to blog
        cmmt=Comment(to_blog=blog,body=Get('body'),upload_time=datetime.utcnow(),author=g.user)
    else:
        under_cmmt=Comment.query.filter_by(id=Get('under_cmmt_id')).first()
        if under_cmmt is None:
            flash('No such comment!')
            return redirect('/index')
        if Get('to_cmmt_id'):
            cmmt=Sub_Comment(under_cmmt=under_cmmt,to_blog=blog,to_cmmt_id=Get('to_cmmt_id'),body=Get('body'),upload_time=datetime.utcnow(),author=g.user)
        else:
            cmmt=Sub_Comment(under_cmmt=under_cmmt,to_blog=blog,body=Get('body'),upload_time=datetime.utcnow(),author=g.user)
    db.session.add(cmmt)
    db.session.commit()
    flash('Comment successfully!')
    return redirect(url_for('blog_page')+'?id='+str(id))

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    Get=request.form.get
    if User.query.filter_by(email=Get('email')).first():
        flash('The email has been registered!')
        return redirect(url_for('register'))
    elif User.query.filter_by(nickname=Get('nickname')).first():
        flash('This nickname has been registered!')
        return redirect(url_for('register'))
    else:
        user=User(nickname=Get('nickname'),email=Get('email'),passwd=Get('passwd'),about_me=Get('about_me'))
        db.session.add(user)
        db.session.commit()
        flash('Register successfully!')
        login_user(user)
        return redirect(url_for('index'))

@login_required
@app.route('/write_blog',methods=['GET','POST'])
def write_blog():
    if request.method=='GET':
        return render_template('write_blog.html')
    Get=request.form.get
    blog=Blog(title=Get('title'),body=Get('body'),author=g.user,upload_time=datetime.utcnow(),last_cmmt_time=datetime.utcnow())
    db.session.add(blog)
    db.session.commit()
    flash('Your blog is successfully uploaded!')
    return redirect(url_for('index'))


@login_required
@app.route('/like_blog',methods=['POST',])
def like_blog():
    data=json.loads(request.get_data())
    resp={'success':False}
    if data['type']=='blog':
        obj=Blog.query.filter_by(id=data['id']).first()
    elif data['type']=='cmmt':
        obj=Comment.query.filter_by(id=data['id']).first()
    else:
        obj=Sub_Comment.query.filter_by(id=data['id']).first()
    
    if data['title']!='like_blog':
        resp['text']='Bad data!'
    elif obj is None:
        resp['text']='No such object!'
    elif data['like']==True:
        obj.like_num+=1
        db.session.add(obj)
        db.session.commit()
        resp['success']=True
    else:
        obj.like_num-=1
        db.session.add(obj)
        db.session.commit()
        resp['success']=True
    return json.dumps(resp)       

#user
@app.route('/user/<nickname>')
def user(nickname):
    user=User.query.filter_by(nickname=nickname).first()
    return render_template('user.html',user=user)

@app.route('/user/<nickname>/blogs')
def blogs(nickname):
    user=User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('Can\'t find user '+nickname+' !')
        return redirect(url_for('index'))
    page=int(request.args.get('page',default=1))
    blogs=Blog.query.filter_by(author=user).order_by(Blog.upload_time.desc()).paginate(page,BLOGS_PER_PAGE,False)  #a paginate object
    return render_template('blogs.html',blogs=blogs,user=user)

@login_required
@app.route('/user/<nickname>/edit',methods=['POST','GET'])
def edit(nickname):
    user=User.query.filter_by(nickname=nickname).first()
    if user!=g.user:
        flash('You have no privilege to access this page!')
        return render_template('index.html')
    if request.method=='GET':
        return render_template('edit.html',user=user)
    
    else:   #when receiving a post
        file=request.files.get('avatar')
        if file and valid_profile(file.filename):
            filename=g.user.nickname+'_id='+str(g.user.id)+ '.'+file.filename.rsplit('.',1)[1]            
            pathname=os.path.join(UPLOAD_FOLDER,filename)
            file.save(pathname)
            user.avatar=pathname[5:]
            print(user.avatar)
        Get=request.form.get
        user.email=Get('email')
        user.tel_num=Get('tel_num')
        user.about_me=Get('about_me')
        db.session.add(user)
        db.session.commit()
        flash('edit successfully!')
        return redirect(url_for('edit',nickname=g.user.nickname))

#api
@app.route('/api')
def api():
    return render_template('api.html')

@app.route('/api/user')
def api_get_user():
    id=request.args.get('id')
    nickname=request.args.get('nickname')
    resp=dict(theme='api_get_user')
    
    if id is not None:
        id=int(id)
        user=User.query.filter_by(id=id).first()
    elif nickname is not None:
        user=User.query.filter_by(nickname=nickname).first()
    else:
        resp['success']=False
        resp['reason']='No arguments were given'
    
    if not user:    #No such user
        resp['success']=False
        resp['reason']='No such user'
    else:
        resp['success']=True
        resp['user']=dict(nickname=user.nickname,tel_num=user.tel_num,about_me=user.about_me,follower_num=user.followers.count(),followed_num=user.followeds.count(),blog_num=user.blogs.count(),last_seen_utc=str(user.last_seen))    
    return json.dumps(resp)

@app.route('/api/blogs')
def api_get_blogs():
    nickname=request.args.get('author')
    user=User.query.filter_by(nickname=nickname).first()
    resp=dict(theme='blogs')

    if user is None:
        resp['success']=False
        resp['reason']='No such user'
    else:
        resp['success']=True
        i=1
        blogs=dict()
        for blog in user.blogs.order_by(Blog.upload_time.desc()):
            blogs['blog'+str(i)]=dict(id=blog.id,author=blog.author.nickname,like_num=blog.like_num,cmmt_num=blog.cmmts.count()+blog.sub_cmmts.count(),upload_time=str(blog.upload_time),title=blog.title,body=blog.body)
            i=i+1
        resp['blogs']=blogs
    return json.dumps(resp)

@app.route('/api/blog_page')
def api_get_blog_page():
    id=request.args.get('id')
    resp=dict(theme='blog_page')

    if id is not None:
        id=int(id)
        blog=Blog.query.filter_by(id=id).first()
    else:
        resp['success']=False
        resp['reason']='No arguments were given'

    if not blog:
        resp['success']=False
        resp['reason']='No such blog'
    else:
        resp['success']=True
        obj=dict(author=blog.author.nickname,like_num=blog.like_num,cmmt_num=blog.cmmts.count()+blog.sub_cmmts.count(),upload_time=str(blog.upload_time),last_cmmt_time=str(blog.last_cmmt_time),title=blog.title,body=blog.body)
        i=1
        for cmmt in blog.cmmts.order_by(Comment.upload_time.asc()):
            comment=dict(author=cmmt.author.nickname,like_num=cmmt.like_num,cmmt_num=cmmt.sub_cmmts.count(),upload_time=str(cmmt.upload_time),body=cmmt.body)
            j=1
            for sub_cmmt in cmmt.sub_cmmts.order_by(Sub_Comment.upload_time.asc()):
                sub_comment=dict(author=sub_cmmt.author.nickname,like_num=cmmt.like_num,upload_time=str(sub_cmmt.upload_time),body=sub_cmmt.body)
                if sub_cmmt.to_cmmt is None:   #if it is a wild sub_cmmt
                    sub_comment['to_whom']='None'
                else:
                    sub_comment['to_whom']=sub_cmmt.to_cmmt.author.nickname
                comment['sub_cmmt'+str(j)]=sub_comment
                j=j+1
            obj['cmmt'+str(i)]=comment
            i=i+1
        resp['blog']=obj
    return json.dumps(resp)

#login management
@app.route('/login',methods=['POST',])
def login():
    if g.user and g.user.is_authenticated:
        flash('You have already logged in !')
        return redirect(url_for('/'))
    data=json.loads(request.get_data())
    resp=dict(success=False)
    if data['title']!='login':
        resp['text']='Bad data !'
        return json.dumps(resp)
    user=User.query.filter_by(email=data['email']).first()
    if user is None:
        resp['text']='Invalid email !'
    elif user.passwd!=data['passwd']:
        print(user.passwd,data['passwd'])
        resp['text']='Wrong password !'
    else:
        login_user(user)
        flash('Login successfully !')
        resp['success']=True
        resp['text']='Login successfully !'
    return json.dumps(resp)

@app.route('/logout')
def logout():
    if not g.user.is_authenticated:
        flash('You have not logged in yet !')
        return redirect(url_for('index'))
    logout_user()
    flash('Logout successfully !')
    return redirect(url_for('index'))

@app.before_request
def before_request():
    g.user=current_user
    if g.user.is_authenticated:
        g.user.last_seen=datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
    return None

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))



