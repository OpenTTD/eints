%rebase main_template title='Upload language for ' + pdata.human_name
<h1>
    <a class="eint-header-link" href="/project/{{proj_name}}">{{pdata.human_name}}</a>
</h1>
<hr />
<h2 class="eint-heading-icon eint-icon-document-1-upload">Upload Language</h2>
Please select which language you want to upload.
<br />
% for liso, lname in lisos:
    <br />
    <a href="/upload/{{proj_name}}/{{liso}}">{{liso}} ({{lname}})</a>
% end
