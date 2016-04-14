from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, User, Category, Item

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

#Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/category/')
def showCategories():
    # TODO: render public and private pages
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    categories = session.query(Category).all()
    return render_template('categories.html', categories = categories)

@app.route('/category/new/', methods=['GET','POST'])
def newCategory():
    if 'username' not in login_session:
        flash("You must be logged in order to add a new category.")
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        name = request.form['name']
        user_id = login_session['user_id']
        newCategory = Category(name = name, user_id = user_id)
        session.add(newCategory)
        session.commit()
        flash("Category %s created!" % name)
        return redirect(url_for('showCategories'))
    else:
        return render_template("newcategory.html")

@app.route('/category/<int:category_id>/delete/', methods=['GET','POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        flash("You must be logged in and the creator of a category in order to delete it.")
        return redirect(url_for('showLogin'))

    categoryToDelete = session.query(Category).filter_by(id = category_id).one()
    if categoryToDelete.user_id == login_session['user_id'] and request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash ("%s has been deleted" % categoryToDelete.name)
        return redirect(url_for('showCategories'))
    elif categoryToDelete.user_id == login_session['user_id']:
        return render_template('deletecategory.html', category = categoryToDelete)
    else:
        flash("You can only delete categories that you have created.")
        return redirect(url_for('showCategories'))

@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        flash("You must be logged in and the creator of a category in order to edit it.")
        return redirect(url_for('showLogin'))

    categoryToEdit = session.query(Category).filter_by(id = category_id).one()
    if categoryToEdit.user_id == login_session['user_id'] and request.method == 'POST':
        categoryToEdit.name = request.form['name']
        flash("Name updated to %s" % categoryToEdit.name)
        session.add(categoryToEdit)
        session.commit()
        return redirect(url_for('showCategories'))
    elif categoryToEdit.user_id == login_session['user_id']:
        return render_template('editcategory.html', category = categoryToEdit)
    else:
        flash("You can only edit categories that you have created.")
        return redirect(url_for('showCategories'))

# TODO: item pages
#show all items for category
@app.route('/category/<int:category_id>/item/')
def showItems(category_id):
    return "Page to show items of category #%s" % category_id

#add item
@app.route('/category/<int:category_id>/item/new/')
def newItem(category_id):
    return "Page to make a new item for category #%s" % category_id

#edit item
@app.route('/category/<int:category_id>/item/<int:item_id>/edit/')
def editItem(category_id, item_id):
    return "Page to edit item #%s for category #%s" % (item_id, category_id)

#delete item
@app.route('/category/<int:category_id>/item/<int:item_id>/delete/')
def deleteItem(category_id, item_id):
    return "Page to delete item #%s for category #%s" % (item_id, category_id)

@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gitConnect/')
def gitConnect():
    if login_session['state'] != request.args.get('state'):
        response = make_response(json.dumps('Invalid State Parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.args.get('code')
    uri = "https://github.com/login/oauth/access_token?"
    uri += "code=" + code + "&"
    uri += "client_id=4435c0a8240811f213e6&"
    uri += "client_secret=f703352800fdf1ea073de23532fa6385eb99d218"
    h = httplib2.Http()
    headers = {'Accept': 'application/json'}
    access_token = json.loads(h.request(uri, 'POST', headers = headers)[1])['access_token']
    #print "RESULT"
    #jsonResult = json.loads(result)
    print access_token
    uri = "https://api.github.com/user?access_token=" + access_token
    h = httplib2.Http()
    print "********************************************************"
    userData = json.loads(h.request(uri, 'GET')[1])
    print "********************************************************"
    print userData
    print "********************************************************"
    #print user[0]
    #print "********************************************************"
    #print user[1]
    login_session['provider'] = 'github'
    login_session['username'] = userData['login']
    login_session['name'] = userData['name']
    login_session['picture'] = userData['avatar_url']
    login_session['email'] = userData['email']
    login_session['github_id'] = userData['id']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    flash("You are now logged in, " + login_session['name'])
    return redirect(url_for('showCategories'))

@app.route('/gitDisconnect')
def gitDisconnect():
    if login_session['provider'] == 'github':
        del login_session['provider']
        del login_session['username']
        del login_session['name']
        del login_session['picture']
        del login_session['email']
        del login_session['github_id']
        del login_session['user_id']
        # TODO: insert link into logout page or revoke authorization or ask to revoke
        return """
                You have been logged out, however this application
                is this authorized to access your Github account. To
                revoke this authorization, visit your account page on Github.com
            """
    else:
        return "You were not logged in"

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def createUser(login_session):
    newUser = User(name = login_session['name'],
                    email = login_session['email'],
                    picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

if __name__ == '__main__':
  app.secret_key = "shhh_dont_share_this_with_anyone"
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)