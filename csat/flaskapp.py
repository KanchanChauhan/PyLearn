import re
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack, jsonify
from flask_mail import Mail, Message, smtplib
from pdfs import create_pdf


# create application
app = Flask(__name__)

app.config.from_object('config')

#Mail server configuration 
app.config.update(MAIL_SERVER='smtp.gmail.com')
mail = Mail(app)

def init_db():
    #Creates the database tables.
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    #Opens a new database connection if there is none yet for the current application context.
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        sqlite_db = sqlite3.connect(app.config['DATABASE'])
        sqlite_db.row_factory = sqlite3.Row
        top.sqlite_db = sqlite_db
    return top.sqlite_db


@app.teardown_appcontext
def close_db_connection(exception):
    #Closes the database again at the end of the request.
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

@app.route('/')
def index():
    #homepage
    return render_template('get_score.html')


@app.route('/_calculate_avg')
def calculate_avg():
    #AJAX request : calculate average score and returns json response
    quality_score = request.args.get('quality_score', 0, type=int)
    value_score = request.args.get('value_score', 0, type=int)
    purchase_exp_score = request.args.get('purchase_exp_score', 0, type=int)
    usage_exp_score = request.args.get('usage_exp_score', 0, type=int)
    return jsonify(result=(quality_score + value_score + purchase_exp_score + usage_exp_score)/4)

@app.route('/get_feedback', methods=['POST'])
def get_feedback():
    error = None
    #Check if average score is empty
    if eval(request.form['avg_score']) == 0 :
        error = 'Average not calculated, Please make your selection!!'
        return render_template('get_score.html', error=error)
    else:    
        return render_template('get_feedback.html', avg_score=eval(request.form['avg_score']))


@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    return render_template('get_attr_importance.html', avg_score=eval(request.form['avg_score']), feedback = request.form['feedback']) 


@app.route('/save_attr_importance', methods=['POST'])
def save_attr_importance():
    #Saves the data to database
    error = None
    #Check if radio button selected
    if not request.form.get('quality_imp', '') or not request.form.get('value_imp', '') or not request.form.get('purchase_imp', '') or not request.form.get('usage_imp', ''):
        error = 'Please make your selection!!'
        return render_template('get_attr_importance.html', error=error)
    db = get_db()
    db.execute('insert into entries (quality_imp, value_imp, purchase_imp, usage_imp, avg_score, feedback) values (?, ?, ?, ?, ?, ?)',
        [request.form['quality_imp'], request.form['value_imp'], request.form['purchase_imp'], request.form['usage_imp'], request.form['avg_score'], request.form['feedback']])
    db.commit()
    return redirect(url_for('show_report'))                  

@app.route('/report')
def show_report():
    db = get_db()
    cur = db.execute('select quality_imp, value_imp, purchase_imp, usage_imp, avg_score, feedback from entries order by id desc')
    entries = cur.fetchall()
    return render_template('report.html', entries=entries)

@app.route('/report_temp',methods=['POST'])
def send_report():
    #Saves the report as PDF in root folder, send out the report as attachment in mail
    error = None
    db = get_db()
    cur = db.execute('select quality_imp, value_imp, purchase_imp, usage_imp, avg_score, feedback from entries order by id desc')
    entries = cur.fetchall()
    email_id = request.form['email_id']
    # Validate the email address
    if not email_id or not is_email_address_valid(email_id):
        error = "Please enter a valid email address"
        return render_template('report.html', error=error)
    else:    
        create_pdf(render_template('report_temp.html', entries=entries))
        msg = Message('Hello',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[email_id])
        msg.body = "Please find your Product Satisfactory Report in attachment."
        with app.open_resource("test.pdf") as fp:
            msg.attach("file.pdf", "application/pdf", fp.read())
        mail.send(msg)
        return render_template('report.html', entries=entries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return render_template('get_score.html', error=error)
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

def is_email_address_valid(email):
    """Validate the email address using a regex."""
    if not re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", email):
        return False
    return True    

#Run app
if __name__ == '__main__':
    init_db()
    app.run()
