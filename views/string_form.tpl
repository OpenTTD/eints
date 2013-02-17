<html>
<head>
<title>Editing {{sname}}</title>
</head>
<body>
<strong>Project</strong>: {{pdata.name}}<br>
<strong>Translation language</strong>: {{lname}}<br>
<strong>String name</strong>: {{sname}}
<form>
% for tc in tcs:
    <hr>
    <h2>{{tc.get_stringname(sname)}}</h2>
    <strong>Current base language text:</strong><br>{{tc.transl[0].current_base.text}}
    <p>
    <strong>State of the translated string:</strong>{{tc.transl[0].state}}<br>
    % if tc.transl[0].user is not None:
        Created by "{{tc.transl[0].user}}", X days ago<br>
    % end
    <textarea rows="4" cols="75">{{tc.transl[0].text.text}}</textarea><br>
    % if len(tc.transl[0].errors) == 0:
        % if tc.transl[0].state == 'out-of-date':
            The current translation is correct: <input type="checkbox" name="ok_{{tc.case}}"/>
        % end
    % else:
       <p><strong>Errors:</strong>
        % for err in tc.transl[0].errors:
            <br>{{err[0]}}: {{err[2]}}
        % end
    % end
    <p>
    % if tc.transl[0].current_base != tc.transl[0].trans_base:
        Previous base language text:<br>{{tc.transl[0].trans_base.text}}
    % end
    % if len(tc.transl) > 1:
        <p><strong>Previous translations:</strong><br>
        <table border="1">
        <tr><th>Who<th>When<th>Translation</tr>
        % for tl in tc.transl[1:]:
            <tr><td>{{tl.user}}<td>X ago<td>{{tl.text.text}}</tr>
        % end
        </table>
    % end
    <p>
    <input type="submit" value="Send all strings (and go to next string)"/>
    <input type="reset" value="Reset all strings"/>
% end
</form>
</body>
</html>
