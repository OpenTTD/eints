%rebase main_template title='Web translator language overview'
<h1 class="eint-heading-icon eint-icon-drawer-closed">State of the {{lngname}} language for all projects</h1>
% if len(prjdata) == 0:
    Currently there are no projects that use the {{lngname}} language, perhaps you can
    translate some projects?
% else:
    <table class="table table-condensed table-striped table-hover">
        <thead>
            <tr>
                <th>Project</th>
                <th><i class="icon-cog"></i> Action</th>
                <th class="number">Unknown</th>
                <th class="number">Correct</th>
                <th class="number">Outdated</th>
                <th class="number">Invalid</th>
                <th class="number">Missing</th>
            </tr>
        </thead>
        <tbody>
        % for pmd, exists, lstate in prjdata:
            <tr>
            <td><a href="/project/{{pmd.name}}">{{pmd.human_name}}</a></td>
            % if exists:
                % if lstate[2] > 0 or lstate[3] > 0 or lstate[4] > 0:
                  <td><a href="/translation/{{pmd.name}}/{{lngname}}">Start fixing</a></td>
                % else:
                  <td>Done!</td>
                % end
            % else:
                <td>
                    <form style="margin-bottom: 0" action="/newlanguage/{{pmd.name}}" method="post" enctype="multipart/form-data">
                        <fieldset>
                            <input type="hidden" name="language_select" value="{{lngname}}"/>
                            <button class="btn btn-mini" type="submit">Start new</button>
                        </fieldset>
                    </form>
                </td>
            % end
            <td class="number">{{lstate[0]}}</td>
            <td class="number">{{lstate[1]}}</td>
            <td class="number">{{lstate[2]}}</td>
            <td class="number">{{lstate[3]}}</td>
            <td class="number">{{lstate[4]}}</td>
            </tr>
        % end
        </tbody>
    </table>
% end
