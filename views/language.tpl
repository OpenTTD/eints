%rebase main_template title='language ' + language + ' in ' + proj_name
<h1 class="eint-heading-icon eint-icon-checklist">{{pdata.name}}: <em>{{language}}</em></h1>
<hr />
<h2>Strings</h2>
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
    % if len(strs) == 0:
        No strings in this category
    % end
    % if len(strs) > 0:
        % for sname in strs:
            % if is_blng:
                {{sname}}<br />
            % else:
                <a href="/string/{{proj_name}}/{{language}}/{{sname}}">{{sname}}</a><br />
            % end
        % end
    % end
% end
