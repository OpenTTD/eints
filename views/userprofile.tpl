%rebase main_template title='Web translator language overview'
<h1 class="eint-heading-icon eint-icon-drawer-closed">Profile of user '{{userauth.name}}'</h1>
% if not is_owner and len(languages) == 0:
    Sorry, you have no access to any projects.
% else:
    <table class="table table-condensed table-striped table-hover">
        <thead>
            <tr>
                <th>Project</th>
                % if is_owner:
                    <th>Manager</th>
                % end
                % for l in languages:
                    <th>{{l}}</th>
                % end
            </tr>
        </thead>
        <tbody>
        % for pmd, owner, langs in prjdata:
            <tr>
            <td><a href="/project/{{pmd.name}}">{{pmd.human_name}}</a></td>
            % if is_owner:
                <td>
                % if owner:
                  <a href="/projsettings/{{pmd.name}}">Settings</a>
                % end
                </td>
            % end
            % for lngname in languages:
                <td>
                % lang = langs.get(lngname)
                % if lang is not None:
                    % if not lang[2]:
                        No access
                    % elif lang[0]:                        
                        % if lang[1][2] > 0 or lang[1][3] > 0 or lang[1][4] > 0:
                            <a href="/translation/{{pmd.name}}/{{lngname}}">Start fixing</a>
                        % else:
                            Done!
                        % end
                    % elif lang[1][4] > 0:
                        <form style="margin-bottom: 0" action="/newlanguage/{{pmd.name}}" method="post" enctype="multipart/form-data">
                            <fieldset>
                                <input type="hidden" name="language_select" value="{{lngname}}"/>
                                <button class="btn btn-mini" type="submit">Start new</button>
                            </fieldset>
                        </form>
                    % end
                % end
                </td>
            % end
            </tr>
        % end
        </tbody>
    </table>
% end
