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
% end
% if len(pdata.languages) > 0:
    <p>
    <table border="1">
    <tr><th>Language</tr>
    <tr><td><a href="/translation/{{proj_name}}/{{base_lng.name}}">{{base_lng.name}}</a> (base language)</tr>
    % for lngname, lng in sorted(pdata.languages.items()):
        % if lng != base_lng:
            <tr><td><a href="/translation/{{proj_name}}/{{lngname}}">{{lngname}}</a> (translation)</tr>
        % end
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
