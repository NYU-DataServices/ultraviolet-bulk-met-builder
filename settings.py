import os


"""
Site Settings
"""
APP_SECRET_KEY = ''
DEBUG = True
SITE_ROOT = 'https://URL-ROOT'

"""
SQLite
"""
DB = "ultrav.db"

"""
Github
e.g.
GH_BASEREPO= 'NYU-DataServices/ultraviolet-metadata'
"""
GH_TOKEN = 'PERSONAL-ACCESS-TOKEN'
GH_BASEREPO = 'PATH-TO-REPO-EXCLUDING-GH-ROOT-URL'
GITUSER = 'GITHUB-USERNAME'
GITUSEREMAIL = 'GITHUB-USER-EMAIL'

"""
Mail
"""
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587 # Or use 465
MAIL_USE_TLS = True
MAIL_USERNAME = 'USER-EMAIL@gmail.com'
MAIL_PASSWORD = ''

"""
Asset Paths
"""
_DIR = os.path.join('static', 'DIRECTORY')
