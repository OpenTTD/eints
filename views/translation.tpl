<html>
<head>
<title>{{language}} translation of "{{project}}"</title>
</head>
<body>
<h1>Translation of {{blng.name}} to {{language}} in "{{project}}"</h1>
% for sname, bchg, case_lst in strings:
    <h3>{{sname}}</h3>
    <table border="1">
    <tr><th>State<th>Case<th>Text</tr>
    % for cname, state, chg in case_lst:
        <tr><td>{{state}}<td>{{cname}}<td>{{'-' if chg is None else chg.new_text.text}}</tr>
    % end
    </table>
% end
</body>
</html>
