%rebase main_template title='Remove translation language ' + lname
<h1>Remove translation language {{lname}}</h1>
<br />
You are about to remove the entire translation language {{lname}} from {{pdata.name}}.
<br />
<strong>Are you sure?</strong>
<br />
<form action="/really_delete/{{proj_name}}/{{lname}}" method="post" enctype="multipart/form-data">
    <button type="submit">Yes, remove translation language {{lname}}</button>
    <a href="/project/{{proj_name}}">No! Take me out of here</a>
</form>
