from dotenv import load_dotenv
import os

load_dotenv()

"""
Site Settings
"""
APP_SECRET_KEY  = os.environ.get("APP_SECRET_KEY")
DEBUG           = os.environ.get("DEBUG")
SITE_ROOT       = os.environ.get("SITE_ROOT")

"""
SQLite
"""
DB              = os.environ.get("DB")

"""
Github
"""
GH_TOKEN        = os.environ.get("GH_TOKEN")
GH_BASEREPO     = os.environ.get("GH_BASEREPO")
GITUSER         = os.environ.get("GITUSER")
GITUSEREMAIL    = os.environ.get("GITUSEREMAIL")

"""
Mail
"""
MAIL_SERVER     = os.environ.get("MAIL_SERVER")
MAIL_PORT       = os.environ.get("MAIL_PORT")
MAIL_USE_TLS    = os.environ.get("MAIL_USE_TLS")
MAIL_USERNAME   = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD   = os.environ.get("MAIL_PASSWORD")

"""
Asset Paths
"""
_DIR            = os.path.join('static', 'DIRECTORY')
