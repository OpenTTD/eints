%rebase main_template title='Create a new translation project'
<h1>Create a new translation project</h1>
<br />
<form class="form-inline well" action="/newproject" method="post" enctype="multipart/form-data">
    <fieldset>
        <label for="name">Name (single name):</label> <input type="text" id="name" name="name"/> (letter, optionally followed by letters or digits)
        <div class="pull-right">
            <button class="btn btn-primary" type="submit">Create Project!</button>
        </div>
    </fieldset>
</form>
