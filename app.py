from flask import Flask,jsonify,render_template,request,redirect, session
from flask_sqlalchemy  import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, login_required, UserMixin, logout_user
import requests, os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.secret_key = "super secret key3333"


login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True ) 
    email = db.Column(db.String(30),  unique=True )     

def create_db():
    try:
        db.create_all()
        user = User(id=1,username='admin',email='admin@mail.ru')
        guest = User(id=2,username='guest',email='maksimdaubert@gmail.com')
        db.session.add(user)
        db.session.add(guest)
        db.session.commit()
    except:
        None

#Отвечает за сессию пользователей. Запрещает доступ к роутам, перед которыми указано @login_required
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/healthcheck")
def api():
    json_out=[{'status':'started'}]
    return jsonify(json_out), 200

@app.route("/")
@login_required
def index():
    text='Привет мир!'
    return render_template('index.html',txt=text)

@app.route('/users/<page>', methods=['GET']) 
@login_required
def get_run_requests_page(page):
    response=requests.get('https://reqres.in/api/users?page='+page)
    txt=response.json()
    pages=int(txt['total_pages'])
    txt=txt['data']
    return render_template('get.html',out_json=txt,pages=pages)

@app.route('/form',methods=['GET','POST'])
@login_required
def form():
    text=''
    if request.method == 'POST' :
        text = request.form.get('input_text')
    return render_template('form.html',text=text)

@app.route('/admin',methods=['GET','POST']) 
@login_required
def admin():
    if current_user.username != 'admin':
        return redirect('/')
    name = email =''
    if request.method == 'POST' :
        name = request.form.get('name')
        email = request.form.get('email')
        try:
            user = User(username=name,email=email)
            db.session.add(user)
            db.session.commit()
        except:
            return('При добавлении пользователя произошла ошибка')
    users = User.query.all()
    return render_template('admin.html',users=users,name=name,email=email)

@app.route('/admin/deleteUser/<id>',methods=['POST']) 
@login_required
def admin_del(id):
    if current_user.username != 'Максим Дауберт':
        return redirect('/')
    if request.method == 'POST' :
        try:
            user = User.query.get(int(id))
            db.session.delete(user)
            db.session.commit()
        except:
            return('При удалении пользователя произошла ошибка')
    users = User.query.all()
    return redirect('/')

    
@app.route('/logout') ## button logout
@login_required
def logout():
    session.pop(current_user.username, None)
    logout_user()
    return redirect("/") 

@app.route('/login', methods=['GET','POST'])
def login():
    txt= user =''
    if request.method == 'POST' :
        inputEmail= request.form.get('inputEmail')
        try:
            session.pop(current_user.username, None)
        except:
            user = User.query.filter_by(email=inputEmail).first()
        if user:
            login_user(user)
            next = request.args.get('next')
            return redirect(next)
        else:
            txt = 'доступ закрыт: '+str(user)
    return render_template('login.html',txt=txt)

if __name__ == "__main__":
    app.run(debug=True)