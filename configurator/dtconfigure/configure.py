from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import os, sys

from pathlib import Path

path_file = os.path.dirname(os.path.realpath(__file__))
path_module = Path(path_file)
sys.path.append(f"{path_module}")

from configurator.dtconfigure.auth import login_required
from configurator.dtconfigure.db import get_db
import os, sys


"""
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )
)
"""

from DICOMTransit.LocalDB.schema import CNBP_blueprint

envvars = CNBP_blueprint.dotenv_variables

bp = Blueprint("configure", __name__)


@bp.route("/")
@login_required
def index():
    """
    Show all the configurations, most recent order first
    :return:
    """

    db = get_db()
    configurations = db.execute(
        "SELECT p.*, u.username"
        " FROM configuration p JOIN user u ON p.user_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()

    # A list of password keys whose content we want to obscure on the UI
    password_keys = [
        "LORISpassword",
        "ProxyPassword",
        "LORISHostPassword",
        "DevOrthancPassword",
        "ProdOrthancPassword",
    ]
    return render_template(
        "configure/index.html",
        configurations=configurations,
        password_keys=password_keys,
    )


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """
    The Create View
    """

    if request.method == "POST":
        error = None

        # Check form data and get result
        d = check_form_inputs(request.form)
        if d is None:
            return "Could not save data"
        else:
            # Create a list of Tuples because we want to use executemany
            data = [tuple(d)]
            # Get connection to the database and get a cursor
            db = get_db()
            c = db.cursor()

            # Create INSERT SQL string
            db_frag = "INSERT INTO configuration ("
            user_frag = "user_id,"
            user_val_frag = "?,"
            cols = ",".join(envvars)
            end_cols_frag = ") "
            vals_frag = "VALUES("
            vals = "?," * len(envvars)
            # remove trailing comma ,
            vals = vals.rstrip(",")
            end_vals_frag = ")"
            sql = (
                db_frag
                + user_frag
                + cols
                + end_cols_frag
                + vals_frag
                + user_val_frag
                + vals
                + end_vals_frag
            )

            c.executemany(sql, data)
            db.commit()
            return redirect(url_for("configure.index"))

    # It's not a POST so we are showing files from configuration table
    configurations = {}
    # Ue list comprehension to create dict of configurations
    # The dict keys are the samne as the dict values
    configurations = {v: v for v in envvars}
    return render_template("configure/create.html", configurations=configurations)


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """
    The Update View
    """
    configuration = get_configuration(id)

    if request.method == "POST":
        error = None

        # Check form data and get result
        input_data = check_form_inputs(request.form)

        if input_data is None:
            return "Could not update data. Input data is NONE! Check how it was obtained etc. "
        else:
            # Create a list of Tuples because we want to use executemany
            input_data.append(id)
            data = [tuple(input_data)]
            # Get connection to the database and get a cursor
            db = get_db()
            c = db.cursor()
            # Create UPDATE SQL string
            db_frag = "UPDATE configuration SET "
            user_val_frag = "user_id=?,"
            # Create column assighments from form data and append operator
            # and placeholder for last element of form element
            cols_vals = "=?,".join(envvars) + "=?"
            where_frag = " WHERE id=?"
            # Assemble the sql string
            sql = db_frag + user_val_frag + cols_vals + where_frag
            # Add logged in user id to data values for WHERE clause
            # Execute the sql
            c.executemany(sql, data)
            # Commit the transaction
            db.commit()
            # Return by redirecting to index page
            return redirect(url_for("configure.index"))

    configurations = {}
    # Ue list comprehension to create dict of configurations
    # The dict keys are the samne as the dict values
    configurations = dict(configuration)
    # Remove columns that should not be user editable on the front-end
    del configurations["user_id"]
    del configurations["created"]
    del configurations["username"]
    password_keys = [
        "LORISpassword",
        "ProxyPassword",
        "LORISHostPassword",
        "DevOrthancPassword",
        "ProdOrthancPassword",
    ]
    return render_template(
        "configure/update.html",
        configurations=configurations,
        password_keys=password_keys,
    )


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """
    Delete View
    :param id:
    :return:
    """

    get_configuration(id)
    db = get_db()
    db.execute("DELETE FROM configuration WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("configure.index"))


def check_form_inputs(form):
    """
    Check the form inputs
    :param form:
    :return:
    """

    # Create an empty list
    data = []
    error = ""

    # Form keys
    form_keys = list(form)
    if sorted(form_keys) == sorted(envvars):
        data = [str(g.user["id"])] + list(form.values())
    else:
        error = "The form values are invalid. All fields are required"

    # If there are errors then show them and return None
    if error is not None and error != "":
        flash(error)
        return None

    # Return the values since all is okay
    return data


def get_configuration(id, check_user=True):
    """
    Get configuration and check if user matches. 
    :param id:
    :param check_user:
    :return:
    """
    configuration = (
        get_db()
        .execute(
            "SELECT p.*, u.username"
            " FROM configuration p JOIN user u ON p.user_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if configuration is None:
        abort(404, "Configuration id {0} doesn't exist.".format(id))

    if check_user and configuration["user_id"] != g.user["id"]:
        abort(403)

    return configuration
