%rebase main_template title='Upload language for ' + pdata.name
<h1 class="eint-heading-icon eint-icon-lang-upload">Upload Language for <a class="eint-header-link" href="/project/{{proj_name}}">{{pdata.name}}</a></h1>
<br />
<form class="form-horizontal well" action="/upload/{{proj_name}}" method="post" enctype="multipart/form-data">
    <fieldset style="margin-left:100px;"><!-- center-weight the form - no harm doing this with inline style -->
        <br />
        <br />
        <div class="control-group">
            <div class="controls">
                <label class="eint-file-upload" for="langfile">Language file: &nbsp;</label>
                <input type="file" name="langfile" id="langfile" />
            </div>
        </div>

        <div class="control-group">
            <div class="controls">
                 <label class="checkbox" for="override" class="checkbox">
                    <input type="checkbox" name="override" id="override" /> Override newer texts
                </label>
            </div>
            <div class="controls">
                <label class="checkbox" for="base_language" class="checkbox">
                    <input type="checkbox" name="base_language" id="base_language" /> File contains the base language
                </label>
            </div>
        </div>

        <div class="eint-form-actions">
            <button class="btn btn-primary btn-large" type="submit">Upload</button>
        </div>
    </fieldset>
</form>
