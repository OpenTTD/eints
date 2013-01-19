<html>
<head>
<title>Web translator - {{name}} - {{lname}}</title>
</head>
<body>
<h1>Web translator - {{name}} - {{lname}}</h1>
Overview of the {{lname}} strings in the {{name}} project.
<p><table><tr><th>String name</th><th>State</th><th>Text</th></tr>
% for entry in entries:
    <tr><td>{{entry.name}}</td><td>{{entry.state}}</td><td>{{entry.text}}</td></tr>
% end
</table></p>
</body>
</html>
