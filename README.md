# UltraViolet Bulk Metadata Builder

A proof-of-concept Flask app to generate UV JSON metadata records and manage their push to Github

**Run/Install**
 
 <code>git clone https://github.com/</code>
 
 <code>cd ultrav-meta</code>
 
 Create and activate environment if planning to use one
 
 <code>pip install -r requirements.txt</code>
 
 <code>python app.py</code>
 
Open localhost (http://127.0.0.1:5000/). Comes with sample database (ultrav.db) with single user <code>admin@nyu.edu</code> (pw <code>12345678</code>).

**A Short List of Requirements**

 - <code>Flask==1.1.*</code> 
 - <code>Flask-Login==0.5.*</code>
 - <code>Flask-WTF==0.14.*</code>
 - <code>flask-mail==0.9.*</code>
 - <code>email_validator==1.1.*</code>
 - <code>PyGithub==1.55</code>
 - <code>beautifulsoup4==4.10.*</code>
 - <code>shortuuid==1.0.*</code>
 
**To Do:**

 - Ingest of JSON InvenioRDM met schema file to auto create template in DB
 - Auto creation of string representation of JSON schema file to enable JSON hashing
 - Ping UV to obtain UV ID for new records
 - Deletion of records, projects
 - Push records to UV via API
 - Systematic commit names to follow record creation workflow (e.g. "Initial ____", "Edit _____" etc.)
  