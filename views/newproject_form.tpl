%rebase main_template title='Create a new translation project'
<h1>Create a new translation project</h1>
<form action="/newproject" method="post" enctype="multipart/form-data">
    Name (single name): <input type="text" name="name"/> (letter, optionally followed by letters or digits)<br />
    <input type="submit" value="Create!"/>
</form>
