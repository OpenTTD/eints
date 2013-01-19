<html>
<head>
<title>Web translator - {{name}}</title>
</head>
<body>
<h1>Web translator - {{name}}</h1>
<p>Web translator project page of {{name}}.</p>
<p>Description: {{project.description}}</p>
% if project.website is not None:
    <p>Website: <a href="{{project.website}}">{{project.website}}</a></p>
% end
% if len(project.languages) > 0:
    <table><tr><th>Language</th><tr>
%   for lang in sorted(p.lang_name for p in project.languages.values()):
        <tr><td><a href="../languages/{{name}}/{{lang}}">{{lang}}</a></td></tr>
%   end
    </table></p>
% end
</body>
</html>
