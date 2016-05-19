from app import app,db
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

manage = Manager(app)
migrate = Migrate(app=app, db=db)
manage.add_command('db', MigrateCommand)

@manage.command
def create_admin():
    from app import models
    email = input('Please input your email:')
    password = input('Please input your password:')
    nickname = input('Please input your nickname:')
    admin = models.User(email,password,nickname,2)
    models.db.session.add(admin)
    models.db.session.commit()

if __name__ == '__main__':
    manage.run()
