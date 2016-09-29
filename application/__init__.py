from flask import (Flask, render_template, request, redirect, jsonify, url_for,
                   flash, make_response)
from flask import session as login_session
import json

from sqlalchemy import asc
from dbsetup import Category, Item

import user_auth
import db_utils

app = Flask(__name__)


# JSON endpoints
@app.route('/category/JSON/')
def categories_json():
    categories = db_utils.session.query(Category).all()
    return jsonify(Category=Category.serialize_list(categories))


@app.route('/category/<int:category_id>/JSON/')
def category_items_json(category_id):
    items = db_utils.session.query(Item).filter_by(
        category_id=category_id).all()
    return jsonify(Item=Item.serialize_list(items))


@app.route('/category/<int:category_id>/item/<int:item_id>/JSON/')
def item_json(category_id, item_id):
    item = db_utils.get_by_id(Item, item_id)
    return jsonify(Item=item.serialize)


@app.route('/')
@app.route('/category/')
def show_categories():
    all_categories = db_utils.session.query(Category)
    if 'user_id' in login_session:
        user_id = login_session['user_id']
        userCategories = all_categories.filter_by(
            user_id=user_id).order_by(asc(Category.name))
        publicCategories = all_categories.filter(
            user_id != user_id).order_by(asc(Category.name))
        return render_template(
            'categories.html',
            public_categories=publicCategories,
            user_categories=userCategories)
    else:
        return render_template('categories.html',
                               public_categories=all_categories.all())


@app.route('/category/new/', methods=['GET', 'POST'])
def new_category():
    if 'username' not in login_session:
        flash("You must be logged in order to add a new category.")
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        new_category = Category(name=request.form['name'],
                                user_id=login_session['user_id'])
        db_utils.save_record(new_category)
        flash("Category %s created!" % new_category.name)
        return redirect(url_for('show_categories'))
    else:
        return render_template("newcategory.html")


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def delete_category(category_id):
    if 'username' not in login_session:
        flash("""
            You must be logged in and the creator of a category in order to
            delete it.
        """)
        return redirect(url_for('show_login'))

    category_to_delete = db_utils.get_by_id(Category, category_id)

    if (category_to_delete.user_id == login_session['user_id'] and
            request.method == 'POST'):
        db_utils.delete_category_items(category_to_delete.id)
        db_utils.delete_record(category_to_delete)
        flash("%s has been deleted" % category_to_delete.name)
        return redirect(url_for('show_categories'))
    elif category_to_delete.user_id == login_session['user_id']:
        return render_template('deletecategory.html',
                               category=category_to_delete)
    else:
        flash("You can only delete categories that you have created.")
        return redirect(url_for('show_categories'))


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def edit_category(category_id):
    if 'username' not in login_session:
        flash("""
            You must be logged in and the creator of a category in order to
            edit it.
        """)
        return redirect(url_for('show_login'))

    category_to_edit = db_utils.get_by_id(Category, category_id)

    if (category_to_edit.user_id == login_session['user_id'] and
            request.method == 'POST'):
        category_to_edit.name = request.form['name']
        db_utils.save_record(category_to_edit)
        flash("Name updated to %s" % category_to_edit.name)
        return redirect(url_for('show_categories'))
    elif category_to_edit.user_id == login_session['user_id']:
        return render_template('editcategory.html', category=category_to_edit)
    else:
        flash("You can only edit categories that you have created.")
        return redirect(url_for('show_categories'))


# show all items for category
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/item/')
def show_category_items(category_id):
    category = db_utils.get_by_id(Category, category_id)
    items = db_utils.session.query(Item).filter_by(
        category_id=category_id).order_by(asc(Item.name))
    return render_template('items.html', category=category, items=items)


# add item
@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def new_item(category_id):
    if 'username' not in login_session:
        flash("You must be logged in to add a new item.")
        return redirect(url_for('show_login'))

    category = db_utils.get_by_id(Category, category_id)
    if (request.method == 'POST' and
            login_session['user_id'] == category.user_id):
        item_to_create = Item(name=request.form['name'],
                              description=request.form['description'],
                              user_id=login_session['user_id'],
                              category_id=category_id)
        db_utils.save_record(item_to_create)
        flash("Item %s of category %s has been created!" % (
            item_to_create.name, category.name))
        return redirect(url_for('show_category_items',
                                category_id=category_id))
    elif login_session['user_id'] == category.user_id:
        return render_template('newitem.html', category=category)
    else:
        flash("You can only add items to categories that you have created.")
        return redirect(url_for('show_categories'))


@app.route('/category/<int:category_id>/item/<int:item_id>/')
def show_item(category_id, item_id):
    item = db_utils.get_by_id(Item, item_id)
    category = db_utils.get_by_id(Category, category_id)
    return render_template('singleitem.html', category=category, item=item)


# edit item
@app.route(
    '/category/<int:category_id>/item/<int:item_id>/edit/',
    methods=['GET', 'POST'])
def edit_item(category_id, item_id):
    if 'username' not in login_session:
        flash("You must be logged in to edit an item.")
        return redirect('/login')

    item_to_edit = db_utils.get_by_id(Item, item_id)
    if (request.method == 'POST' and
            login_session['user_id'] == item_to_edit.user_id):
        # TODO: error handling for blank field
        if request.form['name']:
            item_to_edit.name = request.form['name']
        if request.form['description']:
            item_to_edit.description = request.form['description']

        db_utils.save_record(item_to_edit)
        flash("%s has been updated." % item_to_edit.name)

        return redirect(url_for('show_category_items',
                                category_id=category_id))

    elif login_session['user_id'] == item_to_edit.user_id:
        return render_template(
            'edititem.html', category_id=category_id, item=item_to_edit)
    else:
        flash("You can only edit items that you have created.")
        return redirect(url_for('show_category_items',
                                category_id=category_id))


# delete item
@app.route(
    '/category/<int:category_id>/item/<int:item_id>/delete/',
    methods=['GET', 'POST'])
def delete_item(category_id, item_id):
    if 'username' not in login_session:
        flash("You must be logged in to delete an item.")
        return redirect('/login')

    item_to_delete = db_utils.get_by_id(Item, item_id)
    if (request.method == 'POST' and
            login_session['user_id'] == item_to_delete.user_id):
        db_utils.delete_record(item_to_delete)
        flash("%s has been deleted." % item_to_delete.name)
        return redirect(url_for('show_category_items',
                                category_id=category_id))
    elif login_session['user_id'] == item_to_delete.user_id:
        return render_template(
            'deleteitem.html', category_id=category_id, item=item_to_delete)
    else:
        flash("You can only delete items that you have created.")
        return redirect(url_for('show_category_items',
                                category_id=category_id))


@app.route('/login/')
def show_login():
    state = user_auth.make_state()
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gitConnect/')
def git_connect():
    if login_session['state'] != request.args.get('state'):
        response = make_response(json.dumps('Invalid State Parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.args.get('code')
    user_id = user_auth.githubConnect(code, login_session)
    login_session['user_id'] = user_id
    flash("You are now logged in, " + login_session['name'])

    return redirect(url_for('show_categories'))


@app.route('/logout/')
def logout():
    flash(user_auth.logout(login_session))
    return redirect('/')
