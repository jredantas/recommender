# -*- coding: utf-8 -*-
"""
Spyder Editor

Developer: Jose Renato
created in 2017-09-11

"""
#######################################
#####                             #####
#####     Imports section         #####
#####                             #####
#######################################
from flask import Flask, g
from flask import render_template, url_for
from flask import request, session, redirect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects import mysql
from sqlalchemy import func

from passlib.hash import sha256_crypt
import numpy as np
import pandas as pd


from model import Contact, Person
from model import Expense, Account, Income


#######################################
#####                             #####
#####     Config  section         #####
#####                             #####
#######################################
app = Flask(__name__)

app.config.update(dict(
        DATABASE='nobdan',
        DEBUG=True,
        SECRET_KEY='_5#y2L"F4Q8z\n\xec]/A0Zr98j/3yX R~XHH!jmN]LWX/,?RT',
        USERNAME='admin',
        PASSWORD='admin'
    ))

#app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# set the secret key.  keep this really secret:
app.secret_key = app.config.get('SECRET_KEY')

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'+app.config.get('USERNAME')+':'+app.config.get('PASSWORD')+'@localhost:3306/'+app.config.get('DATABASE')

#######################################
#####                             #####
#####     DBA     section         #####
#####                             #####
#######################################

def connect_db(conn_string=SQLALCHEMY_DATABASE_URI):
    """Connects to the specific database."""
    db = create_engine(conn_string)
    db.echo = False
    return db

def init_db():
    """Initializes the database."""
    INIT_DATABASE_URI = 'mysql+pymysql://'+app.config.get('USERNAME')+':'+app.config.get('PASSWORD')+'@localhost:3306/'
    db = get_db(INIT_DATABASE_URI)
    
    Session = sessionmaker(bind=db)
    dbsession = Session()
    print('Create session variable.')

    # Open the .sql file
    sql_file = open('schema.sql','r')
    print('Open schema.sql.')
    # Create an empty command string
    sql_command = ''
    # Iterate over all lines in the sql file
    for line in sql_file:
        # Ignore comented lines
        if not line.startswith('--') and line.strip('\n'):
            # Append line to the command string
            sql_command += line.strip('\n')
            # If the command string ends with ';', it is a full statement
            if sql_command.endswith(';'):
                # Try to execute statemente and commit it
                try:
                    print(sql_command)
                    dbsession.execute(sql_command)
                    dbsession.commit()
                # Assert in case of error
                except Exception as err:
                    print(err)
                # Finally, clear command string
                finally:
                    sql_command = ''

def get_db(conn_string=SQLALCHEMY_DATABASE_URI):
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sql_db'):
        g.sql_db = connect_db(conn_string)
    return g.sql_db

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sql_db'):
        g.sql_db.dispose()


#######################################
#####                             #####
#####   Custom filter section     #####
#####                             #####
#######################################
@app.template_filter('number')
def number_filter(s):
    try:
        float(s)
        return True
    except:
        return False

@app.template_filter('datetime')
def datetime_filter(d): # date = datetime object.
    try:
        d.strftime('%d/%m/%Y')
        return True
    except:
        return False
    
@app.template_filter('sn')
def supress_none_filter(val):
    if not val is None:
        return val
    else:
        return ''

      
#######################################
#####                             #####
#####   Preambule section         #####
#####                             #####
#######################################
@app.route('/')
def accueil():
    if 'username' in session:
       return render_template('accueil.html', titre='Financial web', username=session['username'])
    return render_template('accueil.html', titre='Financial web')

@app.route('/contact')
def contact():
    return render_template('contact.html', titre='Financial web - Contact us')


@app.route('/list/person')
@app.route('/under_construction')
def under_construction():
    return render_template('under_construction.html', titre='Financial web')

@app.route('/show/person/<id>')
@app.route('/remove/person/<id>')
def under_construction_id(id):
    return render_template('under_construction.html', titre='Financial web')
    

#######################################
#####                             #####
#####  AUthentication section     #####
#####                             #####
#######################################
@app.route('/signup')
@app.route('/insert/person')
def signup():
    return render_template('signup.html', titre='Financial web - Sign up')

    
@app.route('/profile')
def profile():
    if len(session) == 0:
        return render_template('accueil.html', titre='Financial Web', alert='User not logged in.')
    return redirect(url_for('under_construction'))
    #return render_template('profile.html', titre='Financial web - User profile')

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['username']
    passwd = request.form['password']
    if request.method == 'POST': # and username == 'admin':
        try:
            db = get_db()
            metadata = MetaData(bind=db)
            Session = sessionmaker(bind=db)
            dbsession = Session()
            table = Table('person', metadata, autoload=True)
            result = dbsession.query(table).filter(table.columns.email == username).first()
            if result is not None:
                if sha256_crypt.verify( passwd, result[4]): 
                    session['username'] = username
                    session['logged_in'] = True
                    return redirect(url_for('accueil'))
        except Exception as err:
            print(err)
            return render_template('accueil.html', titre='Financial Web', alert='It was not possible to retrieve the information. Please try again.')

        
    return render_template('accueil.html', titre='Financial Web', alert='Username or password not correct.')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('logged_in', False)
    return redirect(url_for('accueil'))

#######################################
#####                             #####
#####   Suplementary functions    #####
#####                             #####
#######################################
def get_labels(table):
    columns = []
    columnsStr = ''
    for i, key in enumerate(table.c.keys()):
        columns.append(' '.join(key.split('_')).title())
        columnsStr += key
        if i != len(table.c.keys()) -1:
            columnsStr += ', '
    columns = tuple(columns)
    return columns

def format_date(d):
    d = d.split('/')
    d = str(d[-1]+'-'+d[-2]+'-'+d[0])
    return d

#######################################
#####                             #####
#####   CRUD section              #####
#####                             #####
#######################################
@app.route('/list/<instance>')
def hall(instance):
    if session.get('logged_in') != True:
        return render_template('accueil.html', titre='Financial Web', alert='User not logged in.')
    
    try:
        db = get_db()
        metadata = MetaData(bind=db)
        Session = sessionmaker(bind=db)
        dbsession = Session()
        table = Table(str(instance), metadata, autoload=True)
        labels = get_labels(table)
        result = dbsession.query(table).all()
    except Exception as err:
        print(err)
        return render_template('accueil.html', titre='Financial Web', alert='It was not possible to retrieve the information. Please try again.')
    
    return render_template('list.html', titre='Financial web - '+instance, instance=instance, elements=result, columns=labels)
    
@app.route('/show/<instance>/<id>')
def show(instance, id):
    if session.get('logged_in') != True:
        return render_template('accueil.html', titre='Financial Web', alert='User not logged in.')

    try:
        db = get_db()
        metadata = MetaData(bind=db)
        Session = sessionmaker(bind=db)
        dbsession = Session()
        table = Table(str(instance), metadata, autoload=True)
        labels = get_labels(table)
        result = dbsession.query(table).filter(table.columns.id == id).first()
        elements = zip(labels, result)
    except Exception as err:
        print(err)
        return render_template('accueil.html', titre='Financial Web', alert='It was not possible to retrieve the information. Please try again.')
    
    return render_template('show.html', titre='Financial web - '+instance,  instance=instance, elements=elements)

@app.route('/insert/<instance>')
def insert(instance):
    if session.get('logged_in') != True:
        return render_template('accueil.html', titre='Financial Web', alert='User not logged in.')

    try:
        db = get_db()
        metadata = MetaData(bind=db)
        table = Table(str(instance), metadata, autoload=True)
        labels = get_labels(table)
        primaryKeyColName = table.primary_key.columns.values()[0].name
        labels, columns = zip(*filter(lambda x: primaryKeyColName.title() not in x, zip(labels,table.columns)))
        elements = zip(labels, columns)
    except Exception as err:
        print(err)
        return render_template('accueil.html', titre='Financial Web', alert='It was not possible to retrieve the information. Please try again.')

    return render_template('insert.html', titre='Financial web - '+instance, instance=instance, columns=elements)

@app.route('/remove/<instance>/<id>')
def remove(instance, id):
    if session.get('logged_in') != True:
        return render_template('accueil.html', titre='Financial Web', alert='User not logged in.')

    try:
        db = get_db()
        metadata = MetaData(bind=db)
        Session = sessionmaker(bind=db)
        dbsession = Session()
        table = Table(str(instance), metadata, autoload=True)
        labels = get_labels(table)
        result = dbsession.query(table).filter(table.columns.id == id).first()
        elements = zip(labels, result)
    except Exception as err:
        print(err)
        return render_template('accueil.html', titre='Financial Web', alert='It was not possible to retrieve the information. Please try again.')
    
    
    return render_template('remove.html', titre='Financial web - '+instance, instance=instance, elements=elements)

@app.route('/update/<instance>/<id>')
def update(instance, id):
    if session.get('logged_in') != True:
        return render_template('accueil.html', titre='Financial Web', alert='User not logged in.')
    return render_template('update.html', titre='Financial web - '+instance, section_titre=instance)


#######################################
#####                             #####
#####   Model section             #####
#####                             #####
#######################################
@app.route('/person/insert', methods=['POST'])
def insert_person():
    if request.method == 'POST':
        if request.form['inputPassword1'] != request.form['inputPassword2']:
             return render_template('signup.html', titre='Financial Web', alert='Password fields must be equal. Try again.')

        try:
            db = get_db()
            Session = sessionmaker(bind=db)
            dbsession = Session()
            person = Person(request.form['inputName'], request.form['inputCompany'], request.form['inputEmail'], request.form['inputPassword1'])
            dbsession.add(person)
            dbsession.commit()
            return render_template('accueil.html', titre='Financial Web', alert='User registered. Thank you.')
        except Exception as err:
            print(err)
            return render_template('accueil.html', titre='Financial Web', alert='User not registered. Try again.')

@app.route('/contact/add', methods=['POST'])
def insert_contact():
    if request.method == 'POST':
        try:
            db = get_db()
            Session = sessionmaker(bind=db)
            dbsession = Session()
            contact = Contact(request.form['inputName'], request.form['inputEmail'], request.form['formControlMessage'])
            dbsession.add(contact)
            dbsession.commit()
            return render_template('accueil.html', titre='Financial Web', alert='Contact registered. Thank you.')
        except Exception as err:
            print(err)
            return render_template('accueil.html', titre='Financial Web', alert='Contact not registered. Try again.')

@app.route('/<instance>/add', methods=['POST'])
def insert_add(instance):
    if request.method == 'POST':
        try:

            #recuperar a tabela
            db = get_db()
            metadata = MetaData(bind=db)
            table = Table(str(instance), metadata, autoload=True)
            primaryKeyColName = table.primary_key.columns.values()[0].name
            
            #colocar os dados dos forms correspondentes as colunas
            values = {}
            for column in table.columns:
                if column.name != primaryKeyColName:
                    if request.form[column.name] != '':
                        values[column.name] = request.form[column.name]
                        if isinstance(column.type, mysql.DECIMAL):
                            values[column.name] = float(request.form[column.name]) #datetime.datetime.strftime(datetime.date(request.form[column.name]), '%Y-%m-%d')
                        if isinstance(column.type, mysql.INTEGER):
                            values[column.name] = int(request.form[column.name]) #datetime.datetime.strftime(datetime.date(request.form[column.name]), '%Y-%m-%d')
                        #if isinstance(column.type, mysql.TIMESTAMP):
                        #    values[column.name] = format_date(request.form[column.name]) #datetime.datetime.strftime(datetime.date(request.form[column.name]), '%Y-%m-%d')
                    
            #criar objeto e gravar
            Session = sessionmaker(bind=db)
            dbsession = Session()
            i = table.insert()
            i = i.values(values)
            dbsession.execute(i)
            dbsession.commit()

            # update
            #u = update(mytable)
            #u = u.values({"field3": "new_value"})
            #u = u.where(mytable.c.id == 33)
            #session.execute(u)


            return redirect(url_for('hall', instance=instance))

        except Exception as err:
            print(err)
            return render_template('accueil.html', titre='Financial Web', alert='It was not possible to insert the record. Try again.')

@app.route('/<instance>/remove', methods=['POST'])
def remove_save(instance):
    if request.method == 'POST':
        
        try:
            
            db = get_db()
            metadata = MetaData(bind=db)
            Session = sessionmaker(bind=db)
            dbsession = Session()
            table = Table(str(instance), metadata, autoload=True)
            i = table.delete(table.c.id == request.form['id'])
            dbsession.execute(i)
            dbsession.commit()

            return redirect(url_for('hall', instance=instance))

        except Exception as err:
            print(err)
            return render_template('accueil.html', titre='Financial Web', alert='It was not possible to insert the record. Try again.')


if __name__ == '__main__':

    #app.run(host='0.0.0.0', port=8080, debug=True)
    app.run(debug=True)
