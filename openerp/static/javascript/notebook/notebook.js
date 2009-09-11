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

var Notebook = function(element, options) {

    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, options);
    }
  
    return this.__init__(element, options);
}

Notebook.prototype = {

    __class__: Notebook,

    repr : function() {
        return "[Notebook]";
    },
    
    toString: MochiKit.Base.forwardCall("repr"),
    
    __init__ : function(element, options) {
        this.element = MochiKit.DOM.getElement(element);
        
        if (!this.element) {
            throw "Invalid argument:" + element;
        }
        
        if (this.element.notebook) {
            return this.element.notebook;
        }
        
        this.options = MochiKit.Base.update({
            'closable': true,
            'scrollable': true,
            'remember': true,
            'onclose': null
        }, options || {});

        this.prepare();
                
        this.element.notebook = this;
        return this;
    },
    
    destroy: function() {
        MochiKit.Signal.disconnect(this.evtResize);
        MochiKit.Signal.disconnect(this.evtLeftClick);
        MochiKit.Signal.disconnect(this.evtRightClick);
        MochiKit.Signal.disconnect(this.evtStripClick);
    },

    prepare: function() {
        
        this.elemLeft = DIV({'class': 'notebook-tabs-left'});
        this.elemRight = DIV({'class': 'notebook-tabs-right'});
        this.elemWrap = DIV({'class': 'notebook-tabs-wrap'});
        this.elemStrip = UL({'class': 'notebook-tabs-strip'});
        this.elemStack = DIV({'class': 'notebook-pages'});
        
        this.cookie = '_notebook_' +  this.element.id + '_active_page';
        
        this.tabs = [];
        this.pages = [];
               
        var pages = MochiKit.Base.filter(function(e){
            return e.tagName == 'DIV';
        }, this.element.childNodes);
        

        for(var i=0; i<pages.length; i++) {
        
            var page = pages[i];
            var title = page.title || "Page " + i;
            
            this.add(title, page, false);
        }
        
        MochiKit.DOM.appendChildNodes(this.elemWrap, this.elemStrip);        
        MochiKit.DOM.appendChildNodes(this.element, 
            DIV({'class': 'notebook-tabs'},
                this.elemRight,
                this.elemLeft,
                this.elemWrap),
            this.elemStack);
            
        MochiKit.DOM.addElementClass(this.element, 'notebook');
        
        this.evtResize = MochiKit.Signal.connect(window, 'onresize', this, this.onResize);
        this.evtLeftClick = MochiKit.Signal.connect(this.elemLeft, 'onclick', this, this.onScrollLeft);
        this.evtRightClick = MochiKit.Signal.connect(this.elemRight, 'onclick', this, this.onScrollRight);
        
        this.evtStripClick = MochiKit.Signal.connect(this.elemStrip, 'onclick', this, this.onStripClick);

        this.adjustSize();
        
        var self = this;
        MochiKit.Async.callLater(0, function() {
            var i = self.options.remember ? parseInt(getCookie(self.cookie)) || 0 : 0;
            self.show(i);
        });

        showElement(this.element);

    },
    
    getTab: function(tab) {
    
        if (typeof(tab) == "number") {
            if (tab >= this.tabs.length)
                return null;
            tab = this.tabs[tab];
        }
        
        return tab;
    },
        
    getActiveTab: function() {
        return this.activeTab || null;
    },
    
    getPage: function(tab) {
        try {
            return this.pages[findIdentical(this.tabs, this.getTab(tab))];
        } catch(e){}
        return null;
    },
    
    getNext: function(tab) {
    
        var tab = this.getTab(tab);
        var i = findIdentical(this.tabs, tab);
        
        for(var j=i+1; j<this.tabs.length; j++) {
            var t = this.tabs[j];
            if (t.style.display == "none") {
                continue;
            }
            return t;
        }
        return null;
    },
    
    getPrev: function(tab) {
    
        var tab = this.getTab(tab);
        var i = findIdentical(this.tabs, tab);
        
        for(var j=i-1; j>=0; j--) {
            var t = this.tabs[j];
            if (t.style.display == "none") {
                continue;
            }
            return t;
        }
        return null;
    },
    
    add: function(title, content, activate) {
        
        var title = isUndefinedOrNull(title) ? 'Page ' + this.tabs.length : title;        
        var page = content && content.tagName == "DIV" ? content : DIV({}, content);
        
        MochiKit.DOM.addElementClass(page, 'notebook-page');
        
        var tab = LI({'class': 'notebook-tab'},
                        A({'href': 'javascript: void(0)', 'class': 'tab-title'}, 
                            SPAN(null, title)));
                            
        if (this.options.closable) {
            MochiKit.DOM.appendChildNodes(tab, 
                SPAN({'href': 'javascript: void(0)', 'class': 'tab-close'}));
                
            MochiKit.DOM.addElementClass(tab, 'notebook-tab-closable');
        }
                
        this.tabs = this.tabs.concat(tab);
        this.pages = this.pages.concat(page);
        
        MochiKit.DOM.appendChildNodes(this.elemStrip, tab);
        MochiKit.DOM.appendChildNodes(this.elemStack, page);
        
        this.show(tab, activate);
    },
    
    remove: function(tab) {
    
        var tab = this.getTab(tab);
        if (!tab) {
            return;
        }
        
        if (typeof(this.options.onclose) == "function" &&
            !this.options.onclose(this, tab)) {
            return;
        }
        
        this.hide(tab);
        
        var i = findIdentical(this.tabs, tab);
        var page = this.pages[i];
        
        this.tabs.splice(i, 1);
        this.pages.splice(i, 1);
        
        MochiKit.DOM.removeElement(tab);
        MochiKit.DOM.removeElement(page);
        
        MochiKit.Signal.signal(this, "remove", this, tab);
    },
    
    show: function(tab, activate) {
    
        var tab = this.getTab(tab);
        var activate = typeof(activate) == "undefined" ? true : activate;
        
        if (!tab || tab == this.activeTab) {
            return;
        }
        
        if (activate) {
        
            if (this.activeTab) {
                var at = this.activeTab;
                var pg = this.activePage;
                
                MochiKit.DOM.removeElementClass(at, 'notebook-tab-active');
                MochiKit.DOM.removeElementClass(pg, 'notebook-page-active');
            }
            
            var i = findIdentical(this.tabs, tab);
            var page = this.pages[i];
            
            MochiKit.DOM.addElementClass(tab, 'notebook-tab-active');
            MochiKit.DOM.addElementClass(page, 'notebook-page-active');
        }
        
        tab.style.display = "";
        
        MochiKit.Signal.signal(this, "show", this, tab);
        
        if (activate) {
            this.setActiveTab(tab);
        }
        this.adjustScroll();
    },
    
    hide: function(tab) {
    
        var tab = this.getTab(tab);
        
        if (!tab) {
            return;
        }
        
        var i = findIdentical(this.tabs, tab);
        var t = null;
        
        if (tab == this.activeTab) {
            t = this.getNext(tab) || this.getPrev(tab);
        }
            
        tab.style.display = "none";
        this.pages[i].style.display = "none";
        
        MochiKit.Signal.signal(this, "hide", this, tab);    
        
        if (t) {
            this.show(t);
        }
        this.adjustScroll();
    },
    
    setActiveTab: function(tab) {
    
        var tab = this.getTab(tab);
        if (!tab) {
            return;
        }
        
        if (this.options.scrollable) {
        
            var x = this.elemWrap.scrollLeft;
            var w = this.widthWrap;
            
            var left = getElementPosition(tab, this.elemWrap).x + x;
            var right = left + getElementDimensions(tab).w;
            
            if (left < x) {
                this.elemWrap.scrollLeft = left;
            } else if (right > (x + w)){
                this.elemWrap.scrollLeft = right - w;
            }
        }
        
        this.activeTab = tab;
        this.activePage = this.getPage(tab);
        
        if (this.options.remember) {
            setCookie(this.cookie, findIdentical(this.tabs, tab));
        }
        
        MochiKit.Signal.signal(this, "activate", this, tab);    
    },
    
    adjustScroll: function() {
    
        if (!this.options.scrollable) {
            return;
        }
    
        var w = MochiKit.Style.getElementDimensions(this.elemWrap).w;
        var t = 0;
                
        MochiKit.Iter.forEach(this.tabs, function(e){
            if (e.style.display != "none")
                t += e.offsetWidth + 2;
        });
        
        this.widthWrap = w;
        this.widthTabs = t;
        
        if (t <= w) {
        
            MochiKit.DOM.hideElement(this.elemLeft);
            MochiKit.DOM.hideElement(this.elemRight);
            MochiKit.DOM.removeElementClass(this.elemWrap, 'notebook-tabs-wrap-scrollable');
            
            this.elemWrap.scrollLeft = 0;
            
        } else {
        
            MochiKit.DOM.showElement(this.elemLeft);
            MochiKit.DOM.showElement(this.elemRight);            
            MochiKit.DOM.addElementClass(this.elemWrap, 'notebook-tabs-wrap-scrollable');
            
            var x = this.elemWrap.scrollLeft;
            var l = t - x;
            
            if (l < w) {
                this.elemWrap.scrollLeft = x - (w - l);
            } else {
                this.setActiveTab(this.activeTab);
            }
        }
    },

    adjustSize: function() {
    
        hideElement(this.elemWrap);
        var w = this.element.parentNode.clientWidth;
        setElementDimensions(this.elemWrap, {w: w});
        showElement(this.elemWrap);

        this.adjustScroll();
    },
        
    onResize: function(evt) {
        this.adjustSize();
    },
    
    onStripClick: function(evt) {
        var tab = evt.target();
        var action = MochiKit.DOM.hasElementClass(tab, 'tab-close') ? 'remove' : 'show';
        
        tab = tab.tagName == "LI" ? tab : getFirstParentByTagAndClassName(evt.target(), 'li');
        
        if (tab) {
            this[action](tab)
        }
    },
    
    onScrollRight: function(evt) {
    
        var w = this.widthTabs - this.widthWrap;
        var x = this.elemWrap.scrollLeft;
        
        var s = Math.min(w, x + 100);

        this.elemWrap.scrollLeft = s;
    },
    
    onScrollLeft: function(evt) {
    
        var x = this.elemWrap.scrollLeft;
        var s = Math.max(0, x - 100);
        
        this.elemWrap.scrollLeft = s;
    }

}

Notebook.adjustSize = function(callback) {

    var elems = MochiKit.Base.filter(function(e){
        return e.notebook;
    }, getElementsByTagAndClassName('div', 'notebook'));
    
    MochiKit.Iter.forEach(elems, function(e){
        hideElement(e.notebook.elemWrap);
    });
    
    if (typeof(callback) == "function")
        callback();
        
    MochiKit.Iter.forEach(elems, function(e){
        e.notebook.adjustSize();
    });
}

//==============================================================================

var Scroll = function (element, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, options);
    }
    this.__init__(element, options);
};

Scroll.prototype = new MochiKit.Visual.Base();

MochiKit.Base.update(Scroll.prototype, {

    __init__: function (element, /* optional */options) {
        var b = MochiKit.Base;
        var s = MochiKit.Style;
        this.element = MochiKit.DOM.getElement(element);

        options = b.update({
            side: "left",
            duration: 0.5
        }, options);

        this.start(options);
    },

    setup: function () {
        this.options.from = this.element.scrollLeft;
    },

    /** @id MochiKit.Visual.Opacity.prototype.update */
    update: function (position) {
        var prop = this.options.side == "left" ? "scrollLeft" : "scrollTop";
        this.element[prop] = parseInt(position, 10);
    }
});

// vim: ts=4 sts=4 sw=4 si et


