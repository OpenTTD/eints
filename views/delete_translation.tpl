%from webtranslate.bottle import url, request
%rebase main_template title='Remove translation language ' + lname
<h1>
    <a class="eint-header-link" href="/project/{{proj_name}}">{{pdata.name}}</a>
</h1>
<hr />
<h2 class="eint-heading-icon eint-icon-document-1-remove">Delete Translation: {{lname}}</h2>
<br />
<div class="alert">
    <img class="pull-left" style="margin-right:14px; margin-top:3px;" src="{{ url('static', path='img/woocons1/Sign_Warning.png') }}">
    <div style="float-left;">
        <strong>Are you sure you want to remove {{lname}} from {{pdata.name}}?
        <br />You will not be able to undo this.</strong>
    </div>
</div>
<br />

<form action="/really_delete/{{proj_name}}/{{lname}}" method="post" enctype="multipart/form-data">
    <div class="eint-form-actions">
        <a class="btn" href="/project/{{proj_name}}">Cancel</a>
        &nbsp;&nbsp;&nbsp;&nbsp;
        <button class="btn btn-danger" type="submit"><i class="icon-white icon-remove-sign"></i> Remove {{lname}}</button>
    </div>
</form>
<br />
<br />
