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
from flask import Flask, g, jsonify
from flask import render_template, url_for
from flask import request, session, redirect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table

from passlib.hash import sha256_crypt


from model import Recomendacao


#######################################
#####                             #####
#####     Config  section         #####
#####                             #####
#######################################
app = Flask(__name__)

app.config.update(dict(
        DATABASE='db_recommender',
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
#####   Preambule section         #####
#####                             #####
#######################################
#TODO: criar resposta de erro
#TODO: segurança - autenticação e chave de requisição
@app.route('/')
def accueil():
    if 'username' in session:
       return render_template('accueil.html', titre='Financial web', username=session['username'])
    return render_template('accueil.html', titre='Financial web')

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

#######################################
#####                             #####
#####   READ section              #####
#####                             #####
#######################################

@app.route('/api/v1.0/recommendation/<user>')
def get_recommendation(user):

    try:
        db = get_db()
        Session = sessionmaker(bind=db)
        dbsession = Session()
        
        #TODO: filtrar por data de geração ou por recomendação ativa

        result = dbsession.query(Recomendacao).filter(Recomendacao.cliente == user)
        #TODO: if len(result >= 1):
        produtos = dict()
        for r in result:
            produtos[r.produto] = r.rank
        serialized = dict()
        serialized['cliente'] = user
        serialized['produtos'] = produtos
        
        #TODO: gravar data de oferta

    except Exception as err:
        print(err)
        return jsonify({"response":"Something went wrong."})
    
    return jsonify(serialized)

if __name__ == '__main__':

    #app.run(host='0.0.0.0', port=8080, debug=True)
    app.run(debug=True)
