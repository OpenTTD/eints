<html>
<head>
<title>Editing {{sname}}</title>
</head>
<body>
<h1>Editing string <tt>{{sname}}</tt> of the {{lname}} language in {{pdata.name}}</h1>
<p>Translation texts:
<table border="1">
<tr><th>State<th>Case<th>Text</tr>
% for cname, state, chg in case_lst:
    <tr><td>{{state}}<td>{{'none' if not cname else cname}}<td>{{'-' if chg is None else chg.new_text.text}}</tr>
% end
</table>
<p>Base language text:<br>
{{bchg.base_text.text}}
</body>
</html>
