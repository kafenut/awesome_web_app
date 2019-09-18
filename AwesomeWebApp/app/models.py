#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import db,app
from hashlib import md5

Follow=db.Table('Follow',
     db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
     db.Column('followed_id',db.Integer,db.ForeignKey('user.id'))
    )

class Blog(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    upload_time=db.Column(db.DateTime)
    last_cmmt_time=db.Column(db.DateTime)
    like_num=db.Column(db.Integer,default=0)
    title=db.Column(db.String(50))
    body=db.Column(db.String(500))
    cmmts=db.relationship('Comment',backref='to_blog',lazy='dynamic')
    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    sub_cmmts=db.relationship('Sub_Comment',backref='to_blog',lazy='dynamic')
    #author=db.relationship('User',backref='blogs')

    def __repr__(self):
        return 'Class Blog: author is '+self.author.nickname

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    nickname=db.Column(db.String(60),index=True,unique=True)
    email=db.Column(db.String(144),index=True,unique=True)
    tel_num=db.Column(db.String(20),index=True,unique=True)
    passwd=db.Column(db.String(32),index=True)
    about_me=db.Column(db.String(256))
    last_seen=db.Column(db.DateTime)
    avatar=db.Column(db.String(500))
    blogs=db.relationship('Blog',backref='author',lazy='dynamic')
    cmmts=db.relationship('Comment',backref='author',lazy='dynamic')
    sub_cmmts=db.relationship('Sub_Comment',backref='author',lazy='dynamic')
    followeds=db.relationship('User',
                             secondary=Follow,
                             primaryjoin=(Follow.c.follower_id==id),
                             secondaryjoin=(Follow.c.followed_id==id),
                             backref=db.backref('followers',lazy='dynamic'),
                             lazy='dynamic'
                             )
    #followers: join=(Follow.c.followed_id=id)

    def is_following(self,user):
        return self.followeds.filter(Follow.c.followed_id == user.id).count()>0

    def follow(self,user):
        if not self.is_following(user):
            self.followeds.append(user)
            return self
        return None

    def unfollow(self,user):
        if self.is_following(user):
            self.followeds.remove(user)
            return self
        return None

    @property
    def followed_blogs(self):
        return Blog.query.join(Follow,(Follow.c.followed_id==Blog.author_id)).filter(Follow.c.follower_id==self.id).order_by(Blog.upload_time.desc())

    def get_avatar(self,size):
        return self.avatar

    def avatar1(self,size):
        return 'http://www.gravatar.com/avatar/'+md5(self.email.encode('utf-8')).hexdigest()+'?d=mm&s='+str(size)
    
    def __repr__(self):
        return 'Class User: '+self.nickname

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return True

    def get_id(self):
        return self.id




class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    upload_time=db.Column(db.DateTime)
    like_num=db.Column(db.Integer,default=0)
    body=db.Column(db.String(500))
    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    #author=db.relationship('User',backref='cmmts')
    to_blog_id=db.Column(db.Integer,db.ForeignKey('blog.id'))
    sub_cmmts=db.relationship('Sub_Comment',backref='under_cmmt',lazy='dynamic')

    def __repr__(self):
        return 'Class Comment: author is '+self.author.nickname

class Sub_Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    upload_time=db.Column(db.DateTime)
    like_num=db.Column(db.Integer,default=0)
    body=db.Column(db.String(500))
    to_cmmt_id=db.Column(db.Integer)
    to_blog_id=db.Column(db.Integer,db.ForeignKey('blog.id'))
    #to_blog=db.relationship('Blog',backref='sub_cmmts')
    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    #author=db.relationship('User',backref='sub_cmmts')
    under_cmmt_id=db.Column(db.Integer,db.ForeignKey('comment.id'))
    #under_cmmt=db.relationship('Comment',backref='cmmts')
    
    @property
    def to_cmmt(self):
        if self.to_cmmt_id is None:
            return None
        return Sub_Comment.query.filter_by(id=self.to_cmmt_id).first()
    
    def __repr__(self):
        return 'Class Sub_Comment : author is ' +self.author.nickname
    

    




