# Item Catalog

Full-stack C.R.U.D. web application written in Python with the Flask framework.
Utilizes SqlAlchemy.

## Setup
1. Download Vagrant folder from: https://github.com/udacity/fullstack-nanodegree-vm
   For instructions on installing and running Vagrant, see here: https://www.vagrantup.com/docs/getting-started/
2. Download this repository into the same directory as the Vagrant file from step 1
3. Add your own secrets.py file in the application folder in the project directory, with:

   ```python
   app_secret_key = # generate a secure session key, see here:
   # http://flask.pocoo.org/docs/0.11/quickstart/#sessions
   github_client_id = # your github oauth2 client id
   github_client_secret = # your github oath2 secret
   ```

4. Once inside the Vagrant VM, navigate to /vagrant/item-catalog and enter:

   ```
   python application/dbsetup.py
   python runserver.py
   ```

5. In your browser, navigate to: http://localhost:5000/
