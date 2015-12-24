%rebase('main_template', title='Web translator language overview')
<h1 class="eint-heading-icon eint-icon-drawer-closed">Profile of user '{{userauth.name}}'</h1>
% if not is_owner and len(lnginfos) == 0:
    Sorry, you have no access to any projects.
% else:
    <table class="table table-condensed table-striped table-hover">
        <thead>
            <tr>
                <th>Project</th>
                % if is_owner:
                    <th>Manager</th>
                % end
                % for l in lnginfos:
                    <th>{{l.name}} ({{l.isocode}})</th>
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
            % for lnginfo in lnginfos:
                <td>
                % lang = langs.get(lnginfo.isocode)
                % if lang is not None:
                    % if not lang[2]:
                        No access
                    % elif lang[0]:
                        % if lang[1][2] > 0 or lang[1][3] > 0 or lang[1][4] > 0:
                            <a href="/translation/{{pmd.name}}/{{lnginfo.isocode}}">Start fixing</a>
                        % else:
                            Done!
                        % end
                    % elif lang[1][4] > 0:
                        <form style="margin-bottom: 0" action="/newlanguage/{{pmd.name}}" method="post" enctype="multipart/form-data">
                            <fieldset>
                                <input type="hidden" name="language_select" value="{{lnginfo.isocode}}"/>
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
