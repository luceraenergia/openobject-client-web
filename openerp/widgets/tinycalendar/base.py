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

import math
import time
import datetime
import xml.dom.minidom

import cherrypy

from openerp import rpc
from openerp import tools

from openerp.i18n import format
from openerp.utils import TinyDict

from openerp.widgets.interface import TinyWidget
from openerp.widgets.interface import ConcurrencyInfo

from openerp.widgets import JSLink, CSSLink

from utils import Day
from utils import parse_datetime

COLOR_PALETTE = ['#f57900', '#cc0000', '#d400a8', '#75507b', '#3465a4', '#73d216', '#c17d11', '#edd400',
                 '#fcaf3e', '#ef2929', '#ff00c9', '#ad7fa8', '#729fcf', '#8ae234', '#e9b96e', '#fce94f',
                 '#ff8e00', '#ff0000', '#b0008c', '#9000ff', '#0078ff', '#00ff00', '#e6ff00', '#ffff00',
                 '#905000', '#9b0000', '#840067', '#510090', '#0000c9', '#009b00', '#9abe00', '#ffc900',]

_colorline = ['#%02x%02x%02x' % (25+((r+10)%11)*23,5+((g+1)%11)*20,25+((b+4)%11)*23) for r in range(11) for g in range(11) for b in range(11) ]
def choice_colors(n):
    if n > len(COLOR_PALETTE):
        return _colorline[0:-1:len(_colorline)/(n+1)]
    elif n:
        return COLOR_PALETTE[:n]
    return []

class TinyEvent(TinyWidget):

    template = """<div class="calEvent" style="background-color: ${color}"
    starts="${str(starts)}" ends="${str(ends)}" record_id="${record_id}" title="${description}">${title}</div>
    """

    params = ['starts', 'ends', 'title', 'description', 'color', 'record_id']

    starts = None
    ends = None
    dayspan = 0
    color = None

    title = ''
    description = ''

    record = {}
    record_id = False

    def __init__(self, record, starts, ends, title='', description='', dayspan=0, color=None):

        super(TinyEvent, self).__init__()

        self.record = record
        self.record_id = record['id']

        if starts and ends:

            self.starts = (starts or None) and datetime.datetime(*starts[:6])
            self.ends = (ends or None) and datetime.datetime(*ends[:6])

        self.dayspan = dayspan

        self.title = title
        self.description = description
        self.color = color

class ICalendar(TinyWidget):
    """ Base Calendar calss
    """

    mode = 'month'
    date_start = None
    date_delay = None
    date_stop = None
    color_field = None
    day_length = 8
    use_search = False
    selected_day = None
    date_format = '%Y-%m-%d'

    params = ['use_search']
    member_widgets = ['concurrency_info']

    css = [CSSLink('openerp', 'tinycalendar/css/calendar.css')]
    javascript = [JSLink('openerp', 'tinycalendar/javascript/calendar_date.js'),
                  JSLink('openerp', 'tinycalendar/javascript/calendar_utils.js'),
                  JSLink('openerp', 'tinycalendar/javascript/calendar_box.js'),
                  JSLink('openerp', 'tinycalendar/javascript/calendar_month.js'),
                  JSLink('openerp', 'tinycalendar/javascript/calendar_week.js')]

    def __init__(self, model, ids, view, domain=[], context={}, options=None):

        super(ICalendar, self).__init__()

        self.info_fields = []
        self.fields = []

        self.events = {}

        self.colors = {}
        self.color_values = []

        self.calendar_fields = {}
        self.concurrency_info = None

        self.ids = ids
        self.model = model
        self.domain = domain or []
        self.context = context or {}
        self.options = options

        self.date_format = format.get_datetime_format('date')
        self.use_search = (options or None) and options.use_search

        try:
            dt = parse_datetime(options.selected_day)
            self.selected_day = Day(dt.year, dt.month, dt.day)
        except:
            pass

        proxy = rpc.RPCProxy(model)

        view_id = view.get('view_id', False)

        dom = xml.dom.minidom.parseString(view['arch'].encode('utf-8'))
        root = dom.childNodes[0]
        attrs = tools.node_attributes(root)

        self.string = attrs.get('string', '')
        self.date_start = attrs.get('date_start')
        self.date_delay = attrs.get('date_delay')
        self.date_stop = attrs.get('date_stop')
        self.color_field = attrs.get('color')
        self.day_length = int(attrs.get('day_length', 8))

        if options and options.mode:
            self.mode = options.mode
        else:
            self.mode = attrs.get('mode') or self.mode or 'month'

        self.info_fields = self.parse(root, view['fields'])

        fields = view['fields']
        fields = fields.keys() + [self.date_start, self.date_stop, self.date_delay, self.color_field]

        fields = list(set([x for x in fields if x]))

        self.fields = proxy.fields_get(fields)

        if self.color_field and options and options.colors:
            self.colors = options.colors

        if self.color_field and options and options.color_values:
            self.color_values = options.color_values

        self.calendar_fields['date_start'] = dict(name=self.date_start,
                                                  kind=self.fields[self.date_start]['type'])

        if self.date_delay:
            self.calendar_fields['date_delay'] = dict(name=self.date_delay,
                                                      kind=self.fields[self.date_delay]['type'])

        if self.date_stop:
            self.calendar_fields['date_stop'] = dict(name=self.date_stop,
                                                         kind=self.fields[self.date_stop]['type'])

        self.calendar_fields['day_length'] = self.day_length

    def parse(self, root, fields):
        """ Deraived class must override parse method
        """
        pass

    def convert(self, event):

        fields = [x for x in [self.date_start, self.date_stop] if x]

        for fld in fields:
            typ = self.fields[fld]['type']
            assert typ in ('date', 'datetime'), "Invalid field type (%s), should be either `date` or `datetime`: %s" % (typ, fld)
            fmt = format.DT_SERVER_FORMATS[typ]

            if event[fld] and fmt:
                event[fld] = time.strptime(event[fld], fmt)

            # default start time is 9:00 AM
            if typ == 'date' and fld == self.date_start:
                ds = list(event[fld])
                ds[3] = 9
                event[fld] = tuple(ds)

    def get_events(self, days):

        proxy = rpc.RPCProxy(self.model)

        #XXX: how to get events not falling between the given day range but spans the range?
        #domain = self.domain + [(self.date_start, '>', days[0].prev().isoformat()),
        #                        (self.date_start, '<', days[-1].next().isoformat())]

        first = days[0].month2.prev()[0] #HACK: add prev month
        domain = self.domain + [(self.date_start, '>', first.isoformat()),
                                (self.date_start, '<', days[-1].next().isoformat())]

        # convert color values from string to python values
        if self.color_values and self.color_field in self.fields:
            try:
                import openerp.widgets as tw
                atr = self.fields[self.color_field]
                atr['required'] = False
                wid = tw.form.WIDGETS[atr['type']](**atr)
                vals = self.color_values[:]
                for i, v in enumerate(vals):
                    try:
                        vals[i] = wid.validator.to_python(v)
                    except:
                        pass
                domain += [(self.color_field, "in", vals)]
            except Exception, e:
                pass

        if self.options and self.options.use_search:
            domain += self.options.search_domain

        ctx = rpc.session.context.copy()
        ctx.update(self.context)

        order_by = ('sequence' in self.fields or 0) and 'sequence'

        ids = proxy.search(domain, 0, 0, order_by, ctx)
        result = proxy.read(ids, self.fields.keys()+['__last_update'], ctx)
        self._update_concurrency_info(self.model, result)
        self.concurrency_info = ConcurrencyInfo(self.model, ids)
        
        if not self.color_values:
            self.colors = {}
        
        if self.color_field:

            for evt in result:
                key = evt[self.color_field]
                name = key
                value = key

                if isinstance(key, list): # M2O, XMLRPC returns List instead of Tuple
                    evt[self.color_field] = key = tuple(key)

                if isinstance(key, tuple): # M2O
                    value, name = key

                self.colors[key] = (name, value, None)

            colors = choice_colors(len(self.colors))
            for i, (key, value) in enumerate(self.colors.items()):
                self.colors[key] = (value[0], value[1], colors[i])

        events = []

        for evt in result:
            self.convert(evt)
            events += [self.get_event_widget(evt)]

        # filter out the events which are not in the range
        result = []
        for e in events:
            if e.dayspan > 0 and days[0] - e.dayspan < e.starts:
                result += [e]
            if e.dayspan == 0 and days[0] <= e.starts:
                result += [e]

        return result

    def get_event_widget(self, event):

        title = ''       # the title
        description = [] # the description
        starts = None    # the starting time (datetime)
        ends = None      # the end time (datetime)

        if self.info_fields:

            f = self.info_fields[0]
            s = event[f]

            if isinstance(s, (tuple, list)): s = s[-1]

            title = ustr(s)

            for f in self.info_fields[1:]:
                s = event[f]
                if isinstance(s, (tuple, list)): s = s[-1]

                description += [ustr(s)]

        starts = event.get(self.date_start)
        ends = event.get(self.date_delay) or 1.0
        span = 0

        if starts and ends:

            n = 0
            h = ends

            if ends == self.day_length:
                span = 1

            elif ends > self.day_length:
                n = ends / self.day_length
                h = ends % self.day_length

                n = int(math.floor(n))

                if h > 0: 
                    span = n + 1
                else:
                    span = n

            ends = time.localtime(time.mktime(starts) + (h * 60 * 60) + (n * 24 * 60 * 60))

        if starts and self.date_stop:

            ends = event.get(self.date_stop)
            if not ends:
                ends = time.localtime(time.mktime(starts) + 60 * 60)

            tds = time.mktime(starts)
            tde = time.mktime(ends)

            if tds >= tde:
                tde = tds + 60 * 60
                ends = time.localtime(tde)

            n = (tde - tds) / (60 * 60)

            if n >= self.day_length:
                span = math.ceil(n / 24)

        starts = format.format_datetime(starts, "datetime", True)
        ends = format.format_datetime(ends, "datetime", True)

        color_key = event.get(self.color_field)
        color = self.colors.get(color_key)

        title = title.strip()
        description = ', '.join(description).strip()

        return TinyEvent(event, starts, ends, title, description, dayspan=span, color=(color or None) and color[-1])


class TinyCalendar(ICalendar):

    def parse(self, root, fields):

        info_fields = []
        attrs = tools.node_attributes(root)

        for node in root.childNodes:
            attrs = tools.node_attributes(node)

            if node.localName == 'field':
                info_fields += [attrs['name']]

        return info_fields

# vim: ts=4 sts=4 sw=4 si et

