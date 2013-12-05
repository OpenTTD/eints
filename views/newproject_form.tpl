%rebase main_template title='Create a new translation project'
<h1 class="eint-heading-icon eint-icon-add">Create a new translation project</h1>
<br />
<form class="form well" action="/createproject" method="post" enctype="multipart/form-data">
    <br />
    <fieldset style="padding-left:160px;">
        <label for="name">Project identifier (required)</label>
        <input class="input-xxlarge" type="text" id="name" name="name"/>
        <span class="help-block">Only characters A-Z, a-z, 0-9 and dash (-) allowed</span>
        <br />
        <br />
        <div class="control-group">
            <label class="control-label" for="projtype_select">Project type:</label>&nbsp;
            <select name="projtype_select" id="projtype_select">
                <option selected value="none">Select a project type</option>
                % for ptype_name in all_ptype_names:
                    <option value="{{ptype_name}}">{{ptype_name}}</option>
                % end
            </select>
            &nbsp;
            <button class="btn btn-primary" type="submit">Create Project!</button>
        </div>
    </fieldset>
</form>
