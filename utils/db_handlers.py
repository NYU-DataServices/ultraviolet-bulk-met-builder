#
# Project SQLite DB Handlers
#

import sqlite3
import io
from settings import DB
from werkzeug.security import check_password_hash
from utils.emailer import check_if_expired


"""Project-level DB Handlers"""

def fetch_multiple_met_projects():
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT * FROM projects""")
            return cur.fetchall()
    except:
        return False
    finally:
        con.close()


def fetch_single_met_projects(metgroupid):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT * FROM projects WHERE metgroupid = ?""", (metgroupid,))
            return cur.fetchall()[0]
    except:
        return False
    finally:
        con.close()


def update_project_record(metgroupid, project_name):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""UPDATE projects SET project_name = ? WHERE metgroupid = ?""", (project_name, metgroupid))
            con.commit()
        return True
    except:
        return False
    finally:
        con.close()


def create_project_record(project_name, template_id):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""INSERT INTO projects (project_name, selected_template_id) VALUES (?,?)""", (project_name, template_id))
            con.commit()
        return True
    except:
        return False
    finally:
        con.close()


def fetch_met_group_records(metgroupid):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT * FROM projects WHERE metgroupid = ?""", (metgroupid,))
            project_title = cur.fetchall()[0][1]
            cur.execute("""SELECT * FROM recordsummary WHERE metgroupid = ?""", (metgroupid,))
            rows = cur.fetchall()
            return rows, project_title
    except:
        return False
    finally:
        con.close()


"""Record-level DB Handlers"""

def fetch_met_fields_vals(uv_id):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT * FROM metadata_ind_fields WHERE uv_id = ? ORDER BY rowid ASC""", (uv_id,))
            rows = cur.fetchall()
            return rows
    except:
        return False
    finally:
        con.close()


def record_metgroup(uv_id, met_title, metgroupid=False):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""INSERT OR IGNORE INTO recordsummary (uv_id,title,github_link,uv_record_link,metgroupid,sent_git) VALUES (?,?,?,?,?,?)""",
                        (uv_id,met_title,"NONE","NONE",metgroupid, 0))
            cur.execute("""UPDATE recordsummary SET title = ?, metgroupid = ? WHERE uv_id = ?""", (met_title, metgroupid, uv_id))
            con.commit()
        return True
    except:
        return False
    finally:
        con.close()


def record_met_field_vals(uv_id, vals_rows):
    """This function first deletes any previous record for that UV ID,
    then inserts most current values. Works for both newly created records
    as well as updating previous ones
    """
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""DELETE FROM metadata_ind_fields WHERE uv_id = ?""",(uv_id,) )
            for row in vals_rows:
                cur.execute("""INSERT INTO metadata_ind_fields VALUES (?,?,?,?,?,?)""", row)
            con.commit()
        return True
    except:
        return False
    finally:
        con.close()


def record_met_json(uv_id, hash_json_record):
    """Inserts the hashed JSON into JSON met record table"""
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""INSERT OR IGNORE INTO metdata_json (uv_id, json_hash) VALUES (?,?)""",(uv_id, hash_json_record) )
            cur.execute("""UPDATE metdata_json SET json_hash = ? WHERE uv_id = ?""", (hash_json_record, uv_id))
            con.commit()
        return True
    except:
        return False
    finally:
        con.close()


def pluck_title_fieldorder_num(template_id, title_label):
    """Finds index number of title field so as to identify title and allow it to be added to recordsummary table"""

    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT field_order FROM met_template_field_info WHERE template_num = ? AND parent_field = 0 AND label_name = ?""", (template_id, title_label))
            rows = cur.fetchall()
            return rows[0][0]
    except:
        return False
    finally:
        con.close()


def pluck_metgroup_num(uv_id):
    """Quick lookup of metgroupid where uv_id is known"""

    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT metgroupid FROM recordsummary WHERE uv_id = ? """, (uv_id, ))
            rows = cur.fetchall()
            return rows[0][0]
    except:
        return False
    finally:
        con.close()


def fetch_record_json(uv_id):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT * FROM metdata_json WHERE uv_id = ?""", (uv_id,))
            rows = cur.fetchall()
            return rows[0]
    except:
        return False
    finally:
        con.close()


def record_github_status(uv_id, githubURL):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""UPDATE recordsummary SET sent_git = 1, github_link = ? WHERE uv_id = ?""", (githubURL, uv_id))
            return True
    except:
        return False
    finally:
        con.close()


"""Template DB Handlers"""

def fetch_met_template(template_id):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT * FROM met_template_field_info WHERE template_num = ?""", (template_id,))
            rows = cur.fetchall()
            template_fields = []
            for row in rows:
                single_template_fields = {
                    "field_num":row[0],
                    "field_order":row[2],
                    "parent_field":row[3],
                    "field_class_type":row[4],
                    "label_name":row[5],
                    "json_name":row[6],
                    "header_val":row[7],
                    "accordion":row[8],
                    "add_row":row[9],
                    "enum_options":row[10],
                    "string_representation":row[11],
                    "children":[]
                }
                template_fields.append(single_template_fields)
            return_template_fields = {}
            for field in template_fields:
                try:
                    return_template_fields[field["field_order"]].append(field)
                except:
                    return_template_fields[field["field_order"]] = [field]
            return return_template_fields

    except:
        return False
    finally:
        con.close()


def retrieve_current_templates():
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT * FROM templates""")
            rows = cur.fetchall()
            return rows
    except:
        return False
    finally:
        con.close()


"""User management DB handlers"""

def retrieve_user(email=False, user_id=False):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            if not user_id:
                cur.execute("""SELECT * FROM users WHERE email = ?""", (email,) )
            else:
                cur.execute("""SELECT * FROM users WHERE user_id = ?""", (user_id,))
            rows = cur.fetchall()
            return rows
    except:
        return False
    finally:
        con.close()


def retrieve_all_users():
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT user_id, email, is_admin FROM users""")
            return cur.fetchall()
    except:
        return False
    finally:
        con.close()


def set_user(email, password, access):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""INSERT INTO users (email, password_hash, is_admin) VALUES (?,?,?)""",(email, password, access) )
            con.commit()
            return True
    except:
        return False
    finally:
        con.close()


def update_user(email, password):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""UPDATE users SET password_hash = ? WHERE email = ?""",(password, email) )
            con.commit()
        return True
    except:
        return False
    finally:
        con.close()


def update_user_role(user, role):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""UPDATE users SET is_admin = ? WHERE user_id = ?""",(role, user) )
            con.commit()
        return True
    except:
        return False
    finally:
        con.close()


def set_reset_pw(user_email, temp_pw, expire_date, if_used, unique_token):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""INSERT INTO user_reset (user_email, temp_password, expiration_date, if_used, unique_token) VALUES (?,?,?,?,?)""", (user_email, temp_pw, expire_date, if_used, unique_token))
            con.commit()
        return True
    except:
        return False
    finally:
        con.close()


def check_unique_token(user_email, token):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT * FROM user_reset WHERE user_email = ? ORDER BY rowid DESC LIMIT 1""", (user_email,))
            rows = cur.fetchall()
            if len(rows) == 1:
                if not check_if_expired(rows[0][2]):
                    if rows[0][4] == token:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
    except:
        return False
    finally:
        con.close()


def check_reset_pw(user_email, temp_pw):
    try:
        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("""SELECT * FROM user_reset WHERE user_email = ? ORDER BY rowid DESC LIMIT 1""", (user_email,))
            rows = cur.fetchall()
            print(rows)
            if len(rows) == 1 and rows[0][3] != 1:
                if not check_if_expired(rows[0][2]):
                    if check_password_hash(rows[0][1], temp_pw):
                        cur.execute("""UPDATE user_reset SET if_used = 1 WHERE user_email = ? AND expiration_date = ?""", (rows[0][0],rows[0][2]))
                        return True
                    else:
                        return "Temporary password was incorrect, try entering again."
                else:
                    return "Temporary password has expired. Please request a password reset again."
            else:
                return "No temporary password was set or it has already been used. Please request a password reset again."
    except:
        return "A problem occurred with finding your account. Please try entering again."
    finally:
        con.close()