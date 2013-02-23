%rebase main_template title='Upload language for ' + proj_name
<h1>Upload language for {{proj_name}}</h1>
<form action="/upload/{{proj_name}}" method="post" enctype="multipart/form-data">
    <label for="langfile">Language file:</label> <input type="file" name="langfile" id="langfile" /><br />
    <label for="override">Override newer texts:</label> <input type="checkbox" name="override" id="override" /><br />
    <label for="base_language">File contains the base language:</label> <input type="checkbox" name="base_language" id="base_language" /><br />
    <input type="submit" value="Send changes"/>
</form>
