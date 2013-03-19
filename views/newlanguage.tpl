%rebase main_template title='Add a new translation language'
<h1 class="eint-heading-icon eint-icon-add">Add a new translation language</h1>
<br />
Available languages:<br />
% for lang in base_langs:
    {{lang.isocode}} ({{lang.name}}) <strong>Base language</strong><br />
% end
<p />
% for lang in translations:
    {{lang.isocode}} ({{lang.name}}) Already existing translation<br />
% end
<p />
<form class="form-inline well" action="/newlanguage/{{proj_name}}" method="post" enctype="multipart/form-data">
    <fieldset>
        <div class="control-group">
            % for lang in can_be_added:
                <div class="controls">
                    <label class="checkbox" for="override" class="checkbox">
                        <input type="checkbox" name="{{lang.isocode}}" id="{{lang.isocode}}" /> {{lang.isocode}} ({{lang.name}})
                    </label>
                </div>
            % end
        </div>

        <div class="pull-right">
            <button class="btn btn-primary" type="submit">Add translation language!</button>
        </div>
    </fieldset>
</form>
