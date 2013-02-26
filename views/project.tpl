%rebase main_template title='Web translator - ' + pdata.name
<h1 class="eint-heading-icon eint-icon-drawer-open">{{pdata.name}}</h1>
<h3>Project Overview</h3>
% if base_lng is None:
    <p class="alert alert-info"><strong>To get started, please <a href="/upload/{{proj_name}}">upload a lang file</a> to use as base language.</strong></p>
% else:
    <table border="1">
        <tr>
            <th rowspan="2">Languages ({{len(pdata.languages)}})
            <th colspan="5">Strings ({{len(base_lng.changes)}})
            <th rowspan="2">Links
        </tr>
        <tr>
            <th>Unknown
            <th>Correct
            <th>Outdated
            <th>Invalid
            <th>Missing
        </tr>
        <tr>
            <td><strong><a href="/language/{{proj_name}}/{{base_lng.name}}">{{base_lng.name}}</a> (base language)</strong>
            <td><strong>{{bcounts[0]}}</strong>
            <td><strong>{{bcounts[1]}}</strong>
            <td><strong>-</strong>
            <td><strong>{{bcounts[3]}}</strong>
            <td><strong>-</strong>
            <td><strong>-</strong>
        </tr>
    % for lngname, counts in transl:
        <tr>
            <td><a href="/language/{{proj_name}}/{{lngname}}">{{lngname}}</a> (translation)
            <td>{{counts[0]}}
            <td>{{counts[1]}}
            <td>{{counts[2]}}
            <td>{{counts[3]}}
            <td>{{counts[4]}}
            <td><a href="/fix/{{proj_name}}/{{lngname}}">Start fixing</a>
        </tr>
    %end
    </table>
    <p>Where
    <em>Unknown</em> means the state of the translation was not decidable,
    <em>Correct</em> means the string is technically correct and up to date,
    <em>Outdated</em> means a valid translation exists, but it needs review as a newer base language text exists,
    <em>Invalid</em> means a translation exists, but its string parameters do not match with the base language, and
    <em>Missing</em> means no translation could be found.
%end
<ul>
    <li><a href="/upload/{{proj_name}}">Upload language</a>
    <li>Download language
    <li>Remove translation language
    <li>Edit translators
</ul>
