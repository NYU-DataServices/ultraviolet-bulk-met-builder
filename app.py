from flask import Flask, render_template, request, session, url_for, flash, redirect, abort, Markup, Response
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_mail import Mail
from werkzeug.security import generate_password_hash
import os
import sys
from importlib import import_module
import json
from random import random
import zlib, base64

from utils.db_handlers import *
from utils.github_handlers import *
from utils.emailer import *
from utils.met_field_models import *
from utils.form_builder_helpers import *
from utils.api_handlers import *
from models import *
from settings import APP_SECRET_KEY, DEBUG, MAIL_SERVER, \
                    MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD

app = Flask(__name__)
application = app
app.secret_key = APP_SECRET_KEY
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
mail = Mail(app)



""" Site navigation routes """

@app.route('/', methods = ['GET'])
def home():
    return render_template('general_use_template.html')


""" Project management routes """

@app.route('/projects', methods = ['GET'])
def list_projects():
    try:
        project_list = fetch_multiple_met_projects()
        if project_list:
            return render_template('project_list.html',
                                   title_text="UltraViolet Project List",
                                   proj_list = project_list)
        else:
            flash("There are currently no projects.")
            return render_template('general_use_template.html', title_text="No Results")
    except:
        flash("There was an error in retrieving a list of projects.")
        return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/projects/<metgroupid>', methods = ['GET'])
def retrieve_project_detail(metgroupid):
    try:
        met_group_list, project_title = fetch_met_group_records(metgroupid)
        if len(met_group_list) > 0:
            return render_template("project_detail_view.html",
                                   project_title = project_title,
                                   metgroupid = metgroupid,
                                   met_group_list = met_group_list)
        else:
            flash("There are not currently any records created for this project. Please select the \"Create New Record\" option above.")
            return home()
    except:
        flash("There was an error in retrieving the project detail.")
        return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/project-edit/<metgroupid>', methods = ['POST', 'GET'])
@login_required
def project_edit(metgroupid):
    project_title = fetch_single_met_projects(metgroupid)[1]
    if project_title:
        return render_template("project_edit_view.html",
                               project_title=project_title,
                               metgroupid=metgroupid)

    flash("There was an error in retrieving the project detail.")
    return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/project-update', methods = ['POST', 'GET'])
def update_project():
    metgroupid = request.args.get('id')
    success_update_project = update_project_record(metgroupid, request.form['new_project_title'])
    if success_update_project:
        return home()

    flash("There was an error in updating project.")
    return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/project-create', methods = ['GET', 'POST'])
@login_required
def project_create():
    try:
        templates = retrieve_current_templates()

        #Retrieve last known project ID number so it can be incremented
        project_id_list = [i[0] for i in fetch_multiple_met_projects()]
        project_id_list.sort(reverse=True)
        next_project_id = str(int(project_id_list[0]) + 1) if len(project_id_list) > 0 else "1"

        return render_template('project_create.html',
                               next_project_id = next_project_id,
                               template_list = templates)
    except:
        flash("There was an error in preparing to create a new project.")
        return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/establish-new-project', methods = ['GET', 'POST'])
def establish_new_project():
    new_metgroupid = request.args.get('id')
    success_create_project = create_project_record(request.form['new_project_title'],
                                                   request.form['selected_template'])
    if success_create_project:
        return home()

    flash("There was an error in creating project.")
    return render_template('general_use_template.html', title_text="An Error Occurred.")


""" Record management routes """

@app.route('/record-create-select-options', methods = ['GET'])
@login_required
def record_create_select():
    templates = retrieve_current_templates()
    project_list = fetch_multiple_met_projects()
    return render_template('single_record_options_select.html',
                           template_list = templates,
                           proj_list = project_list)

    flash("There was an error in creating a new record.")
    return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/record-create', methods = ['GET', 'POST'])
def record_create():
    templateid, metgroupid = request.form.get('selected_template'), request.form.get('selected_metgroup')
    try:
        template_fields = fetch_met_template(templateid)
        metadata_template = parse_field_info_db(template_fields)

        # We now ping the UV API and if successful, proceed with UV ID reserved there. Otherwise, indicate an error
        # For now, we substitute a random ID maker until UV goes into production
        #success_id_pull, uv_id = get_draft_id()
        success_id_pull, uv_id = get_temp_random_id()

        if success_id_pull:
            return render_template("single_record_view.html",
                                   uv_id = uv_id,
                                   tempid = templateid,
                                   mgrpid = metgroupid,
                                   met_form_html = metadata_template,
                                   submit_button_value = "Create Record")
        else:
            flash(uv_id)
            return render_template('general_use_template.html', title_text="An Error Occurred.")
    except:
        flash("There was an error in creating an entry template.")
        return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/record-edit/<uv_id>', methods = ['POST', 'GET'])
@login_required
def record_edit(uv_id):
    met_field_vals = fetch_met_fields_vals(uv_id)
    templateid = met_field_vals[0][2]
    metgroupid = pluck_metgroup_num(uv_id)
    if met_field_vals:
        template_fields = fetch_met_template(templateid)
        list_record_fields = arrange_template_fields(template_fields)
        metadata_template = parse_previous_field_info_db(template_fields, met_field_vals)
        form_html = "".join([i for i in metadata_template])

        return render_template("single_record_view.html",
                               uv_id = uv_id,
                               tempid = templateid,
                               mgrpid = metgroupid,
                               met_form_html = form_html,
                               submit_button_value = "Update Record",
                               list_record_fields = list_record_fields)

    flash("There was an error in retrieving editable record.")
    return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/record-update', methods = ['POST', 'GET'])
def record_update():
    uv_id, template_id, metgroupid = request.args.get('id'), request.args.get('template'), request.args.get('metgroupid')
    record_title = [i[1] for i in request.form.items() if i[0].split("_")[2] == "title"][0]

    # DB modifications
    grouped_dict = form_inputs_parser(request.form)[0]
    db_insert_field_vals = field_vals_to_db_rows(grouped_dict, uv_id, template_id)
    success_update_rec = record_met_field_vals(uv_id, db_insert_field_vals)
    success_update_metgroup = record_metgroup(uv_id, record_title, metgroupid)

    # JSON creation
    json_string_template_list = import_module('met_templates.template_{}.json_string_template_{}'.format(template_id,
                                                                                    template_id)).json_string_template
    json_record = template_to_json_builder(json_string_template_list, request.form)
    compressed_json = zlib.compress(json_record.encode('utf-8'), 9)
    success_change_json_rec = record_met_json(uv_id, compressed_json)
    if success_change_json_rec and success_update_rec and success_update_metgroup:
        return home()

    flash("There was an error in recording record.")
    return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/record-git/<uv_id>', methods = ['GET'])
@login_required
def record_git(uv_id):
    user = User(session.get('mets_user', None))
    if user.is_admin(0):
        return abort(403)

    try:
        json_hash = fetch_record_json(uv_id)[2]
    except TypeError:
        flash("This record has not yet been saved. Please edit/update the record first before pushing to Github.")
        return redirect(url_for('retrieve_project_detail', metgroupid = request.args.get('metgroupnum')))

    json_string = json.dumps(json.loads(zlib.decompress(json_hash).decode('utf-8')), indent = 4)
    githubURL = 'metadata/{}/ultraviolet-{}.json'.format(uv_id, uv_id)
    if_update = bool(request.args.get('update'))
    template_info = [i for i in retrieve_current_templates() if i[0] == fetch_met_fields_vals(uv_id)[0][2]][0]
    commit_text = commit_string_maker(if_update, user, template_info)

    success_push_github = uv_repo_push(githubURL, commit_text, json_string, update=if_update)
    if success_push_github:
        record_github_status(uv_id, 'https://github.com/' +
                             GH_BASEREPO + '/tree/main/' +
                             githubURL.replace('/ultraviolet.json', ''))
        flash("Successfully pushed to Github")
        return home()
    else:
        flash("There was an error in pushing to Github.")
        return render_template('general_use_template.html', title_text="An Error Occurred.")

    flash("There was an error in retrieving json.")
    return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/add-multiple-records', methods = ['POST', 'GET'])
@login_required
def addmultiples():
    uv_id = request.args.get('id')
    template_id = request.args.get('template')
    metgroupid = pluck_metgroup_num(uv_id)

    # This needed in case user fails to enter anything for number of records to make; defaults to 1
    try:
        number_new_records = int(request.form['number_new_records'])
    except:
        number_new_records = 1

    duplicate_field_vals_fieldnums = [int(i[0].split('_')[0]) for i in request.form.items() if i[0] != 'number_new_records']
    met_field_vals = fetch_met_fields_vals(uv_id)

    # Title field is given special treatment here, so we find out what the field number is for this template for title
    # If the user has not selected to duplicate the title, a placeholder title name will be created (to give list of
    # records in summary view a name to diplay

    title_field_num = pluck_title_field_num(template_id, "Title")

    try:
        for i in range(0, number_new_records):
            vals_rows = []
            new_uv_id = get_temp_random_id()[1]
            for rec in met_field_vals:
                if rec[1] in duplicate_field_vals_fieldnums:
                    insert_val = rec[6]
                    if rec[1] == title_field_num:
                        insert_val = insert_val + '(' + str(i+1) + ')'
                        record_title = insert_val
                else:
                    insert_val = ''
                    if rec[1] == title_field_num:
                        insert_val = 'Placeholder Title ' + '(' + str(i+1) + ')'
                        record_title = insert_val

                vals_rows.append((new_uv_id,
                                  rec[1],
                                  int(template_id),
                                  rec[3],
                                  rec[4],
                                  rec[5],
                                  insert_val))
            record_met_field_vals(new_uv_id, vals_rows)
            record_metgroup(new_uv_id, record_title, metgroupid)

        flash("Additional records created. Click on Project List and select Project to view list of new records.")
        return home()

    except:
        flash("There was an error in creating multiple records.")
        return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/record-delete', methods = ['GET'])
@login_required
def record_delete():
    user = User(session.get('mets_user', None))
    if user.is_admin(0):
        return abort(403)

    uv_id = request.args.get('uv_id')

    try:
        success_delete_record = delete_record(uv_id)
        if success_delete_record:
            flash("Successfully deleted record")
            return home()
        else:
            flash("There was an error in deleting record.")
            return render_template('general_use_template.html', title_text="An Error Occurred.")
    except:
        flash("There was an error in deleting record.")
        return render_template('general_use_template.html', title_text="An Error Occurred.")


""" Template management routes """

@app.route('/templates', methods = ['GET'])
def list_templates():
    try:
        template_list = retrieve_current_templates()
        if template_list:
            return render_template('template_list.html',
                                   title_text="UltraViolet Template List",
                                   template_list=template_list)
        else:
            flash("There are currently no templates.")
            return render_template('general_use_template.html', title_text="No Results")

    except:
        flash("There was an error in retrieving templates.")
        return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/templates/<templateid>', methods = ['GET'])
def retrieve_template_detail(templateid):
    template_string = open(os.path.join('met_templates', 'template_' + str(templateid), 'template_' + str(templateid) + '.json' )).read()
    return render_template('template_detail_view.html',
                           template_id = templateid,
                           template_json_string = template_string)



""" User management routes """

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/register', methods=["GET", "POST"])
def register_page():
    form = RegistrationForm(request.form)

    if request.method == "POST" and form.validate():
        email = form.email.data.lower()
        password = generate_password_hash(form.password.data)
        users_check = retrieve_user(email)

        if len(users_check) > 0:
            flash("That email address has already been registered. Please log in or select a different email address.")
            return render_template('register.html', form=form, alert=True)

        else:
            add_user = set_user(email, password, 0)
            if add_user:
                return render_template('general_use_template.html', title_text="Thanks for registering!")
            else:
                flash("An error occurred in registration. Please try again.")
                return render_template('register.html', form=form)

    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        """ Normal use of login page to log in using POST method. """
        try:
            user = User(form.email.data.lower())

            if user.check_password(form.password.data):
                login_user(user, remember=True)
                session['mets_user'] = user.id

                next = request.args.get('next')
                if next not in ['', 'metbuilder']:
                    return abort(403)
                return render_template('general_use_template.html', title_text = "Login successful!" )
            else:
                flash("Incorrect password. Please try again.")
                return render_template('login.html', form=form)

        except:
            """
            This scenario should happen only if user-provided email is
            not found, indicating a mistype or attempt to login with
            non-registered user
            """
            flash("User not found. Please try again.")
            return render_template('login.html', form=form)

    if request.method == "GET":
        """ This request occurs when a user logs out; the system redirects to login page again. """
        return render_template('login.html', form=form)

    """ Some other kind of error in landing on login page. Shouldn't normally happen. """
    flash("An error occurred during login. Please try again.")
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out.")
    return redirect(url_for('login'))


@app.route('/reset', methods=["GET", "POST"])
@login_required
def reset_page():
    form = ResetForm(request.form)

    if request.method == "POST" and form.validate():
        email = form.email.data.lower()
        new_password = generate_password_hash(form.new_password.data)

        user = User(email)
        if user.user_found:
            if user.check_password(form.password.data):

                change_user = update_user(email, new_password)
                if change_user:
                    return render_template('general_use_template.html', title_text="Password succesfully updated!")

                else:
                    flash("An error occurred in updating password. Please try again.")
                    return render_template('reset.html', form=form)

            else:
                flash("Incorrect password. Please try again.")
                return render_template('reset.html', form=form)

        else:
            flash("Email not found. Please try again.")
            return render_template('reset.html', form=form)

    return render_template("reset.html", form=form)


@app.route('/profile', methods=["GET"])
@login_required
def profile():
    try:
        email = User(session.get('mets_user', None)).email
        roles = {"0":"User", "1":"Admin", "2": "Super Admin"}
        role = str(User(session.get('mets_user', None)).access)
        return render_template("profile.html", account_email=email, role=roles[role])
    except:
        """ If user fails to be retrieved because user ID has expired, send back to login """
        form = LoginForm(request.form)
        return render_template('login.html', form=form)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ResetRequestForm(request.form)

    if request.method == "POST" and form.validate():
        email = form.email.data.lower()

        if retrieve_user(email=email) != False:
            temp_pw, expire_date, unique_token = build_reset_pw()
            if set_reset_pw(email, generate_password_hash(temp_pw), expire_date, 0, unique_token):
                send_reset_email(email, temp_pw, mail, unique_token)
                flash("A temporary password has been sent to your email address (keep an eye on your spam folder if the email does not arrive). Please check your email and enter the password below.")
                return redirect(url_for('forgot_password_check', reset_email=email, next=unique_token))
            else:
                flash("An error occurred in sending a temporary password. Please try again.")
                return render_template('forgot_password.html', form=form)
        else:
           flash("Email not found. Please try again.")
           return render_template('forgot_password.html', form=form)

    return render_template('forgot_password.html', form=form)


@app.route('/forgot_password_check', methods=['GET', 'POST'])
def forgot_password_check():
    try:
        in_email = request.args.get('reset_email').replace('%40','@')
        sent_unique_token = request.args.get('next')
        let_pass = check_unique_token(in_email, sent_unique_token)
    except:
        flash("A password reset is not available.")
        return render_template('general_use_template.html', title_text="Error in resetting password.")
    form = LoginForm(request.form, email=in_email)

    if request.method == "POST" and let_pass == True:
        user_email = form.email.data.lower()
        message = check_reset_pw(user_email, form.password.data)
        if message == True:
            return redirect(url_for('reset_forgot', next=sent_unique_token, reset_email=user_email))

        else:
            flash(message)
            if "incorrect" in message:
                return redirect(url_for('forgot_password_check', next=sent_unique_token, reset_email=user_email))
            return redirect(url_for('forgot_password'))

    """
    Initial arrival at reset password site. Since this page is not login/password protected, 
    we don't allow anyone to direct access the page as a GET without having the correct unique_token 
    attached to the user's email's reset password.
    """
    if let_pass:
        return render_template('temp_reset_login.html', form=form, next=sent_unique_token, reset_email=in_email)


@app.route('/reset_forgot', methods=['GET', 'POST'])
def reset_forgot():
    try:
        in_email = request.args.get('reset_email').replace('%40','@')
        sent_unique_token = request.args.get('next')
        let_pass = check_unique_token(in_email, sent_unique_token)
    except:
        flash("Password reset was not successful. Please try again.")
        return render_template('general_use_template.html', title_text="Error in resetting password.")

    form = ResetFormForgot(request.form)


    if request.method == "POST" and form.validate():
        new_password = generate_password_hash(form.new_password.data)
        change_user = update_user(in_email, new_password)
        if change_user:
            flash("Password succesfully updated! Please login to continue.")
            return redirect(url_for('login') )

        else:
            flash("An error occurred in updating password. Please try again.")
            return render_template('reset_forgot.html', form=form, reset_email=user_email, next=sent_unique_token)

    if let_pass:
        return render_template('reset_forgot.html', form=form, reset_email=in_email, next=sent_unique_token)

    else:
        return abort(403)


@app.route('/system-admin', methods = ['GET'])
@login_required
def system_admin():
    user = User(session.get('mets_user', None))
    if user.is_admin(0):
        return abort(403)
    try:
        list_all_users = retrieve_all_users()
        if list_all_users:
            return render_template("system.html", ls_users = list_all_users)
        else:
            flash("There was an error in retrieving system info.")
            return render_template('general_use_template.html', title_text="An Error Occurred.")
    except:
        flash("There was an error in retrieving system info.")
        return render_template('general_use_template.html', title_text="An Error Occurred.")


@app.route('/change-user', methods=['POST'])
def change_user():
    user_change = request.args.get('user')
    new_role = request.args.get('changerole')
    try:
        success_update_user_role = update_user_role(user_change, new_role)
        if success_update_user_role:
            flash("User role successfully updated")
            return render_template("system.html")
        else:
            flash("There was an error in updating user role")
            return render_template("system.html")
    except:
        flash("There was an error in updating user role")
        return render_template("system.html")


""" Error handlers """

@app.errorhandler(404)
def page_not_found(e):
    flash("Page not found.")
    return render_template('general_use_template.html', title_text = "404 Error"), 404


@app.errorhandler(403)
def forbidden_page(e):
    flash("User is not authorized to access this page.")
    return render_template('general_use_template.html', title_text = "403 Error"), 403


@app.errorhandler(500)
def page_error(e):
    flash("Page error. Please try again.")
    return render_template('general_use_template.html', title_text = "500 Error"), 500


if __name__ == '__main__':
     app.run(debug = DEBUG)
