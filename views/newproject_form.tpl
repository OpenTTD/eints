%rebase main_template title='Create a new translation project'
<h1 class="eint-heading-icon eint-icon-add">Create a new translation project</h1>
<br />
<form class="form well" action="/createproject" method="post" enctype="multipart/form-data">
    <br />
    <fieldset style="padding-left:160px;">
        <label for="name">Project identifier (required)</label>
        <input class="input-xxlarge" type="text" id="name" name="name"/>
        <span class="help-block">Only characters A-Z, a-z, 0-9 and dash (-) allowed</span>
        <br />
        <br />
        <div class="eint-form-actions">
            <button class="btn btn-large btn-primary" type="submit">Create Project!</button>
        </div>
    </fieldset>
</form>
