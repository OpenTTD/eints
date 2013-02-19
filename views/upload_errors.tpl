%rebase main_template title='Upload language for ' + proj_name
<h1>Upload language for {{proj_name}}</h1>
The file that you uploaded contains errors:
<p>
% for err in errors:
    % if err[1] is not None:
        {{err[0]}} at line {{err[1] + 1}}: {{err[2]}}<br>
    % else:
        {{err[0]}}: {{err[2]}}<br>
    % end
% end
Please fix your errors first.
