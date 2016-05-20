from app import db
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

#role[(0,'未审核'),(1,'已审核'),(2,'管理')]
ROLE = 0

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    nickname = db.Column(db.String(80))
    role = db.Column(db.SmallInteger, default=ROLE)
    lives = db.relationship('Live', backref='user', lazy='dynamic')

    def __init__(self, email, password, nickname, role):
        self.email = email
        self.password = generate_password_hash(password)
        self.nickname = nickname
        self.role = role

    def is_admin(self):
        return True if self.role == 2 else False

    def is_passed(self):
        return True if self.role >= 1 else False

    @classmethod
    def get(cls,id):
        u = cls.query.get(id)
        return u

    @classmethod
    def add(cls, email, password, nickname):
        u = cls(email, password, nickname,None)
        db.session.add(u)
        db.session.commit()
        return u.id

    @classmethod
    def delete(cls, id):
        s = cls.get(id)
        db.session.delete(s)
        db.session.commit()

    @classmethod
    def update(cls, user_dict):
        s = cls.get(user_dict['id'])
        s.password = generate_password_hash(
            user_dict['password']) if 'password' in user_dict else s.password
        s.nickname = user_dict['nickname'] if 'nickname' in user_dict else s.nickname
        s.role = user_dict['role'] if 'role' in user_dict else s.role
        db.session.commit()

    @classmethod
    def list(cls, id=None, email=None):
        if id is not None:
            s = cls.get(id)
        elif email is not None:
            s = cls.query.filter_by(email = email).first()
        else:
            s = cls.query.all()
        return s

    @classmethod
    def login(cls, email, password):
        s = cls.query.filter_by(email = email).first()
        if s is None:
            return False, "邮箱不存在"
        elif not check_password_hash(s.password, password):
            return False, "密码不正确!"
        else:
            return s, "你已成功登录!"

    def __repr__(self):
        return '<User %r>' % self.email


class Live(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    aid = db.Column(db.String(32))
    name = db.Column(db.String(120))
    roomid = db.Column(db.String(120))

    def __init__(self, uid, aid,name,roomid):
        self.uid = uid
        self.aid = aid
        self.name = name
        self.roomid = roomid

    @classmethod
    def add(cls, uid, aid,name,roomid):
        l = cls(uid, aid,name,roomid)
        db.session.add(l)
        db.session.commit()
        return l.id

    @classmethod
    def update(cls,id,name = None,roomid=None):
        l = cls.query.get(id)
        if name:
            l.name = name
        if roomid:
            l.roomid = roomid
        db.session.commit()

    @classmethod
    def delete(cls, id):
        l = cls.query.get(id)
        db.session.delete(l)
        db.session.commit()

    @classmethod
    def list(cls, id=None, uid=None, aid=None):
        if id is not None:
            s = cls.query.get(id)
        elif uid is not None:
            s = cls.query.filter_by(uid = uid)
        elif aid is not None:
            s = cls.query.filter_by(aid = aid).first()
        else:
            s = cls.query.all()
        return s
