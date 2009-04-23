<%page expression_filter="h"/> <!-- XXX -->
% if reports or actions or relates or attachments:
<table border="0" cellpadding="0">
    <tr>
        <td id="sidebar_pane" width="163" valign="top" style="padding-left: 2px">
            <table border="0" cellpadding="0" cellspacing="0" width="160" id="sidebar" style="display:none">
                % if reports:
                <tr>
                    <td>
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" class="sidebox">
                            <tr>
                                <td>
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                        <tr>
                                            <td width="8" style="background: #ac0000"/>
                                            <td width="7" style="background-color: #363636"/>
                                            <td style="color: white; font-weight: bold; font-size: 12px; background-color: #363636">${_("REPORTS")}</td>
                                            <td width="35" valign="top" style="background: url(/static/images/diagonal_left.gif) no-repeat; background-color: #666666"/>
                                            <td width="50" style="background-color: #666666"/>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
    
                            % for item in reports:
                            <tr data="${str(item)}" onclick="submit_form('action', null, getNodeAttribute(this, 'data'))">
                                <td>
                                    <a href="javascript: void(0)">${item['name']}</a>
                                </td>
                            </tr>
                            % endfor
                        </table>
                    </td>
                </tr>
                % endif
                % if actions:
                <tr>
                    <td>
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" class="sidebox">
                            <tr>
                                <td>
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                        <tr>
                                            <td width="8" style="background: #ac0000"/>
                                            <td width="7" style="background-color: #363636"/>
                                            <td style="color: white; font-weight: bold; font-size: 12px; background-color: #363636">${_("ACTIONS")}</td>
                                            <td width="35" valign="top" style="background: url(/static/images/diagonal_left.gif) no-repeat; background-color: #666666"/>
                                            <td width="50" style="background-color: #666666"/>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            % for item in actions:
                            <tr data="${str(item)}" onclick="submit_form('action', null, getNodeAttribute(this, 'data'))">
                                <td>
                                    <a href="javascript: void(0)">${item['name']}</a>
                                </td>
                            </tr>
                            % endfor
                        </table>
                    </td>
                </tr>
                % endif
                % if relates:
                <tr>
                    <td>
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" class="sidebox">
                            <tr>
                                <td>
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                        <tr>
                                            <td width="8" style="background: #ac0000"/>
                                            <td width="7" style="background-color: #363636"/>
                                            <td style="color: white; font-weight: bold; font-size: 12px; background-color: #363636">${_("LINKS")}</td>
                                            <td width="35" valign="top" style="background: url(/static/images/diagonal_left.gif) no-repeat; background-color: #666666"/>
                                            <td width="50" style="background-color: #666666"/>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            % for item in relates:
                            <tr data="${str(item)}" onclick="submit_form('relate', null, getNodeAttribute(this, 'data'), '${item.get('target', '')}')">
                                <td>
                                    <a href="javascript: void(0)">${item['name']}</a>
                                </td>
                            </tr>
                            % endfor
                        </table>
                    </td>
                </tr>
                % endif
                
                % if attachments:
                <tr>
                    <td>
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" class="sidebox">
                            <tr>
                                <td>
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                        <tr>
                                            <td width="8" style="background: #ac0000"/>
                                            <td width="7" style="background-color: #363636"/>
                                            <td style="font: verdana; color:white; font-weight:bold; font-size:12px; background-color: #363636">${_("ATTACHMENTS")}</td>
                                            <td width="42" valign="top" style="background: url(/static/images/diagonal_left.gif) no-repeat; background-color: #666666"/>
                                            <td width="50" style="background-color: #666666"/>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            % for item in attachments:
                            <tr data="${str(item)}">
                                % if item[1]:
                                <td>
                                    <a href="/attachment/save_as/${item[1]}?record=${item[0]}">${item[1]}</a>
                                </td>
                                % endif
                            </tr>
                            % endfor
                        </table>
                    </td>
                </tr>
                % endif
                
            </table>
        </td>

        <td id="sidebar_hide" valign="top">
           <img src="/static/images/sidebar_show.gif" border="0" onclick="toggle_sidebar();" style="cursor: pointer;"/>
        </td>
    </tr>
</table>
% endif
