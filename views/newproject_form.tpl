%rebase main_template title='Create a new translation project'
<h1>Create a new translation project</h1>
<form action="/newproject" method="post" enctype="multipart/form-data">
    <label for="name">Name (single name):</label> <input type="text" id="name" name="name"/> (letter, optionally followed by letters or digits)
    <br />
    <input type="submit" value="Create!"/>
</form>
