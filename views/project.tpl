%rebase('main_template', title='Web translator - ' + pmd.human_name)
%from webtranslate import utils
<h1>{{pmd.human_name}}</h1>
<hr />
<div class="btn-group pull-right" style="padding-top:3px;">
% if pmd.pdata.url is not '':
    <a class="btn" href="{{pmd.pdata.url}}">&#187; Project Website</a> |
% end
    <a class="btn" href="/projsettings/{{pmd.name}}"><i class="icon-cog"></i> Project Settings</a>
    <a class="btn" href="/newlanguage/{{pmd.name}}"><i class="icon-plus-sign"></i> Start New Translation</a>
    <a class="btn" href="/upload/{{pmd.name}}"><i class="icon-upload"></i> Upload Language</a>
</div>
<h2 class="eint-heading-icon eint-icon-drawer-open">Project Overview</h2>
% if base_lng is None:
    <p class="alert alert-info"><strong>To get started, please <a href="/upload/{{pmd.name}}">upload a lang file</a> to use as base language.</strong></p>
% else:
    <br />
    <br />
    <table class="table table-condensed table-striped table-hover">
        <thead>
            <tr>
                <th colspan="2">Languages ({{len(pmd.pdata.languages)}})</th>
                <th colspan="3" style="text-align:center;"><i class="icon-cog"></i> Actions</th>
                <th colspan="5" style="text-align:center;">Strings ({{len(base_lng.changes)}})</th>
            </tr>
            <tr>
                <th colspan="5"></th>
                <th class="number">Unknown</th>
                <th class="number">Correct</th>
                <th class="number">Outdated</th>
                <th class="number">Invalid</th>
                <th class="number">Missing</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><i class="icon-leaf"></i></td>
                <td><strong><a href="/translation/{{pmd.name}}/{{base_lng.name}}">{{base_lng.name}}</a></strong></td>
                <td><strong>(Base Language)</strong></td>
                <td>-</td>
                <td><a class="pull-right" href="/download/{{pmd.name}}/{{base_lng.name}}"><i class="icon-download"></i> Download</a></td>
                <td class="number"><strong>{{bcounts[0]}}</strong></td>
                <td class="number"><strong>{{bcounts[1]}}</strong></td>
                <td class="number"><strong>-</strong></td>
                <td class="number"><strong>{{bcounts[3]}}</strong></td>
                <td class="number"><strong>-</strong></td>
            </tr>
        % if len(transl) == 0:
            <tr>
                <td colspan="10" class="alert alert-info">To get started with translation, upload a language file</td>
            </tr>
        % else:
            % for lng, counts, needs_fix in transl:
                <tr>
                    <td>
                        % if not needs_fix:
                            <i class="icon-ok-circle"></i>
                        % else:
                            <i class="icon-exclamation-sign"></i>
                        % end
                    </td>
                    <td><a href="/translation/{{pmd.name}}/{{lng.name}}">{{lng.name}}</a></td>
                    % if needs_fix:
                        <td><a href="/fix/{{pmd.name}}/{{lng.name}}">Start Fixing</a></td>
                    % else:
                        <td>Done!</td>
                    % end
                    <td><a class="pull-right" href="/delete/{{pmd.name}}/{{lng.name}}"><i class="icon-remove-circle"></i> Delete</a></td>
                    <td><a class="pull-right" href="/download/{{pmd.name}}/{{lng.name}}"><i class="icon-download"></i> Download</a></td>
                    <td class="number">{{counts[0]}}</td>
                    <td class="number">{{counts[1]}}</td>
                    <td class="number">{{counts[2]}}</td>
                    <td class="number">{{counts[3]}}</td>
                    <td class="number">{{counts[4]}}</td>
                </tr>
            % end
        % end
        </tbody>
    </table>
    <br />
    <dl class="dl-horizontal">
        % for sd in utils.get_status_definition_strings():
            <dt>{{sd.name}}</dt>
            <dd>{{sd.description}}</dd>
        % end
    </dl>
%end
