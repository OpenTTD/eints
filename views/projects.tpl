%rebase main_template title='Web translator projects'
<h1 class="eint-heading-icon eint-icon-drawer-closed">Projects available for translation</h1>
% if len(projects) > 0:
    <ul>
    % for p in projects:
        <li><a href="project/{{p.name}}">{{p.human_name}}</a></li>
    % end
    </ul>
% else:
    Currently no projects available, <a href="/newproject">create one</a>
% end
