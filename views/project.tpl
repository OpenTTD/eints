%rebase main_template title='Web translator - ' + pdata.name
<h1 class="eint-heading-icon eint-icon-drawer-open">Overview of project {{pdata.name}}</h1>
<p>Web translator project page of {{pdata.name}}.</p>
<strong>Number of languages</strong>: {{len(pdata.languages)}}<br />
% if base_lng is None:
    <strong>Base language</strong>: None loaded
% else:
    <strong>Base language</strong>: {{base_lng.name}}<br />
    <strong>Number of strings</strong>: {{len(base_lng.changes)}}

    <table border="1">
        <tr>
            <th rowspan="2">Language
            <th colspan="5">Strings
        </tr>
        <tr>
            <th>Unknown
            <th>Correct
            <th>Outdated
            <th>Invalid
            <th>Missing
        </tr>
        <tr>
            <td><a href="/language/{{proj_name}}/{{base_lng.name}}">{{base_lng.name}}</a> (base language)
            <td>{{bcounts[0]}}
            <td>{{bcounts[1]}}
            <td>-
            <td>{{bcounts[3]}}
            <td>-
        </tr>
    % for lngname, counts in transl:
        <tr>
            <td><a href="/language/{{proj_name}}/{{lngname}}">{{lngname}}</a> (translation)
            <td>{{counts[0]}}
            <td>{{counts[1]}}
            <td>{{counts[2]}}
            <td>{{counts[3]}}
            <td>{{counts[4]}}
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
