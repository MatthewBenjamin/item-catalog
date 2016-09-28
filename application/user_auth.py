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


def makeState():
    return ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))


def getGitHubToken(code):
    uri = "https://github.com/login/oauth/access_token?"
    uri += "code=" + code + "&"
    uri += "client_id=" + secrets.github_client_id + "&"
    uri += "client_secret=" + secrets.github_client_secret
    h = httplib2.Http()
    headers = {'Accept': 'application/json'}
    return json.loads(
        h.request(uri, 'POST', headers=headers)[1])['access_token']


def getGithubUserData(access_token):
    uri = "https://api.github.com/user?access_token=" + access_token
    h = httplib2.Http()

    return json.loads(h.request(uri, 'GET')[1])


def githubConnect(code, login_session):
    access_token = getGitHubToken(code)
    userData = getGithubUserData(access_token)

    login_session['provider'] = 'github'
    login_session['username'] = userData['login']
    login_session['name'] = userData['name']
    login_session['picture'] = userData['avatar_url']
    login_session['email'] = userData['email']
    login_session['github_id'] = userData['id']

    user_id = db_utils.getUserID(login_session['email'])

    if not user_id:
        user_id = db_utils.createUser(login_session)

    return user_id
