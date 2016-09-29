# user-auth.py - Account creation and oauth2
import httplib2
import json
import random
import string

import secrets
import db_utils


def logout(login_session):
    if 'user_id' in login_session:
        login_session.clear()
        return """
                You have been logged out, however this application
                is still authorized to access your Github account. To
                revoke this authorization, visit your account page at
                Github.com
            """

    return "You were not logged in."


def make_state():
    return ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))


def get_github_token(code):
    uri = "https://github.com/login/oauth/access_token?"
    uri += "code=" + code + "&"
    uri += "client_id=" + secrets.github_client_id + "&"
    uri += "client_secret=" + secrets.github_client_secret
    h = httplib2.Http()
    headers = {'Accept': 'application/json'}
    return json.loads(
        h.request(uri, 'POST', headers=headers)[1])['access_token']


def get_github_userdata(access_token):
    uri = "https://api.github.com/user?access_token=" + access_token
    h = httplib2.Http()

    return json.loads(h.request(uri, 'GET')[1])


def githubConnect(code, login_session):
    access_token = get_github_token(code)
    user_data = get_github_userdata(access_token)

    login_session['provider'] = 'github'
    login_session['username'] = user_data['login']
    login_session['name'] = user_data['name']
    login_session['picture'] = user_data['avatar_url']
    login_session['email'] = user_data['email']
    login_session['github_id'] = user_data['id']

    user_id = db_utils.get_user_id(login_session['email'])

    if not user_id:
        user_id = db_utils.create_user(login_session)

    return user_id
