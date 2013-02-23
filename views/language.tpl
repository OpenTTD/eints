%rebase main_template title='language ' + language + ' in ' + proj_name
<h1 class="eint-heading-icon eint-icon-checklist">Overview of the "{{language}}" language in {{pdata.name}}</h1>
<a href="/download/{{proj_name}}/{{language}}">Download</a>
% for title, strs in strings:
    % if len(strs) > 0:
        <h2>{{title}}</h2>
        % for sname in strs:
            % if is_blng:
                {{sname}}<br />
            % else:
                <a href="/string/{{proj_name}}/{{language}}/{{sname}}">{{sname}}</a><br />
            % end
        % end
    % end
% end
