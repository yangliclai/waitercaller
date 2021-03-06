from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from flask_login import LoginManager
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user

import config
if config.test:
    from mockdbhelper import MockDBHelper as DBHelper
else:
    from dbhelper import DBHelper

from passwordhelper import PasswordHelper 
from bitlyhelper import BitlyHelper 
from user import User

import datetime

from forms import RegistrationForm
from forms import LoginForm
from forms import CreateTableForm
from forms import ResolveForm

app = Flask(__name__)
app.secret_key = '69hOf+Y7I31vgBx3F5Z5kCwv8t5qyBT3cnV19pzb/mub5ydZCa'
login_manager = LoginManager(app)

DB = DBHelper()
PH = PasswordHelper()
BH = BitlyHelper()

#flagfromtable = 0

# Once your username + pwd first logoin successfully, the backend required you must have "login_manager.user_loader" module to save 1toAll
@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)    

@app.route("/login", methods=["POST"])
def login():
    form = LoginForm(request.form)
    if form.validate():
        stored_user = DB.get_user(form.loginemail.data)
        if stored_user and PH.validate_password(form.loginpassword.data, stored_user['salt'], stored_user['hashed']):
            user = User(form.loginemail.data)
            login_user(user, remember=True)
            return redirect(url_for('account'))
        form.loginemail.errors.append("Email or password invalid")
    return render_template("home.html", loginform=form, registrationform=RegistrationForm())
BitlyHelper()
@app.route("/register", methods=["POST"])
def register():
    form = RegistrationForm(request.form)
    if form.validate():
        if DB.get_user(form.email.data):
            form.email.errors.append("Email address already registered")
            return render_template("home.html", loginform=LoginForm(), registrationform=form)
        salt = PH.get_salt()
        hashed = PH.get_hash(form.password2.data + salt)
        DB.add_user(form.email.data, salt, hashed)
        return render_template("home.html", loginform=LoginForm(), registrationform=form, onloadmessage="Registration successful. Please log in.")
    return render_template("home.html", loginform=LoginForm(), registrationform=form)

'''
    salt = PH.get_salt()
    hashed = PH.get_hash(pw1 + salt)
    DB.add_user(email, salt, hashed)
'''

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

'''
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")
'''

@app.route("/")
def home():
    #return "Under construction"
    #return render_template("home.html")
    #registrationform = RegistrationForm()
    return render_template("home.html", loginform=LoginForm(), registrationform=RegistrationForm())

@app.route("/dashboard")
@login_required
def dashboard():
    now = datetime.datetime.now()
    requests = DB.get_requests(current_user.get_id())
    for req in requests:
        deltaseconds = (now - req['time']).seconds
        req['wait_minutes'] = "{}.{}".format((deltaseconds/60), str(deltaseconds % 60).zfill(2))
    return render_template("dashboard.html", resolvesubmitform=ResolveForm(),requests=requests)

@app.route("/dashboard/resolve")
@login_required
def dashboard_resolve():
    form = ResolveForm(request.form)
    request_id = request.args.get("request_id")
    #if form.validate():
    DB.delete_request(request_id)
    return redirect(url_for('dashboard'))
    #return render_template("dashboard.html", resolvesubmitform=ResolveForm(),requests=DB.get_requests(request_id))

@app.route("/account")
@login_required
def account():
    tables = DB.get_tables(current_user.get_id())
    return render_template("account.html", createtableform=CreateTableForm(), tables=tables)

@app.route("/account/createtable", methods=["POST"])
@login_required
def account_createtable():
    form = CreateTableForm(request.form)
    if form.validate():
        tableid = DB.add_table(form.tablenumber.data, current_user.get_id())
        new_url = BH.shorten_url(config.base_url + "newrequest/" + str(tableid))
        DB.update_table(tableid, new_url) 
            #DB.add_request(tableid, datetime.datetime.now())
            #DB.delete_request_redundancy(tableid) 
        #DB.delete_table_fulltest(tableid02)
        return redirect(url_for('account'))
        # the delete action must in anoter new thread. I try more and fail within the same if form.v..().
    return render_template("account.html", createtableform=form, tables=DB.get_tables(current_user.get_id()))

@app.route("/account/deletetable")
@login_required 
def account_deletetable():
    tableid = request.args.get("tableid")
    DB.delete_table(tableid)
    return redirect(url_for('account'))

@app.route("/newrequest/<tid>")
def new_request(tid):
    count = 0
    #if DB.add_request(tid, datetime.datetime.now(),count):
    if DB.add_request(tid, datetime.datetime.now(),count):
        return "Your request has been logged and a waiter will be with you shortly"
    return "There is already a request pending for this table. Please be patient, a waiter will be there ASAP"
    #return "your id is %s" % str(requestid)
    #request02 = DB.get_request(requestid)
    #DB.update_request(requestid,count=23)
    #request03 = DB.get_request(requestid)
    #count = DB.get_requestcount_max(request02['owner'])
    #DB.update_request(requestid,count)
    #return "your id is %s %s %s %d" % (requestid ,request03['_id'],request03['owner'],int(request03['count']))
    #print "%s %d" %(tittle,blockcode_passed)
    #request02['table_number'] is unicode format

    #return "Your request has been logged and a waiter will be with you shortly"


if __name__ == '__main__':
    app.run(port=5000, debug=True)
