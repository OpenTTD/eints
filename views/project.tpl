%rebase main_template title='Web translator - ' + pdata.name
<h1 class="eint-heading-icon eint-icon-drawer-open">{{pdata.name}}</h1>
<hr />
<div class="btn-group pull-right" style="padding-top:3px;">
    <a class="btn" href="/upload/{{proj_name}}"><i class="icon-circle-arrow-up"></i> Upload Language</a></li>
    <a class="btn" href="#"><i class="icon-user"></i> Edit Translators</a>
</div>
<h2>Project Overview</h2>
% if base_lng is None:
    <p class="alert alert-info"><strong>To get started, please <a href="/upload/{{proj_name}}">upload a lang file</a> to use as base language.</strong></p>
% else:
    <br />
    <table border="1">
        <thead>
            <tr>
                <th rowspan="2">Languages ({{len(pdata.languages)}})</th>
                <th colspan="5">Strings ({{len(base_lng.changes)}})</th>
                <th rowspan="2">Actions</th>
            </tr>
            <tr>
                <th>Unknown</th>
                <th>Correct</th>
                <th>Outdated</th>
                <th>Invalid</th>
                <th>Missing</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong><a href="/language/{{proj_name}}/{{base_lng.name}}">{{base_lng.name}}</a> (base language)</strong></td>
                <td><strong>{{bcounts[0]}}</strong></td>
                <td><strong>{{bcounts[1]}}</strong></td>
                <td><strong>-</strong></td>
                <td><strong>{{bcounts[3]}}</strong></td>
                <td><strong>-</strong></td>
                <td><strong>Delete | Download</strong></td>
            </tr>
        % for lngname, counts in transl:
            <tr>
                <td><a href="/language/{{proj_name}}/{{lngname}}">{{lngname}}</a> (translation)</td>
                <td>{{counts[0]}}</td>
                <td>{{counts[1]}}</td>
                <td>{{counts[2]}}</td>
                <td>{{counts[3]}}</td>
                <td>{{counts[4]}}</td>
                <td><a href="/fix/{{proj_name}}/{{lngname}}">Start fixing</a> | Delete | Download</td>
            </tr>
        %end
        </tbody>
    </table>
    <br />
    <dl>
        <dt>Unknown</dt>
        <dd>means the state of the translation was not decidable</dd>
        <dt>Correct</dt>
        <dd>means the string is technically correct and up to date</dd>
        <dt>Outdated</dt>
        <dd>means a valid translation exists, but it needs review as a newer base language text exists</dd>
        <dt>Invalid</dt>
        <dd>means a translation exists, but its string parameters do not match with the base language, and</dd>
        <dt>Missing</dt>
        <dd>means no translation could be found</dd>
    </dl>
%end

</ul>
