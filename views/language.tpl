%rebase main_template title='language ' + language + ' in ' + proj_name
<h1 class="eint-heading-icon eint-icon-checklist">
    Status of Strings for <a class="eint-header-link" href="/project/{{proj_name}}">{{pdata.name}}</a>
</h1>
<hr />

<h2>Lang: {{language}}</h2>
<a class="btn pull-right" href="/download/{{proj_name}}/{{language}}"><i class="icon-download"></i> Download Lang File</a>
<div class="btn-group">
% for title, strs in strings:
    <a class="btn btn-info" href="#{{title}}">{{len(strs)}} {{title}}</a>
%end
</div>
<br />
<br />
% for title, strs in strings:
    <h3 id="{{title}}">{{title}}</h3>
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
                <li><a href="/string/{{proj_name}}/{{language}}/{{sdd.sname}}">{{sdd.sname}}</a></li>
            % end
            % for cdd in sdd.cases:
                <dd>({{cdd.state}}) <strong>{{cdd.get_str_casename(sdd.sname)}}</strong> :{{cdd.text}}</dd>
            % end
            </dl>
        % end
    % end
    </div>
% end
