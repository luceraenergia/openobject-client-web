###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
#
# $Id$
#
# Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
#
# The OpenERP web client is distributed under the "OpenERP Public License".
# It's based on Mozilla Public License Version (MPL) 1.1 with following 
# restrictions:
#
# -   All names, links and logos of Tiny, Open ERP and Axelor must be 
#     kept as in original distribution without any changes in all software 
#     screens, especially in start-up page and the software header, even if 
#     the application source code has been changed or updated or code has been 
#     added.
#
# -   All distributions of the software must keep source code with OEPL.
# 
# -   All integrations to any other software must keep source code with OEPL.
#
# If you need commercial licence to remove this kind of restriction please
# contact us.
#
# You can see the MPL licence at: http://www.mozilla.org/MPL/MPL-1.1.html
#
###############################################################################

import os
import base64

import kid
from turbogears import expose
from turbogears import controllers
from turbogears import redirect
from turbogears import validate

from openerp import rpc
from openerp.tinyres import TinyResource
from openerp.utils import TinyDict

import openerp.widgets as tw

from pyparsing import *
import form

class WikiView(controllers.Controller, TinyResource):
    path = '/wiki' 
    @expose(content_type='application/octet')
    def getImage(self, *kw, **kws):
        model = 'ir.attachment'
        field = 'datas_fname'
        file = kws.get('file').replace("'",'').strip()
        proxy = rpc.RPCProxy(model)
        ids = proxy.search([(field,'=',file), ('res_model','=','wiki.wiki')])
        res = proxy.read(ids, ['datas'])[0]
        res = res.get('datas')
        return base64.decodestring(res)
