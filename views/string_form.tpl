%rebase main_template title='Editing ' + sname
<h1 class="eint-heading-icon eint-icon-document-1-edit">Edit String(s) for <a class="eint-header-link" href="/project/{{proj_name}}">{{pdata.name}}</a></h1>
<hr />
<h2>
    Lang: <a class="eint-header-link" href="/language/{{proj_name}}/{{lname}}">{{lname}}</a>
    <span class="muted pull-right">String: {{sname}}</span>
</h2>
<form class="form-horizontal well well-large" action="/string/{{proj_name}}/{{lname}}/{{sname}}" method="post" enctype="multipart/form-data">
% for tc in tcs:
    <fieldset class="well">
        <h4>{{tc.get_stringname(sname)}}</h4>
        <strong>Current base language text:</strong><br />{{tc.transl[0].current_base.text}}
        <input type="hidden" name="base" value="{{tc.transl[0].current_base.text}}"/>
        <p>
            <strong>State of the translated string:</strong>{{tc.transl[0].state}}<br />
            % if tc.transl[0].user is not None:
                Created by "{{tc.transl[0].user}}", X days ago<br />
            % end
        </p>
        <div class="control-group">
            <label class="control-label">Translation: </label>
            <div class="controls">
                <textarea class="input-xxlarge" name="text_{{tc.case}}" rows="4">{{tc.transl[0].text.text}}</textarea>
            </div>
        </div>
        % if len(tc.transl[0].errors) == 0:
            % if tc.transl[0].state == 'out-of-date':
                The current translation is correct: <input type="checkbox" name="ok_{{tc.case}}"/>
            % end
        % else:
           <p><strong>Errors:</strong></p>
            % for err in tc.transl[0].errors:
                <br />{{err[0]}}: {{err[2]}}
            % end
        % end
        % if tc.transl[0].current_base != tc.transl[0].trans_base:
            <p>Previous base language text:<br />{{tc.transl[0].trans_base.text}}</p>
        % end
        % if len(tc.transl) > 1:
            <p><strong>Previous translations:</strong></p>
            <table border="1">
                <tr>
                    <th>Who</th>
                    <th>When</th>
                    <th>Translation</th>
                </tr>
                % for tl in tc.transl[1:]:
                    <tr>
                        <td>{{tl.user}}</td>
                        <td>X ago</td>
                        <td>{{tl.text.text}}</td>
                    </tr>
                % end
            </table>
        % end
        <input class="btn btn-danger" type="reset" value="Reset all strings"/>
        <input class="btn btn-primary pull-right" type="submit" value="Send all strings (and go to next string)"/>
    </fieldset>
% end
</form>
