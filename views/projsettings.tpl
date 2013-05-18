%rebase main_template title='Web translator - ' + human_name
<h1>{{human_name}}</h1>
<hr />
<form class="form-horizontal well well-large" action="/projsettings/{{proj_name}}" method="post" enctype="multipart/form-data">
    <textarea name="name">{{human_name}}</textarea>
    <textarea name="url">{{url}}</textarea>
    <input class="btn btn-primary pull-right" type="submit" value="Save Changes"/>
</form>
