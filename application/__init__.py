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
    return jsonify(Category=Category.serializeList(categories))


@app.route('/category/<int:category_id>/JSON/')
def categoryItemsJSON(category_id):
    items = db_utils.session.query(Item).filter_by(
        category_id=category_id).all()
    return jsonify(Item=Item.serializeList(items))


@app.route('/category/<int:category_id>/item/<int:item_id>/JSON/')
def itemJSON(category_id, item_id):
    item = db_utils.getByID(Item, item_id)
    return jsonify(Item=item.serialize)


@app.route('/')
@app.route('/category/')
def showCategories():
    allCategories = db_utils.session.query(Category)
    if 'user_id' in login_session:
        user_id = login_session['user_id']
        userCategories = allCategories.filter_by(
            user_id=user_id).order_by(asc(Category.name))
        publicCategories = allCategories.filter(
            user_id != user_id).order_by(asc(Category.name))
        return render_template(
            'categories.html',
            public_categories=publicCategories,
            user_categories=userCategories)
    else:
        return render_template('categories.html',
                               public_categories=allCategories.all())


@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        flash("You must be logged in order to add a new category.")
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        db_utils.saveRecord(newCategory)
        flash("Category %s created!" % newCategory.name)
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

    categoryToDelete = db_utils.getByID(Category, category_id)

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

    categoryToEdit = db_utils.getByID(Category, category_id)

    if (categoryToEdit.user_id == login_session['user_id'] and
            request.method == 'POST'):
        categoryToEdit.name = request.form['name']
        db_utils.saveRecord(categoryToEdit)
        flash("Name updated to %s" % categoryToEdit.name)
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
    category = db_utils.getByID(Category, category_id)
    items = db_utils.session.query(Item).filter_by(
        category_id=category_id).order_by(asc(Item.name))
    return render_template('items.html', category=category, items=items)


# add item
@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        flash("You must be logged in to add a new item.")
        return redirect(url_for('showLogin'))

    category = db_utils.getByID(Category, category_id)
    if (request.method == 'POST' and
            login_session['user_id'] == category.user_id):
        itemToCreate = Item(name=request.form['name'],
                            description=request.form['description'],
                            user_id=login_session['user_id'],
                            category_id=category_id)
        db_utils.saveRecord(itemToCreate)
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
    item = db_utils.getByID(Item, item_id)
    category = db_utils.getByID(Category, category_id)
    return render_template('singleitem.html', category=category, item=item)


# edit item
@app.route(
    '/category/<int:category_id>/item/<int:item_id>/edit/',
    methods=['GET', 'POST'])
def editItem(category_id, item_id):
    if 'username' not in login_session:
        flash("You must be logged in to edit an item.")
        return redirect('/login')

    itemToEdit = db_utils.getByID(Item, item_id)
    if (request.method == 'POST' and
            login_session['user_id'] == itemToEdit.user_id):
        # TODO: error handling for blank field
        if request.form['name']:
            itemToEdit.name = request.form['name']
        if request.form['description']:
            itemToEdit.description = request.form['description']

        db_utils.saveRecord(itemToEdit)
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

    itemToDelete = db_utils.getByID(Item, item_id)
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
