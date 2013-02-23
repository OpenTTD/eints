%rebase main_template title='Upload language for ' + proj_name
<h1>Upload Language for {{proj_name}}</h1>
<br />
<form class="form-horizontal well" action="/upload/{{proj_name}}" method="post" enctype="multipart/form-data">
    <fieldset style="margin-left:70px;">
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
                <label class="checkbox" for="is_existing" class="checkbox">
                    <input type="checkbox" name="is_existing" id="is_existing" /> Language already exists in the project
                </label>
            </div>
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
            <button class="btn btn-primary" type="submit">Upload</button>
        </div>
    </fieldset>
</form>
