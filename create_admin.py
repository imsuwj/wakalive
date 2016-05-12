from app import models
email = input('请输入邮箱')
password = input('请输入密码')
nickname = input('请输入昵称')
admin = models.User(email,password,nickname,2)
models.db.session.add(admin)
models.db.session.commit()
