%rebase main_template title='Create a new translation project'
<h1 class="eint-heading-icon eint-icon-add">Create a new translation project</h1>
<br />
<form class="form well" action="/newproject" method="post" enctype="multipart/form-data">
    <br />
    <fieldset style="padding-left:160px;">
        <label for="name">Project Name</label>
        <input class="input-xxlarge" type="text" id="name" name="name"/>
        <span class="help-block">Only characters A-Z, a-z, 0-9 and spaces allowed</span>
        <br />
        <br />
        <label for="url">Project Website (Optional)</label>
        <input class="input-xxlarge" type="text" id="url" name="url"/>
        <span class="help-block">A url to a website somewhere else, not here, including 'http://'</span>
        <br />
        <br />
        <div class="eint-form-actions">
            <button class="btn btn-large btn-primary" type="submit">Create Project!</button>
        </div>
    </fieldset>
</form>
