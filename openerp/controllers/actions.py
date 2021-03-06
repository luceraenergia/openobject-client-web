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

"""This module implementes action methods.
"""

import time
import datetime
import base64

import cherrypy

from openerp import rpc
from openerp import tools
from openerp import common

from form import Form
from tree import Tree
from wizard import Wizard
from selection import Selection

from openerp.utils import TinyDict

def execute_window(view_ids, model, res_id=False, domain=None, view_type='form', context={},
                   mode='form,tree', name=None, target=None, limit=None):
    """Performs `actions.act_window` action.

    @param view_ids: view ids
    @param model: a model for which the action should be performed
    @param res_id: resource id
    @param domain: domain
    @param view_type: view type, eigther `form` or `tree`
    @param context: the context
    @param mode: view mode, eigther `form,tree` or `tree,form` or None

    @return: view (mostly XHTML code)
    """

    params = TinyDict()

    params.model = model
    params.ids = res_id
    params.view_ids = view_ids
    params.domain = domain or []
    params.context = context or {}
    params.limit = limit
    
    if name:
        params.context['_terp_view_name'] = name
    
    if params.ids and not isinstance(params.ids, list):
        params.ids = [params.ids]

    params.id = (params.ids or False) and params.ids[0]

    mode = mode or view_type

    if view_type == 'form':
        mode = mode.split(',')
        params.view_mode=mode

        return Form().create(params)

    elif view_type == 'tree':
        return Tree().create(params)

    else:
        raise common.message(_("Invalid View!"))

def execute_wizard(name, **datas):
    """Executes given wizard with the given data

    @param name: name of the wizard
    @param datas: datas

    @return: wizard view (mostly XHTML code)
    """
    params = TinyDict()
    params.name = name
    params.datas = datas
    params.state = 'init'

    return Wizard().create(params)

PRINT_FORMATS = {
     'pdf' : 'application/pdf',
     'doc' : 'application/vnd.ms-word',
     'html': 'text/html',
     'sxw' : 'application/vnd.sun.xml.writer',
     'odt' : 'application/vnd.oasis.opendocument.text',
     'ods' : 'application/vnd.oasis.opendocument.spreadsheet',
     'xls' : 'application/vnd.ms-excel',
     'doc' : 'application/msword',
     'csv' : 'text/csv',
     'rtf' : 'application/rtf',
     'txt' : 'text/plain',
}

def _print_data(data):

    if 'result' not in data:
        raise common.message(_('Error no report'))

    if data.get('code','normal')=='zlib':
        import zlib
        content = zlib.decompress(base64.decodestring(data['result']))
    else:
        content = base64.decodestring(data['result'])

    cherrypy.response.headers['Content-Type'] = PRINT_FORMATS[data['format']]
    return content

def execute_report(name, **data):
    """Executes a report with the given data, on success returns `application/pdf` data

    @param name: name of the report
    @param data: report data

    @return: `application/pdf` data
    """
    datas = data.copy()
    ids = datas['ids']
    del datas['ids']

    if not ids:
        ids =  rpc.session.execute('object', 'execute', datas['model'], 'search', [])
        if ids == []:
            raise common.message(_('Nothing to print!'))

        datas['id'] = ids[0]

    try:
        ctx = dict(rpc.session.context)
        ctx.update(datas.get('context', {}))
        report_id = rpc.session.execute('report', 'report', name, ids, datas, ctx)
        state = False
        attempt = 0
        while not state:
            val = rpc.session.execute('report', 'report_get', report_id)
            state = val['state']
            if not state:
                time.sleep(1)
                attempt += 1
            if attempt>200:
                raise common.message(_('Printing aborted, too long delay!'))

        # report name
        report_name = 'report'
        report_type = val['format']

        if name != 'custom':
            proxy = rpc.RPCProxy('ir.actions.report.xml')
            res = proxy.search([('report_name','=', name)])
            if res:
                report_name = proxy.read(res[0], ['name'])['name']

        report_name = report_name.replace('Print ', '')
        cherrypy.response.headers['Content-Disposition'] = 'filename="' + report_name + '.' + report_type + '"';

        return _print_data(val)

    except rpc.RPCException, e:
        raise e

def execute(action, **data):
    """Execute the action with the provided data. for internal use only.

    @param action: the action
    @param data: the data

    @return: mostly XHTML code
    """

    if 'type' not in action:
        #XXX: in gtk client just returns to the caller
        #raise common.error('Error', 'Invalid action...')
        return

    # update context with that of the action
    data.setdefault('context', {}).update(tools.expr_eval(action.get('context','{}'), data.get('context', {}).copy()))

    if action['type'] == 'ir.actions.act_window_close':
        return """<html>
        <head>
            <script type="text/javascript">
                window.onload = function(evt){
                    if (window.opener) {
                        window.opener.setTimeout("window.location.reload()", 0);
                        window.close();
                    } else {
                        window.location.href = '/';
                    }
                }
            </script>
        </head>
        <body></body>
        </html>
        """

    elif action['type']=='ir.actions.act_window':
        for key in ('res_id', 'res_model', 'view_type','view_mode', 'limit'):
            data[key] = action.get(key, data.get(key, None))
            
        if not data.get('limit'):
            data['limit'] = 80

        view_ids=False
        if action.get('views', []):
            if isinstance(action['views'], list):
                view_ids=[x[0] for x in action['views']]
                data['view_mode']=",".join([x[1] for x in action['views']])
            else:
                if action.get('view_id', False):
                    view_ids=[action['view_id'][0]]
        elif action.get('view_id', False):
            view_ids=[action['view_id'][0]]

        if not action.get('domain', False):
            action['domain']='[]'

        ctx = data.get('context', {}).copy()
        ctx.update({'active_id': data.get('id', False), 'active_ids': data.get('ids', []),'active_model':data.get('model', False)})
        ctx.update(tools.expr_eval(action.get('context', '{}'), ctx.copy()))
        
        # save active_id in session
        rpc.session.active_id = data.get('id')

        a = ctx.copy()
        a['time'] = time
        a['datetime'] = datetime
        domain = tools.expr_eval(action['domain'], a)

        if data.get('domain', False):
            domain.append(data['domain'])

        res = execute_window(view_ids,
                             data['res_model'],
                             data['res_id'],
                             domain,
                             action['view_type'],
                             ctx, data['view_mode'],
                             name=action.get('name'),
                             target=action.get('target'),
                             limit=data.get('limit'))
        
        return res

    elif action['type']=='ir.actions.server':

        ctx = data.get('context', {}).copy()
        ctx.update({'active_id': data.get('id', False), 'active_ids': data.get('ids', [])})

        res = rpc.RPCProxy('ir.actions.server').run([action['id']], ctx)
        if res:
            if not isinstance(res, list):
                res = [res]

            output = None
            for r in res:
                output = execute(r, **data)
            return output

    elif action['type']=='ir.actions.wizard':
        if 'window' in data:
            del data['window']
            
        ctx1 = data.get('context', {}).copy()
        ctx2 = action.get('context', {}).copy()

        ctx1.update(ctx2)

        data['context'] = ctx1
        
        return execute_wizard(action['wiz_name'], **data)

    elif action['type']=='ir.actions.report.custom':
        data.update(action.get('datas',{}))
        data['report_id'] = action['report_id']
        return execute_report('custom', **data)

    elif action['type']=='ir.actions.report.xml':
        data.update(action.get('datas',{}))
        return execute_report(action['report_name'], **data)

    elif action['type']=="ir.actions.act_url":
        data['url'] = action['url']
        data['target'] = action['target']
        data['type'] = action['type']

        return execute_url(**data)

def execute_url(**data):
    url = data.get('url') or ''

    if not ('://' in url or url.startswith('/')):
        raise common.message(_('Relative URLs are not supported!'))

    raise tools.redirect(url)

def get_action_type(act_id):
    """Get the action type for the given action id.

    @param act_id: the action id
    @return: action type
    """
    res = rpc.session.execute('object', 'execute', 'ir.actions.actions', 'read', act_id, ['type'], rpc.session.context)

    if not (res and len(res)):
        raise common.message(_('Action not found!'))

    return res['type']

def execute_by_id(act_id, type=None, **data):
    """Perforns the given action of type `type` with the provided data.

    @param act_id: the action id
    @param type: action type
    @param data: the data

    @return: JSON object or XHTML code
    """

    if type==None:
        type = get_action_type(act_id)
    ctx = {}
    ctx.update(rpc.session.context.copy())
    ctx.update(data.get('context') or {})    
    res = rpc.session.execute('object', 'execute', type, 'read', act_id, False, ctx)
    return execute(res, **data)

def execute_by_keyword(keyword, adds={}, **data):
    """Performs action represented by the given keyword argument with given data.

    @param keyword: action keyword
    @param data: action data

    @return: XHTML code
    """
    ctx = dict(data.get('context', {}), **rpc.session.context)
    actions = None
    if 'id' in data:
        try:
            id = data.get('id', False)
            if (id != False): id = int(id)
            actions = rpc.session.execute('object', 'execute', 'ir.values', 'get', 'action', keyword, [(data['model'], id)], False, ctx)
            actions = map(lambda x: x[2], actions)
        except rpc.RPCException, e:
            raise e

    keyact = {}
    for action in actions:
        keyact[action['name']] = action

    keyact.update(adds)

    if not keyact:
        raise common.message(_('No action defined!'))

    if len(keyact) == 1:
        key = keyact.keys()[0]
        return execute(keyact[key], **data)
    else:
        return Selection().create(keyact, **data)

# vim: ts=4 sts=4 sw=4 si et

