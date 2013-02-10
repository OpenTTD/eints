<html>
<head>
<title>Upload language for {{proj_name}}</title>
</head>
<body>
<h1>Upload language for {{proj_name}}</h1>
<form action="/upload/{{proj_name}}" method="post" enctype="multipart/form-data">
Language file: <input type="file" name="langfile"/><br>
Language already exists in the project: <input type="checkbox" name="is_existing"/><br>
Override newer texts: <input type="checkbox" name="override"/><br>
File contains the base language: <input type="checkbox" name="base_language"/><br>
<input type="submit" value="Send changes"/>
</form>
</body>
</html>
