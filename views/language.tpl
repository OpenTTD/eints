%rebase main_template title='language ' + language + ' in ' + proj_name
<h1 class="eint-heading-icon eint-icon-checklist">Strings for the "{{language}}" language in {{pdata.name}}</h1>
<hr />
<a class="btn pull-right" href="/download/{{proj_name}}/{{language}}"><i class="icon-download"></i> Download Lang File</a>
<div class="btn-group">
% for title, strs in strings:
    <a class="btn" href="#{{title}}">{{len(strs)}} {{title}}</a>
%end
</div>
<hr />
% for title, strs in strings:
    <h2 id="{{title}}">{{title}}</h2>
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
