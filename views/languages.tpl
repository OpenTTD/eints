%rebase main_template title='Web translator languages overview'
<h1 class="eint-heading-icon eint-icon-drawer-closed">Languages state for the projects</h1>
% if len(lng_data) > 0:
    <ul>
    % for lngname in lng_data:
        <li><a href="/language/{{lngname}}">{{lngname}}</li>
    % end
    </ul>
% else:
    Currently no languages information available.
% end
