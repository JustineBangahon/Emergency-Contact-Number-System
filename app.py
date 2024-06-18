from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
#from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'jaskie123'
#app.permanent_session_lifetime = timedelta(days=5)


db = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    db="emergency_contact_db",
)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect('/')

    error_message = None 

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            flash('Login successful', 'success')
            return redirect('/')
        else:
            error_message = 'Login failed. Please check your credentials.'

    return render_template('login.html', error_message=error_message)

@app.route('/')
def home():
    if 'logged_in' not in session:
        return redirect('/login')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM emergency_contacts")
    contacts = cursor.fetchall()
    return render_template('home.html', contacts=contacts)

@app.route("/index")
def index():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM emergency_contacts")
    contacts = cursor.fetchall()
    return render_template("index.html", contacts=contacts)


@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        ec_name = request.form['ec_name']
        ec_address = request.form['ec_address']
        net_carrier = request.form['net_carrier']
        e_contact_number = request.form['e_contact_number']

        cursor = db.cursor()
        cursor.execute("SELECT * FROM emergency_contacts WHERE e_contact_number = %s", e_contact_number)
        existing_contact = cursor.fetchone()

        if existing_contact:
            flash('Contact number already exists in the database.', 'error')
        else:
            cursor.execute("INSERT INTO emergency_contacts (ec_name, ec_address, net_carrier, e_contact_number) VALUES (%s, %s, %s, %s)",
                           (ec_name, ec_address, net_carrier, e_contact_number))
            db.commit()
    return redirect('/')

@app.route('/update_contact/<int:ec_id>')
def update_contact(ec_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM emergency_contacts WHERE ec_id=%s", ec_id)
    contact = cursor.fetchone()
    return render_template('update_contact.html', contact=contact)

@app.route('/update_contact/<int:ec_id>', methods=['POST'])
def update_contact_post(ec_id):
    if request.method == 'POST':
        ec_name = request.form['ec_name']
        ec_address = request.form['ec_address']
        net_carrier = request.form['net_carrier']
        e_contact_number = request.form['e_contact_number']

        cursor = db.cursor()
        cursor.execute("UPDATE emergency_contacts SET ec_name=%s, ec_address=%s, net_carrier=%s, e_contact_number=%s WHERE ec_id=%s",
                       (ec_name, ec_address, net_carrier, e_contact_number, ec_id))
        db.commit()
    return redirect('/')



@app.route('/delete_contact/<int:ec_id>')
def delete_contact(ec_id):
    return redirect(url_for('confirm_delete_contact', ec_id=ec_id))

@app.route('/confirm_delete_contact/<int:ec_id>')
def confirm_delete_contact(ec_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM emergency_contacts WHERE ec_id=%s", ec_id)
    contact = cursor.fetchone()
    return render_template('confirm_delete.html', contact=contact, ec_id=ec_id)

@app.route('/delete_contact/<int:ec_id>', methods=['POST'])
def delete_contact_confirm(ec_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM emergency_contacts WHERE ec_id=%s", ec_id)
    db.commit()
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out successfully', 'success')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
