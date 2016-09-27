from application import app
from application import secrets

if __name__ == '__main__':
    app.secret_key = secrets.app_secret_key
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
