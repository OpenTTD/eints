%rebase main_template title='Upload language for ' + proj_name
<h1 class="eint-heading-icon eint-icon-warning">Upload Language for {{proj_name}}</h1>
<p class="alert alert-error">The file that you uploaded contains errors</p>
<ul>
% for err in errors:
    % if err[1] is not None:
        <li>{{err[0]}} at line {{err[1] + 1}}: {{err[2]}}</li>
    % else:
        <li>{{err[0]}}: {{err[2]}}</li>
    % end
% end
</ul>
<p><strong>Please fix these errors and try again :)</strong></p>
