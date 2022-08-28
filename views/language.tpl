%rebase('main_template', title='Web Translator - {} ({})'.format(lnginfo.name, lnginfo.isocode))
%from webtranslate import utils, data
<h1 class="eint-heading-icon eint-icon-drawer-closed">State of the {{lnginfo.name}} ({{lnginfo.isocode}}) language for all projects</h1>
% if len(prjdata) == 0:
    Currently there are no projects that use the {{lnginfo.name}} ({{lnginfo.isocode}}) language, perhaps you can
    translate some projects?
% else:
    <table class="table table-condensed table-striped table-hover">
        <thead>
            <tr>
                <th>Project</th>
                <th><i class="icon-cog"></i> Action</th>
                % for s in reversed(data.STATE_DISPLAY):
                    <th class="number">{{s.name}}</th>
                % end
            </tr>
        </thead>
        <tbody>
        % for pmd, exists, lstate in prjdata:
            <tr>
            <td><a href="/translation/{{pmd.name}}/{{lnginfo.isocode}}">{{pmd.human_name}}</a></td>
            % if exists:
                % if utils.lang_needs_fixing(lstate):
                  <td><a href="/fix/{{pmd.name}}/{{lnginfo.isocode}}">Start fixing</a></td>
                % else:
                  <td>Done!</td>
                % end
                % for s in reversed(data.STATE_DISPLAY):
                    <td class="number">{{lstate[s.code]}}</td>
                % end
            % else:
                <td>
                    % if not utils.lang_is_empty(lstate):
                        <form style="margin-bottom: 0" action="/newlanguage/{{pmd.name}}" method="post" enctype="multipart/form-data">
                            <fieldset>
                                <input type="hidden" name="language_select" value="{{lnginfo.isocode}}"/>
                                <button class="btn btn-mini" type="submit">Start new</button>
                            </fieldset>
                        </form>
                    % end
                </td>
                % for s in reversed(data.STATE_DISPLAY):
                    % if lstate[s.code] > 0:
                        <td class="number">{{lstate[s.code]}}</td>
                    % else:
                        <td class="number"></td>
                    % end
                % end
            % end
            </tr>
        % end
        </tbody>
    </table>
% end
