#!/usr/bin/env python3

from flask import Flask, jsonify, request,redirect
from flask_mongoengine import MongoEngine
from flask_basicauth import BasicAuth
from datetime import datetime
import shortuuid
from flask_admin import Admin,BaseView,expose
from flask_admin.contrib.mongoengine import ModelView
from flask_login import current_user, LoginManager,UserMixin
from flask_babelex import Babel
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'todo',
    'host': 'localhost',
    'port': 27017
}
app.config['SECRET_KEY'] = 'test'
db = MongoEngine()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
admin = Admin(name="jiasule",url='/admin',template_mode="bootstrap3")
admin.init_app(app)

app.config['BASIC_AUTH_USERNAME'] = 'test'
app.config['BASIC_AUTH_PASSWORD'] = 'test'
basic_auth = BasicAuth(app)

babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'


class Task(db.Document):
    task_id = db.StringField(required=True)
    name = db.StringField(required=True, max_length=50)
    cname = db.StringField(required=True, max_length=1000)
    ip = db.StringField(required=True, max_length=1000)
    createtime = db.DateTimeField(required=True)

    def to_json(self):
        return {
            "task_id": self.task_id,
            "name": self.name,
            "cname": self.cname,
            "ip": self.ip,
            "createtime": self.createtime.strftime("%Y-%m-%d %H:%M:%S"),
        }

class User(UserMixin,db.Document):
    name = db.StringField(max_length=40)
    user_id = db.StringField(required=True)
    password = db.StringField(max_length=40)

    def __unicode__(self):
        return self.name


class AdminModelView(ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            return False
        else:
            return True
    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())



#admin.add_view(ModelView(User))
admin.add_view(AdminModelView(Task))


@app.route('/task/add', methods=['POST'])
def postTask():
    if not request.json or not 'task' in request.json:
        return jsonify({'err': 'Request not Json or miss task.'})
    else:
        task = Task(
            task_id=shortuuid.uuid(),
            name=request.json['task'],
            cname=request.json['cname'],
            ip=request.json['ip'],
            createtime=datetime.now()
        )
        task.save()
    return jsonify({'status': 0, 'task_id': task['task_id']})


#@app.route('/task/<task_id>', methods=['GET'])
#def getTask(task_id):
#    task = Task.objects(task_id=task_id).first()
#    if not task:
#        return jsonify({'err': 'Not found.'})
#    else:
#        return jsonify({'status': 0, 'task': task.to_json()})

@app.route('/name/<name>', methods=['GET'])
#@basic_auth.required
def getname(name):
    task = Task.objects(name=name).first()
    if not task:
        return jsonify({'err': 'Not found.'})
    else:
        return jsonify({'status': 0, 'task': task.to_json()})

@app.route('/tasks', methods=['GET'])
@basic_auth.required
def getTasks():
    tasks = Task.objects()
    return jsonify({'status': 0, 'tasks': [task.to_json() for task in tasks]})

@app.route('/task/update/<task_id>', methods=['PUT'])
def putTask(task_id):
    task = Task.objects(task_id=task_id).first()
    if not task:
        return jsonify({'err': 'Not found.'})
    else:
        if 'task' in request.json:
            task.update(name=request.json['task'])
        if 'cname' in request.json:
            task.update(cname=request.json['cname'])
            task.update(cname=request.json['cname'])
        if 'ip' in request.json:
            task.update(ip=request.json['ip'])
        task = Task.objects(task_id=task_id).first()
        return jsonify({'status': 0, 'task': task.to_json()})


@app.route('/task/delete/<task_id>', methods=['DELETE'])
def deleteTask(task_id):
    task = Task.objects(task_id=task_id).first()
    if not task:
        return jsonify({'err': 'Not found.'})
    else:
        task.delete()
        return jsonify({'status': 0, 'task_id': task['task_id']})

@app.route('/',methods=['GET'])
def indexpage():
    return redirect('/admin')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,threaded=True,debug=True)
