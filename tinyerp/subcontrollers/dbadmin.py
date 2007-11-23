###############################################################################
#
# Copyright (c) 2007 TinyERP Pvt Ltd. (http://tinyerp.com) All Rights Reserved.
#
# $Id$
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################################################

import re

from turbogears import expose
from turbogears import widgets
from turbogears import controllers
from turbogears import redirect

import time

import cherrypy

from tinyerp import rpc
from tinyerp import common
import xmlrpclib
import base64
from tinyerp.subcontrollers import actions


class DBAdmin(controllers.Controller):

    @expose(template="tinyerp.subcontrollers.templates.dbadmin")
    def index(self):
        return dict()

    @expose(template="tinyerp.subcontrollers.templates.dbadmin_create")    
    def create(self, password=None, db_name=None, language=[], demo_data=False):
                
        if demo_data:
            demo_data = eval(demo_data)
                                            
        url = rpc.session.get_url()
        url = str(url[:-1])
        
        langlist = []
        
        try:
            langlist = rpc.session.execute_db('list_lang')
        except Exception, e:
            pass

        langlist.append(('en_EN','English'))

        if not db_name:
            return dict(url=url, langlist=langlist, message=None)

        message = None
        res = None

        if ((not db_name) or (not re.match('^[a-zA-Z][a-zA-Z0-9_]+$', db_name))):
            message = _('The database name must contain only normal characters or "_".\nYou must avoid all accents, space or special characters.') + "\n\n" + _('Bad database name !')
        else:
            try:
                res = rpc.session.execute_db('create', password, db_name, demo_data, language)
                time.sleep(5) # wait for few seconds
            except Exception, e:
                if ('faultString' in e and e.faultString=='AccessDenied:None') or str(e)=='AccessDenied':
                    message = _('Bad database administrator password !') + "\n\n" + _("Could not create database.")
                else:
                    message = _("Could not create database.") + "\n\n" + _('Error during database creation !')

            if res:
                raise redirect('/')

        return dict(url=url, langlist=langlist, message=message)

    @expose(template="tinyerp.subcontrollers.templates.dbadmin_drop")
    def drop(self, db_name=None, passwd=None):

        message=None
        res = None

        url = rpc.session.get_url()
        url = str(url[:-1])
        db = cherrypy.request.simple_cookie.get('terp_db')
        dblist = []
        
        try:
            dblist = rpc.session.execute_db('list')
        except:
            pass

        if not db_name:
            return dict(url=url, selectedDb=db, message=message, dblist=dblist)

        try:
            res = rpc.session.execute_db('drop', passwd, db_name)
        except Exception, e:
            if ('faultString' in e and e.faultString=='AccessDenied:None') or str(e)=='AccessDenied':
                message = _('Bad database administrator password !') + "\n\n" + _("Could not drop database.")
            else:
                message = _("Couldn't drop database")
        
        if res:
            raise redirect("/dbadmin")

        return dict(url=url, selectedDb=db, message=message, dblist=dblist)

    @expose(template="tinyerp.subcontrollers.templates.dbadmin_backup")
    def backup(self, password=None, dblist=None):

        url = rpc.session.get_url()
        url = str(url[:-1])
        db = cherrypy.request.simple_cookie.get('terp_db')

        dblist_load = []
        try:
            dblist_load = rpc.session.execute_db('list')
        except:
            pass

        if not dblist:
            return dict(url=url, dblist=dblist_load, selectedDb=db, message=None)

        message=None
        res = None

        try:
            res = rpc.session.execute_db('dump', password, dblist)
        except Exception, e:
            message = _("Could not create backup.")

        if res:
            cherrypy.response.headers['Content-Type'] = "application/data"
            return base64.decodestring(res)

        return dict(url=url, dblist=dblist_load, selectedDb=db, message=message)

    @expose(template="tinyerp.subcontrollers.templates.dbadmin_restore")
    def restore(self, passwd=None, new_db=None, path=None):

        url = rpc.session.get_url()
        url = str(url[:-1])
        
        if path is None:
            return dict(url=url, message=None)

        message = None
        res = None

        try:
            data_b64 = base64.encodestring(path.file.read())
            res = rpc.session.execute_db('restore', passwd, new_db, data_b64)
        except Exception, e:
            if e.faultString=='AccessDenied:None':
                message = _('Bad database administrator password !') + "\n\n" + _("Could not restore database.")
            else:
                message = _("Couldn't restore database")

        if res:
            raise redirect("/dbadmin")

        return dict(url=url, message=message)

    @expose(template="tinyerp.subcontrollers.templates.dbadmin_password")
    def password(self, new_passwd=None, old_passwd=None, new_passwd2=None):

        url = rpc.session.get_url()
        url = str(url[:-1])

        message = None
        res = None

        if not new_passwd:
            return dict(url=url, message=message)

        if new_passwd != new_passwd2:
            message = _("Confirmation password do not match new password, operation cancelled!") + "\n\n" + _("Validation Error.")
        else:
            try:
                res = rpc.session.execute_db('change_admin_password', old_passwd, new_passwd)
            except Exception,e:
                if e.faultString=='AccessDenied:None':
                    message = _("Could not change password database.") + "\n\n" + _('Bas password provided !')
                else:
                    message = _("Error, password not changed.")

        if res:
            raise redirect("/dbadmin")

        return dict(url=url, message=message)
