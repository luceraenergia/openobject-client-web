% if editable:
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td>
                <input type="hidden" ${py.attrs(attrs)}
                    id='${name}' 
                    name='${name}' 
                    value="${value}" 
                    class="${css_class}"                     
                    kind="${kind}" 
                    domain="${domain | h}" 
                    context="${ctx | h}" 
                    relation="${relation}"/>
                <input type="text" ${py.attrs(attrs)}
                    id='${name}_text' 
                    value="${text | h}" 
                    class="${css_class}"
                    kind="${kind}" 
                    relation="${relation}"/>
                % if error:
                <span class="fielderror">${error}</span>
                % endif
            </td>
            % if not inline:
            <td width="16" style="padding-left: 2px">
                <img id='${name}_open' 
                    width="16" 
                    height="16" 
                    alt="${_('Open')}" 
                    title="${_('Open a resource')}" 
                    src="/static/images/stock/gtk-open.png" 
                    style="cursor: pointer;" 
                    class="imgSelect"/>
            </td>
            % endif
            <td width="16" style="padding-left: 2px">
                % if readonly:
                <img id='${name}_select'
                    width="16" 
                    height="16" 
                    alt="${_('Search')}" 
                    title="${_('Search')}" 
                    src="/static/images/stock-disabled/gtk-find.png"/>
                % endif
                % if not readonly:
                <img id='${name}_select' 
                    width="16" 
                    height="16" 
                    alt="${_('Search')}" 
                    title="${_('Search')}" 
                    src="/static/images/stock/gtk-find.png" 
                    style="cursor: pointer;" 
                    class="imgSelect"/>
                % endif
            </td>
        </tr>
    </table>
% endif

% if editable:
    <script type="text/javascript">
        new ManyToOne('${name}');
    </script>
% endif

% if not editable and link:
    % if link=='1':
        <span kind="${kind}" id="${name}" value="${value}">
            <a href="${py.url('/form/view', model=relation, id=value)}">${text}</a>
        </span>
    % endif
    % if link=='0':
        <span kind="${kind}" id="${name}" value="${value}">${text}</span>
    % endif
% endif

% if not editable and not link == '0':
    <span>
        <span kind="${kind}" id="${name}" value="${value}">
            <a href="${py.url('/form/view', model=relation, id=value)}">${text}</a>
        </span>
    </span>
% endif
