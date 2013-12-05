%rebase main_template title='Add project details'
<h1 class="eint-heading-icon eint-icon-add">Add project details of {{prjname}}</h1>
<br />
<form class="form well" action="/makeproject/{{projtype_name}}/{{prjname}}" method="post" enctype="multipart/form-data">
    <br />
    <fieldset style="padding-left:160px;">
        <label for="name">Full project name (required)</label>
        <input class="input-xxlarge" type="text" id="humanname" name="humanname"/>
        <span class="help-block">Only characters A-Z, a-z, 0-9, plus (+), dash (-), dot (.), slash (/), and space ( ) allowed</span>
        <br />
        <br />
        <label for="url">Project website (optional)</label>
        <input class="input-xxlarge" type="text" id="url" name="url"/>
        <span class="help-block">A url to a website somewhere else, not here, including 'http://'</span>
        <br />
        <br />
        <div class="eint-form-actions">
            <button class="btn btn-large btn-primary" type="submit">Add project details!</button>
        </div>
    </fieldset>
</form>

