%rebase main_template title='Web translator - ' + pdata.name
%from webtranslate import utils
<h1 class="eint-heading-icon eint-icon-drawer-open">{{pdata.name}}</h1>
<hr />
<div class="btn-group pull-right" style="padding-top:3px;">
    <a class="btn" href="/upload/{{proj_name}}"><i class="icon-upload"></i> Upload Language</a></li>
    <a class="btn" href="#"><i class="icon-user"></i> Edit Translators</a>
</div>
<h2>Project Overview</h2>
% if base_lng is None:
    <p class="alert alert-info"><strong>To get started, please <a href="/upload/{{proj_name}}">upload a lang file</a> to use as base language.</strong></p>
% else:
    <br />
    <table class="table table-condensed table-striped table-hover">
        <thead>
            <tr>
                <th colspan="2">Languages ({{len(pdata.languages)}})</th>
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
                <td><strong><a href="/language/{{proj_name}}/{{base_lng.name}}">{{base_lng.name}}</a></strong></td>
                <td><strong>(Base Language)</strong></td>
                <td><strong>Delete</strong></td>
                <td><strong>Download</strong></td>
                <td class="number"><strong>{{bcounts[0]}}</strong></td>
                <td class="number"><strong>{{bcounts[1]}}</strong></td>
                <td class="number"><strong>-</strong></td>
                <td class="number"><strong>{{bcounts[3]}}</strong></td>
                <td class="number"><strong>-</strong></td>
            </tr>
        % for lngname, counts, needs_fix in transl:
            <tr>
                <td>
                    % if not needs_fix:
                        <i class="icon-ok-circle"></i>
                    % else:
                        <i class="icon-exclamation-sign"></i>
                    % end
                </td>
                <td><a href="/language/{{proj_name}}/{{lngname}}">{{lngname}}</a></td>
                % if needs_fix:
                    <td><a href="/fix/{{proj_name}}/{{lngname}}">Start Fixing</a></td>
                % else:
                    <td>Done!</td>
                % end
                <td>Delete</td>
                <td>Download</td>
                <td class="number">{{counts[0]}}</td>
                <td class="number">{{counts[1]}}</td>
                <td class="number">{{counts[2]}}</td>
                <td class="number">{{counts[3]}}</td>
                <td class="number">{{counts[4]}}</td>
            </tr>
        % end
        </tbody>
    </table>
    <br />

    <dl class="dl-horizontal">
        % for status in utils.get_status_definition_strings().values():
            <dt>{{status['title']}}</dt>
            <dd>{{status['description']}}</dd>
        % end
    </dl>
%end

</ul>
