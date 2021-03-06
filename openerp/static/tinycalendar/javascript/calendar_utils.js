////////////////////////////////////////////////////////////////////////////////
//
// Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
//
// $Id$
//
// Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
//
// The OpenERP web client is distributed under the "OpenERP Public License".
// It's based on Mozilla Public License Version (MPL) 1.1 with following 
// restrictions:
//
// -   All names, links and logos of Tiny, Open ERP and Axelor must be 
//     kept as in original distribution without any changes in all software 
//     screens, especially in start-up page and the software header, even if 
//     the application source code has been changed or updated or code has been 
//     added.
//
// -   All distributions of the software must keep source code with OEPL.
// 
// -   All integrations to any other software must keep source code with OEPL.
//
// If you need commercial licence to remove this kind of restriction please
// contact us.
//
// You can see the MPL licence at: http://www.mozilla.org/MPL/MPL-1.1.html
//
////////////////////////////////////////////////////////////////////////////////

if (typeof(_) == "undefined") {
    _ = function(key) {return key};
}

var Browser = {

    // Is Internet Explorer?
    isIE : /msie/.test(navigator.userAgent.toLowerCase()),

    // Is Internet Explorer 6?
    isIE6 : /msie 6/.test(navigator.userAgent.toLowerCase()),

    // Is Internet Explorer 7?
    isIE7 : /msie 7/.test(navigator.userAgent.toLowerCase()),

    // Is Gecko(Mozilla) derived?
    isGecko : /gecko\//.test(navigator.userAgent.toLowerCase()),
    isGecko18 : /rv:1.8.*gecko\//.test(navigator.userAgent.toLowerCase()),
    isGecko19 : /rv:1.9.*gecko\//.test(navigator.userAgent.toLowerCase()),

    // Is Apple WebKit derived?
    isWebKit : /webkit/.test(navigator.userAgent.toLowerCase()),

    // Is opera?
    isOpera : /opera/.test(navigator.userAgent.toLowerCase())
}

function elementPosition2(elem) {
    var x = y = 0;
    if (elem.offsetParent) {
        x = elem.offsetLeft
        y = elem.offsetTop
        while (elem = elem.offsetParent) {
            x += elem.offsetLeft
            y += elem.offsetTop
        }
    }
    return {x: x, y: y};
}

///////////////////////////////////////////////////////////////////////////////

var CAL_INSTANCE = null;

var getCalendar = function(day, mode) {

    var day = day || MochiKit.DOM.getElement('_terp_selected_day').value;
    var mode = mode || MochiKit.DOM.getElement('_terp_selected_mode').value;
    
    var act = getURL('/calendar/get', {day: day, mode: mode});

    var form = document.forms['view_form'];
    var contents = formContents(form);
    var params = {};

    for(var i in contents[0]){
        var k = contents[0][i];
        var v = contents[1][i];

        params[k] = [v];
    }

    // colors
    var colors = getElementsByTagAndClassName('input', null, 'calGroups');
    var values = [];

    colors = filter(function(e){return e.checked}, colors);
    forEach(colors, function(e){
        values = values.concat(e.value);
    });

    params['_terp_colors'] = $('_terp_colors').value;
    params['_terp_color_values'] = values.join(",");

    showElement('calLoading');

    var req = Ajax.post(act, params);
    req.addCallback(function(xmlHttp){

        var d = DIV();
        d.innerHTML = xmlHttp.responseText;

        var newContainer = d.getElementsByTagName('table')[0];
        
        if (newContainer.id != 'calContainer'){
            return ;//window.location.href = '/';   
        }

        // release resources
        CAL_INSTANCE.__delete__();

        swapDOM('calContainer', newContainer);

        var ua = navigator.userAgent.toLowerCase();

        if ((navigator.appName != 'Netscape') || (ua.indexOf('safari') != -1)) {
            // execute JavaScript
            var scripts = getElementsByTagAndClassName('script', null, newContainer);
            forEach(scripts, function(s){
                eval(s.innerHTML);
            });
        }

        callLater(0, bind(CAL_INSTANCE.onResize, CAL_INSTANCE));
    });

    req.addErrback(function(e){
        log(e);
    });
}

var getMiniCalendar = function(action) {
    var req = Ajax.post(action);

    req.addCallback(function(xmlHttp){

        var d = DIV();
        d.innerHTML = xmlHttp.responseText;

        var newMiniCalendar = d.getElementsByTagName('div')[0];

        swapDOM('MiniCalendar', newMiniCalendar);
    });
}

var saveCalendarRecord = function(record_id, starts, ends){

    var params = getFormParams('_terp_concurrency_info');
    MochiKit.Base.update(params, {
        '_terp_id': record_id,
        '_terp_model': $('_terp_model').value,
        '_terp_fields': $('_terp_calendar_fields').value,
        '_terp_starts' : starts,
        '_terp_ends' : ends,
        '_terp_context': $('_terp_context').value
    });

    var req = Ajax.JSON.post('/calendar/save', params);
    return req.addCallback(function(obj){

        // update concurrency info
        for(var key in obj.info) {
            try {
                var items = getElementsByAttribute(['name', '_terp_concurrency_info'], ['value', '*=' + key]);
                var value = "('" + key + "', '" + obj.info[key] + "')";
                for(var i=0; i<items.length;i++) {
                    items[i].value = value;
                }
            }catch(e){}
        }

        return obj;
    });
}

var editCalendarRecord = function(record_id, date){

    var params = {
        'id': record_id,
        'model': $('_terp_model').value,
        'view_mode': $('_terp_view_mode').value,
        'view_ids': $('_terp_view_ids').value,
        'domain': $('_terp_domain').value,
        'context': $('_terp_context').value,
        'default_date': date
    }

    var act = getURL('/calpopup/edit', params);
    openWindow(act);
}

var copyCalendarRecord = function(record_id){

    var params = {
        '_terp_id': record_id,
        '_terp_model': $('_terp_model').value,
        '_terp_context': $('_terp_context').value
    }

    return Ajax.post('/calendar/duplicate', params);
}

// vim: ts=4 sts=4 sw=4 si et

