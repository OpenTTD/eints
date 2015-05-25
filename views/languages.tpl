%rebase('main_template', title='Web translator languages overview')
<h1 class="eint-heading-icon eint-icon-drawer-closed">Languages available for translators</h1>
% if len(lng_data) > 0:
    <table class="table table-condensed table-striped table-hover">
        <thead>
            <tr>
                <th>ISO code</th>
                <th>Name</th>
                <th>Own name</th>
            </tr>
        </thead>
        <tbody>
            % for langinfo in lng_data:
                <tr>
                    <td><a href="/language/{{langinfo.isocode}}">{{langinfo.isocode}}</td>
                    <td>{{langinfo.name}}</td>
                    <td>{{langinfo.ownname}}</td>
                </tr>
            % end
        </tbody>
    </table>
% else:
    Currently no languages information available.
% end
