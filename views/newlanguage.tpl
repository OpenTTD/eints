%rebase('main_template', title='Web Translator - {} - Start new translation'.format(pmd.human_name))
<h1>
    <a class="eint-header-link" href="/project/{{pmd.name}}">{{pmd.human_name}}</a>
</h1>
<hr />
<h2 class="eint-heading-icon eint-icon-add">Start New Translation</h2>
<form class="form-inline well" action="/newlanguage/{{pmd.name}}" method="post" enctype="multipart/form-data">
    <fieldset>
        <br />
        <div style="width: 60%; margin-left:auto; margin-right:auto;">
        <div class="control-group">
            <label class="control-label" for="language_select">Language:</label>&nbsp;
            <select name="language_select" id="language_select">
                <option selected value="none">Select a new language</option>
                % for lang in can_be_added:
                    <option value="{{lang.isocode}}">{{lang.isocode}} ({{lang.name}})</option>
                % end
            </select>
            &nbsp;
            <button class="btn btn-primary" type="submit">Select new language</button>
        </div>
        </div>
    </fieldset>
</form>

<h3>Existing Languages</h3>
<table class="table table-condensed table-striped">
        % for lang in base_langs:
        <tr>
            <td>
                {{lang.isocode}}
            </td>
            <td>
                {{lang.name}}
            </td>
            <td>
                <strong>Base language</strong>
            </td>
        </tr>
        % end
        % for lang in translations:
        <tr>
            <td>
                {{lang.isocode}}
            </td>
            <td>
                {{lang.name}}
            </td>
            <td>
                 Existing translation
            </td>
        </tr>
        % end
    </tr>
</table>
