from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from dtconfigure.auth import login_required
from dtconfigure.db import get_db
from LocalDB.schema import CNBP_blueprint
envvars = CNBP_blueprint.dotenv_variables

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
            return "Could not save data"
        else:
            # Create a list of Tuples because we want to use executemany
            data = [tuple(d)]
            # Get connection to the database and get a cursor
            db = get_db()
            c = db.cursor()

            # Create INSERT SQL string
            db_frag = 'INSERT INTO configuration ('
            user_frag = "user_id,"
            user_val_frag = "?,"
            cols = ",".join(envvars)
            end_cols_frag = ") "
            vals_frag = "VALUES("
            vals = "?," * len(envvars)
            # remove trailing comma ,
            vals = vals.rstrip(',')
            end_vals_frag = ")"
            sql = db_frag + user_frag + cols + end_cols_frag + vals_frag + user_val_frag + vals + end_vals_frag

            c.executemany(sql,data)
            db.commit()
            return redirect(url_for('configure.index'))

    # It's not a POST so we are showing files from configuration table

    configurations = {}
    # Ue list comprehension to create dict of configurations
    # The dict keys are the samne as the dict values
    configurations = {v:v for v in envvars}
    #print({v:v for v in envvars})
    return render_template('configure/create.html',configurations=configurations)


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
                LocalDatabasePath=?, ProxyIP=?, ProxyUsername=?, ProxyPassword=?, \
                LORISHostIP=?, LORISHostUsername=?, LORISHostPassword=?, \
                InsertionAPI=?, DeletionScript=?, zip_storage_location=?, DevOrthancIP=?,\
                DevOrthanUser=?, DevOrthancPassword=?, ProdOrthancIP=?, ProdOrthancUser=?,\
                ProdOrthancPassword=?', data
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


""" Check the form inputs """
def check_form_inputs(form):
    # Create an empty list
    data = []
    error = ''

    # Form keys
    form_keys = list(form)
    print('Form keys', form_keys)
    print('envvars', envvars)
    if(sorted(form_keys)==sorted(envvars)):
        data = [g.user['id']] + list(form.values())
    else:
        error = 'The form values are invalid. All fields are required'


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


