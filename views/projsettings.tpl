%rebase('main_template', title='Web translator - ' + pmd.human_name)
<h1>
    <a class="eint-header-link" href="/project/{{pmd.name}}">{{pmd.human_name}}</a>
</h1>
<hr />
<h2 class="eint-heading-icon eint-icon-settings">Project Settings</h2>
<form class="form-horizontal well well-large" action="/projsettings/{{pmd.name}}" method="post" enctype="multipart/form-data">
    <fieldset style="padding-left:160px;">
        <label for="name">Full project name (required)</label>
        <input class="input-xxlarge" type="text" id="name" name="name" value="{{pmd.human_name}}"/>
        <span class="help-block">Only characters A-Z, a-z, 0-9, plus (+), dash (-), and space ( ) allowed</span>
        <br />
        <br />
        <label for="url">Project website (optional)</label>
        <input class="input-xxlarge" type="text" id="url" name="url" value="{{pmd.pdata.url}}"/>
        <span class="help-block">A url to a website somewhere else, not here, including 'http://'</span>
        <br />
        <br />
        <div class="eint-form-actions">
            <input class="btn btn-primary pull-right" type="submit" value="Save Changes"/>
        </div>
    </fieldset>
</form>
