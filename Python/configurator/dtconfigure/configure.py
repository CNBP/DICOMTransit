from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from dtconfigure.auth import login_required
from dtconfigure.db import get_db

bp = Blueprint('configure', __name__)

""" Show all the configurations, most recent order first """
@bp.route('/')
@login_required
def index():
    db = get_db()
    configurations = db.execute(
        'SELECT p.*, u.username'
        ' FROM configuration p JOIN user u ON p.user_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    # A list of password keys whose content we want to obscure on the UI
    password_keys = ["LORISpassword","ProxyPassword","LORISHostPassword"]
    return render_template('configure/index.html',
                           configurations=configurations,password_keys=password_keys)


""" The Create View """
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        error = None

        # Check form data and get result
        d =  check_form_inputs(request.form)

        if d is None:
            return False
        else:
            # Create a list of Tuples because we want to use executemany
            data = [tuple(d)]
            # Get connection to the database and get a cursor
            db = get_db()
            c = db.cursor()
            c.executemany(
                'INSERT INTO configuration (user_id, port, LORISurl, \
                LORISusername, LORISpassword, timepoint_prefix, institutionID, \
                projectID_dictionary, LocalDatabase, OrthancURL, ProxyIP, \
                ProxyUsername, ProxyPassword, LORISHostIP, LORISHostUsername, \
                LORISHostPassword, DeletionScript)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                data)
            db.commit()
            return redirect(url_for('configure.index'))

    return render_template('configure/create.html')


""" The Update View """
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    configuration = get_configuration(id)

    if request.method == 'POST':
        error = None

        # Check form data and get result
        d =  check_form_inputs(request.form)

        if d is None:
            return False
        else:
            # Create a list of Tuples because we want to use executemany
            data = [tuple(d)]
            # Get connection to the database and get a cursor
            db = get_db()
            c = db.cursor()
            c.executemany(
                'UPDATE configuration SET user_id=?, port=?, LORISurl=?,\
                LORISusername=?, LORISpassword=?, timepoint_prefix=?, \
                institutionID=?,projectID_dictionary=?, LocalDatabase=?, \
                OrthancURL=?, ProxyIP=?, ProxyUsername=?, ProxyPassword=?, \
                LORISHostIP=?, LORISHostUsername=?, LORISHostPassword=?, \
                DeletionScript=?', data
            )
            db.commit()
            return redirect(url_for('configure.index'))

    return render_template('configure/update.html',configuration=configuration)


""" Delete View """
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_configuration(id)
    db = get_db()
    db.execute('DELETE FROM configuration WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('configure.index'))


def check_form_inputs(form):
    # Create an empty list
    data = []

    """
    The order of values in the data variable is IMPORTANT!!!
    """
    # Insert currently logged in user ID
    data.append(g.user['id'])
    # Insert relevant form values
    data.append(form['port'])
    data.append(form['LORISurl'])
    data.append(form['LORISusername'])
    data.append(form['LORISpassword'])
    data.append(form['timepoint_prefix'])
    data.append(form['institutionID'])
    data.append(form['projectID_dictionary'])
    data.append(form['LocalDatabase'])
    data.append(form['OrthancURL'])
    data.append(form['ProxyIP'])
    data.append(form['ProxyUsername'])
    data.append(form['ProxyPassword'])
    data.append(form['LORISHostIP'])
    data.append(form['LORISHostUsername'])
    data.append(form['LORISHostPassword'])
    data.append(form['DeletionScript'])

    error = ''

    if not form['port']:
        error += 'Port is is required.'
    if not form['LORISurl']:
        error += 'LORIS Url is required.'
    if not form['LORISusername']:
        error += 'LORIS username is required.'
    if not form['LORISpassword']:
        error += 'LORIS password is required.'
    if not form['timepoint_prefix']:
        error += 'Time point prefix is required.'
    if not form['institutionID']:
        error += 'Institution ID is required.'
    if not form['projectID_dictionary']:
        error += 'ProjectID dictionary is required.'
    if not form['LocalDatabase']:
        error += 'Local Database is required.'
    if not form['OrthancURL']:
        error += 'Orthanc URL is required.'
    if not form['ProxyIP']:
        error += 'Proxy IP is required.'
    if not form['ProxyUsername']:
        error += 'Proxy username is required.'
    if not form['ProxyPassword']:
        error += 'Proxy password is required.'
    if not form['LORISHostIP']:
        error += 'LORIS Host IP is required.'
    if not form['LORISHostUsername']:
        error += 'LORIS Host username is required.'
    if not form['LORISHostPassword']:
        error += 'LORIS Host password is required.'
    if not form['DeletionScript']:
        error += 'Path to Deletion script is required.'

    # If there are errors then show them and return None
    if error is not None and error!='':
        flash(error)
        return None

    # Return the values since all is okay
    return data


""" Get configuration and check if user matches """
def get_configuration(id, check_user=True):

    configuration = get_db().execute(
        'SELECT p.*, u.username'
        ' FROM configuration p JOIN user u ON p.user_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if configuration is None:
        abort(404, "Configuration id {0} doesn't exist.".format(id))

    if check_user and configuration['user_id'] != g.user['id']:
        abort(403)

    return configuration


