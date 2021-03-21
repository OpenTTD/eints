%rebase('main_template', title='Web Translator - {} - {} ({})'.format(pmd.human_name, lng.info.name, lng.name))
%from webtranslate import data
<h1>
    <a class="eint-header-link" href="/project/{{pmd.name}}">{{pmd.human_name}}</a>
</h1>
<hr />

<h2 class="eint-heading-icon eint-icon-checklist">{{lng.info.name}} ({{lng.name}}) - Status of Strings</h2>
<a class="btn pull-right" href="/download/{{pmd.name}}/{{lng.name}}"><i class="icon-download"></i> Download Lang File</a>
<div class="btn-group">
% for s in data.STATE_DISPLAY:
    <a class="btn btn-info" href="#{{s.name}}">{{len(stored[s.code])}} {{s.name}}</a>
% end
</div>
<br />
% if is_blng and pmd.pdata.projtype.is_base_translated():
    <br />
    <center><font size=+2>Warning: Strings displayed here may have string commands that are not used in translating</font></center>
    <br />
%end
<br />
% for s in data.STATE_DISPLAY:
    % strs = stored[s.code]
    <h3 id="{{s.name}}">{{s.name}}</h3>
    <div class="well">
    % if len(strs) == 0:
        No strings in this category
    % end
    % if len(strs) > 0:
        % for sdd in strs:
            <dl>
            % if is_blng:
                <dt>{{sdd.sname}}</dt>
            % else:
                <li><a href="/string/{{pmd.name}}/{{lng.name}}/{{sdd.sname}}">{{sdd.sname}}</a></li>
            % end
            % for cdd in sdd.cases:
                <dd>({{cdd.state}}) <strong>{{cdd.get_str_casename(sdd.sname)}}</strong> :<span dir="{{lng.info.textdir}}">{{cdd.text}}</span></dd>
            % end
            </dl>
        % end
    % end
    </div>
% end
