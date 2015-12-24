%rebase('main_template', title='Upload ' + lnginfo.name + ' (' + lnginfo.isocode + ') language for ' + pmd.human_name)
<h1>
    <a class="eint-header-link" href="/project/{{pmd.name}}">{{pmd.human_name}}</a>
</h1>
<hr />
<h2 class="eint-heading-icon eint-icon-document-1-upload">Upload {{lnginfo.name}} ({{lnginfo.isocode}}) language</h2>
<form class="form-horizontal well" action="/upload/{{pmd.name}}/{{lnginfo.isocode}}" method="post" enctype="multipart/form-data">
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
