%rebase('main_template', title='Upload language for ' + pmd.human_name)
<h1 class="eint-heading-icon eint-icon-warning">Upload Language for {{pmd.human_name}}</h1>
<p class="alert alert-error">The file that you uploaded contains errors</p>
<ul>
% for err in errors:
    % if err.line is not None:
        <li>{{err.type}} at line {{err.line + 1}}: {{err.msg}}</li>
    % else:
        <li>{{err.type}}: {{err.msg}}</li>
    % end
% end
</ul>
<p><strong>Please fix these errors and try again :)</strong></p>
