# -*- coding: utf-8 -*-
import datetime

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int))
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.settings.table_user_name = 'user'
auth.settings.table_group_name = 'group_role'
auth.settings.table_membership_name = 'group_membership'
auth.settings.table_permission_name = 'permission'
auth.define_tables()

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.actions_disabled.append('register')
auth.settings.login_url = URL('user', args = 'login')
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

#########################################################################
#defining some sets i need
years = []
guest_errors = None
guest_errors = []

talk_errors = None
talk_errors = []

competence_errors = None
competence_errors = []
#########################################################################
## after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)


db.define_table('category',
	Field('category',unique=True,notnull=True,label=T('Category')),
	format = '%(category)s')

db.define_table('val',
	Field('category',db.category,notnull=True,label=T('Category')),
	Field('val',notnull=True,label=T('Value')),
	Field('deleted','boolean',default=False,label=T('Deleted')))
db.val.category.requires=IS_IN_DB(db,'category.id','%(category)s')

def getCategory(val):
	row = db(db.category.category==val).select().first()

def valueNotEmpty(val):
	if(getCategory(value)==None):
		return False
	else :
		row = db(db.val.category == getCategory(val).id).select().first()
		if row!=None:
			return True
		else:
			return False

def makeYears():
	i = 0
	year = datetime.date.today().year
	while i < 100:
		i = i + 1
		years.append(year)
		year = year - 1

makeYears()

db.define_table('guest',
	Field('firstname',notnull=True,label=T('Firstname')),
	Field('familyname',notnull=True,label=T('Family name')),
	Field('birth_year','integer',notnull=True,label=T('Birth year')),
	Field('sex',db.val,notnull=True,label=T('Sex')),
	Field('national_number',notnull=True,label=T('National number')),
	Field('registration_date','date',default=request.now,label=T('Registration date')),
	Field('registrator',db.user,notnull=True,label=T('Registered by')),
	Field('age',compute=lambda r: (datetime.datetime.now().year) - int(r['birth_year']),label=T('Age')),
	format = '%(familyname)s')

db.guest.birth_year.requires=IS_IN_SET(years,zero=T('Choose One'),error_message = T('Choose a year from the list'))
db.guest.sex.requires=IS_IN_SET(["man","vrouw"],zero=T('Choose One'))

if(auth.user!=None):
	guests_User = db(db.guest.user==auth.user.id)
#programma negeert deze methode als een natgeregende hond met luizen , geen idee waarom voorlopig opgelost met een set
def createDropDownListGuests():

    if(getCategory('guest.sex')!=None and valueNotEmpty('guest.sex')):
        query = ((db.val.category == getCategory("guest.sex").id) & (db.val.deleted==False))
        db.guest.sex.requires=IS_IN_DB(db(query),'val.id','%(val)s')

    else:
        element='guest.sex'
        guest_errors.append(element)

createDropDownListGuests()



db.define_table('talk',
    Field('registrator',db.user,notnull=True,label=T('Registered by')),
    Field('guest',db.guest,notnull=True,label=T('Guest')),
    Field('date_talk','date',default=request.now,label=T('Date Talk')),
    Field('type_of_talk',db.val,notnull=True,label=T('Type of talk')),
    Field('story','text',label=T('Story')),
    format ='%(type_of_talk)s'
)

db.talk.type_of_talk.requires=IS_IN_SET(["intake","trajectbegeleiding","evaluatie"])

db.define_table('competence',
    Field('guest',db.guest,notnull=True,label=T('Guest')),
    Field('state_of_competence',db.val,notnull=True,label=T('State')),            
    Field('competence',db.val,notnull=True,label=T('Competence')),
    Field('type_of_competence',db.val,label=T('Type of competence')),
    format = '%(competence)s')

db.competence.state_of_competence.requires=IS_IN_SET(["kan","wil"])

db.define_table('action',
    Field('guest',db.guest,notnull=True,label=T('Guest')),
    Field ('guidance',db.val,label=T('Guidance')),
    Field('startdate','date',default=request.now,notnull=True,label=T('startdate')),
    Field('date_to_aim', 'date', label=('Aimdate')),
    Field('competence',db.val, label=('Competence')),
    Field('story','text',label=T('Story')),
    Field('success','boolean',label=T('Success')))
