%rebase main_template title='Add a new translation language'
<h1>
    <a class="eint-header-link" href="/project/{{prjname}}">{{pdata.human_name}}</a>
</h1>
<hr />
<h2 class="eint-heading-icon eint-icon-add">Start New Translation for the {{lngname}} language</h2>
<form class="form-inline well" action="/makelanguage/{{prjname}}/{{lngname}}" method="post" enctype="multipart/form-data">
    <fieldset>
        <br />
        You are about to add the {{lngname}} language as translation language to the {{prjname}} project. Are you sure?
        <div style="width: 60%; margin-left:auto; margin-right:auto;">
        <div class="control-group">
            <button class="btn btn-primary" type="submit">Select new language</button>
        </div>
        </div>
    </fieldset>
</form>

