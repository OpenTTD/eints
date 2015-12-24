%from webtranslate.bottle import url, request
%rebase('main_template', title='Web Translator - {} - {} ({}) - Remove language'.format(pmd.human_name, lng.info.name, lng.name))
<h1>
    <a class="eint-header-link" href="/project/{{pmd.name}}">{{pmd.human_name}}</a>
</h1>
<hr />
<h2 class="eint-heading-icon eint-icon-document-1-remove">Delete Translation: {{lng.info.name}} ({{lng.name}})</h2>
<br />
<div class="alert">
    <img class="pull-left" style="margin-right:14px; margin-top:3px;" src="{{ url('static', path='img/woocons1/Sign_Warning.png') }}">
    <div style="float-left;">
        <strong>Are you sure you want to remove {{lng.info.name}} ({{lng.name}}) from {{pmd.human_name}}?
        <br />You will not be able to undo this.</strong>
    </div>
</div>
<br />

<form action="/really_delete/{{pmd.name}}/{{lng.name}}" method="post" enctype="multipart/form-data">
    <div class="eint-form-actions">
        <a class="btn" href="/project/{{pmd.name}}">Cancel</a>
        &nbsp;&nbsp;&nbsp;&nbsp;
        <button class="btn btn-danger" type="submit"><i class="icon-white icon-remove-sign"></i> Remove {{lng.info.name}} ({{lng.name}})</button>
    </div>
</form>
<br />
<br />
