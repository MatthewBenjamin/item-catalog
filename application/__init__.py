from flask import (Flask, render_template, request, redirect, jsonify, url_for,
                   flash, make_response)
from flask import session as login_session
import json

# TODO: move these operations into db_utils.py
from sqlalchemy import asc
from dbsetup import Category, Item

import user_auth
import db_utils


app = Flask(__name__)


# JSON endpoints
@app.route('/category/JSON/')
def categoriesJSON():
    categories = db_utils.session.query(Category).all()
    # TODO: make general serialize helper for arrays of data models
    return jsonify(Category=[i.serialize for i in categories])


@app.route('/category/<int:category_id>/JSON/')
def categoryItemsJSON(category_id):
    items = db_utils.session.query(Item).filter_by(
        category_id=category_id).all()
    # TODO: make general serialize helper for arrays of data models
    return jsonify(Item=[i.serialize for i in items])


@app.route('/category/<int:category_id>/item/<int:item_id>/JSON/')
def itemJSON(category_id, item_id):
    item = db_utils.session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


@app.route('/')
@app.route('/category/')
def showCategories():
    if 'user_id' in login_session:
        user_id = login_session['user_id']
        userCategories = db_utils.session.query(Category).filter_by(
            user_id=user_id).order_by(asc(Category.name))
        publicCategories = db_utils.session.query(
            Category).filter(user_id != user_id).order_by(asc(Category.name))
        return render_template(
            'categories.html',
            public_categories=publicCategories,
            user_categories=userCategories)
    else:
        categories = db_utils.session.query(Category).all()
        return render_template('categories.html', public_categories=categories)


@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        flash("You must be logged in order to add a new category.")
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        name = request.form['name']
        user_id = login_session['user_id']
        newCategory = Category(name=name, user_id=user_id)
        db_utils.session.add(newCategory)
        db_utils.session.commit()
        flash("Category %s created!" % name)
        return redirect(url_for('showCategories'))
    else:
        return render_template("newcategory.html")


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        flash("""
            You must be logged in and the creator of a category in order to
            delete it.
        """)
        return redirect(url_for('showLogin'))

    categoryToDelete = db_utils.session.query(
        Category).filter_by(id=category_id).one()

    if (categoryToDelete.user_id == login_session['user_id'] and
            request.method == 'POST'):
        db_utils.session.delete(categoryToDelete)
        db_utils.session.query(Item).filter_by(
            category_id=categoryToDelete.id).delete()
        db_utils.session.commit()
        flash("%s has been deleted" % categoryToDelete.name)
        return redirect(url_for('showCategories'))
    elif categoryToDelete.user_id == login_session['user_id']:
        return render_template('deletecategory.html',
                               category=categoryToDelete)
    else:
        flash("You can only delete categories that you have created.")
        return redirect(url_for('showCategories'))


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        flash("""
            You must be logged in and the creator of a category in order to
            edit it.
        """)
        return redirect(url_for('showLogin'))

    categoryToEdit = db_utils.session.query(Category).filter_by(
        id=category_id).one()
    # TODO: implement helper, i.e.
    # categoryToEdit = db_utils.getByID(Category, category_id)
    if (categoryToEdit.user_id == login_session['user_id'] and
            request.method == 'POST'):
        categoryToEdit.name = request.form['name']
        flash("Name updated to %s" % categoryToEdit.name)
        db_utils.session.add(categoryToEdit)
        db_utils.session.commit()
        return redirect(url_for('showCategories'))
    elif categoryToEdit.user_id == login_session['user_id']:
        return render_template('editcategory.html', category=categoryToEdit)
    else:
        flash("You can only edit categories that you have created.")
        return redirect(url_for('showCategories'))


# TODO: item pages
# show all items for category
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/item/')
def showCategoryItems(category_id):
    category = db_utils.session.query(Category).filter_by(id=category_id).one()
    items = db_utils.session.query(Item).filter_by(
        category_id=category_id).order_by(asc(Item.name))
    return render_template('items.html', category=category, items=items)


# add item
@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        flash("You must be logged in to add a new item.")
        return redirect(url_for('showLogin'))

    category = db_utils.session.query(Category).filter_by(id=category_id).one()
    if (request.method == 'POST' and
            login_session['user_id'] == category.user_id):
        itemToCreate = Item(name=request.form['name'],
                            description=request.form['description'],
                            user_id=login_session['user_id'],
                            category_id=category_id)
        db_utils.session.add(itemToCreate)
        db_utils.session.commit()
        flash("Item %s of category %s has been created!" % (
            itemToCreate.name, category.name))
        return redirect(url_for('showCategoryItems', category_id=category_id))
    elif login_session['user_id'] == category.user_id:
        return render_template('newitem.html', category=category)
    else:
        flash("You can only add items to categories that you have created.")
        return redirect(url_for('showCategories'))


@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(category_id, item_id):
    item = db_utils.session.query(Item).filter_by(id=item_id).one()
    category = db_utils.session.query(Category).filter_by(id=category_id).one()
    return render_template('singleitem.html', category=category, item=item)


# edit item
@app.route(
    '/category/<int:category_id>/item/<int:item_id>/edit/',
    methods=['GET', 'POST'])
def editItem(category_id, item_id):
    if 'username' not in login_session:
        flash("You must be logged in to edit an item.")
        return redirect('/login')

    itemToEdit = db_utils.session.query(Item).filter_by(id=item_id).one()
    if (request.method == 'POST' and
            login_session['user_id'] == itemToEdit.user_id):
        if request.form['name']:
            itemToEdit.name = request.form['name']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        db_utils.session.add(itemToEdit)
        db_utils.session.commit()
        flash("%s has been updated." % itemToEdit.name)
        return redirect(url_for('showCategoryItems', category_id=category_id))
    elif login_session['user_id'] == itemToEdit.user_id:
        return render_template(
            'edititem.html', category_id=category_id, item=itemToEdit)
    else:
        flash("You can only edit items that you have created.")
        return redirect(url_for('showCategoryItems', category_id=category_id))


# delete item
@app.route(
    '/category/<int:category_id>/item/<int:item_id>/delete/',
    methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        flash("You must be logged in to delete an item.")
        return redirect('/login')

    itemToDelete = db_utils.session.query(Item).filter_by(id=item_id).one()
    if (request.method == 'POST' and
            login_session['user_id'] == itemToDelete.user_id):
        db_utils.session.delete(itemToDelete)
        db_utils.session.commit()
        flash("%s has been deleted." % itemToDelete.name)
        return redirect(url_for('showCategoryItems', category_id=category_id))
    elif login_session['user_id'] == itemToDelete.user_id:
        return render_template(
            'deleteitem.html', category_id=category_id, item=itemToDelete)
    else:
        flash("You can only delete items that you have created.")
        return redirect(url_for('showCategoryItems', category_id=category_id))


@app.route('/login/')
def showLogin():
    state = user_auth.makeState()
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gitConnect/')
def gitConnect():
    if login_session['state'] != request.args.get('state'):
        response = make_response(json.dumps('Invalid State Parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.args.get('code')
    user_id = user_auth.githubConnect(code, login_session)
    login_session['user_id'] = user_id
    flash("You are now logged in, " + login_session['name'])

    return redirect(url_for('showCategories'))


@app.route('/logout/')
def logout():
    flash(user_auth.logout(login_session))
    return redirect('/')
