<html>
<head>
<title>Web translator - projects</title>
</head>
<body>
<h1>Web translator - projects</h1>
<p>Projects available for translation</p>
<p><table>
   <tr><th>Project</th><th>Description</th></tr>
   % for p in projdatas:
       <tr><td><a href="projects/{{p.dir_name}}">{{p.dir_name}}</a></td>
           <td>{{p.description}}</td></tr>
   %end
   </table></p>
</body>
</html>
