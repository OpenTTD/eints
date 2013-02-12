<html>
<head>
<title>Web translator - {{pdata.name}}</title>
</head>
<body>
<h1>Overview of project {{pdata.name}}</h1>
<p>Web translator project page of {{pdata.name}}.
<p><strong>Number of languages</strong>: {{len(pdata.languages)}}<br>
% if base_lng is None:
    <strong>Base language</strong>: None
% else:
    <strong>Base language</strong>: {{base_lng.name}}<br>
    <strong>Number of strings</strong>: {{len(base_lng.changes)}}

    <p>
    <table border="1">
    <tr><th colspan="5">Language</tr>
    <tr><td colspan="5"><a href="/translation/{{proj_name}}/{{base_lng.name}}">{{base_lng.name}}</a> (base language)</tr>
    % for lngname, counts in transl:
        <tr><td><a href="/translation/{{proj_name}}/{{lngname}}">{{lngname}}</a> (translation)
            <td>{{counts[0]}}<td>{{counts[1]}}<td>{{counts[2]}}<td>{{counts[3]}}</tr>
    %end
    </table>
    <p>Where <em>missing</em> means no translation could be found, <em>invalid</em>
    means a translation exists, but its string parameters do not match with the
    base language, <em>outdated</em> means a valid translation exists, but it needs
    review as a newer base language text exists, and <em>correct</em> means the
    string is technically correct and up to date.
%end
<p>
<ul>
<li><a href="/upload/{{proj_name}}">Upload language</a>
<li>Download language
<li>Add translation language
<li>Remove translation language
<li>Edit translators
</ul>
</body>
</html>
