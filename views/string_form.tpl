%rebase main_template title='Editing ' + sname
<h1>
    <a class="eint-header-link" href="/project/{{proj_name}}">{{pdata.human_name}}</a>
</h1>
<a class="pull-right" target="_blank" href="http://bundles.openttdcoop.org/eints/nightlies/LATEST/docs/strings.html">String editing Manual</a>
<hr />
<h2 class="eint-heading-icon eint-icon-document-1-edit">
    <a class="eint-header-link" href="/translation/{{proj_name}}/{{lname}}">{{lname}}</a> - Edit Strings
    <span class="muted pull-right">{{sname}}</span>
</h2>
<form class="form-horizontal" action="/string/{{proj_name}}/{{lname}}/{{sname}}" method="post" enctype="multipart/form-data">
% for tc in tcs:
    <fieldset class="well">
        <span class="pull-left">{{tc.get_stringname(sname)}}</span>
        <div class="pull-right muted">
            <span>Translation status:</span>
            <span>{{tc.transl[0].state}}</span>
        </div>
        <hr class="clearfix" style="margin-top:30px;"/><!-- an inline style per day keeps the doctor away -->
        <div class="control-group">
            <span class="control-label">Base lang string:</span>
            <span class="eint-form-value-as-text span8"><strong id="base_{{tc.case}}">{{tc.transl[0].current_base.text}}</strong></span>
            <button class="pull-right" type="button" onclick="copyText('base_{{tc.case}}', 'text_{{tc.case}}')">Copy</button>
            <input type="hidden" name="base" value="{{tc.transl[0].current_base.text}}"/>
        </div>
        <div class="control-group {{('error','')[len(tc.transl[0].errors) == 0]}}">
            <label class="control-label">Translation:</label>
            <div class="controls">
                <textarea class="span8" name="text_{{tc.case}}" id="text_{{tc.case}}" rows="4"
                % if len(tc.case) == 0:
                id="default_case" oninput="updatePlaceholder()"
                % end
                >{{tc.transl[0].text.text}}</textarea>
                % if len(tc.case) != 0:
                <p>Note: Leave the entry for cases empty, if they shall use the same translation as the default case.</p>
                % end
                % if len(tc.transl[0].errors) == 0:
                    % if tc.transl[0].state == 'out-of-date':
                        The current translation is correct: <input type="checkbox" name="ok_{{tc.case}}"/><!-- !! this case not styled yet -->
                    % end
                % else:
                    % for err in tc.transl[0].errors:
                        <span class="help-block error">{{err.type}}: {{err.msg}}</span>
                    % end
                % end
            </div>
        </div>
        % if tc.transl[0].saved and tc.transl[0].user is not None:
            <div class="control-group">
                <div class="controls">
                    <span class="help-block">Translation created by "{{tc.transl[0].user}}"
                    % if tc.transl[0].stamp_desc is not None:
                        ({{tc.transl[0].stamp_desc}} ago)
                    % end
                    </span>
                </div>
            </div>
        % end
        % if tc.transl[0].current_base != tc.transl[0].trans_base:
            <p>Previous base language text:<br />{{tc.transl[0].trans_base.text}}</p>
        % end
        % if len(tc.transl) > 1:
            <h5>Previous Translations</h5>
            <table class="table table-condensed">
                <thead>
                    <tr>
                        <th>Who</th>
                        <th>When</th>
                        <th>Translation</th>
                    </tr>
                </thead>
                <tbody>
                    % for tl in tc.transl[1:]:
                        <tr>
                            <td>{{tl.user}}</td>
                            <td>{{tl.stamp_desc}} ago</td>
                            <td>{{tl.text.text}}</td>
                        </tr>
                    % end
                </tbody>
            </table>
        % end
        % if len(tc.related) > 0:
            <h5>Related Strings</h5>
            <table border="0" class="table table-condensed">
                <tbody>
                % for rel in tc.related:
                    <tr>
                        <td><a href="/string/{{proj_name}}/{{lname}}/{{rel.sname}}">{{rel.sname}}</a></td>
                        <td>{{rel.text.text}}</td>
                    </tr>
                % end
                </tbody>
            </table>
        % end
    </fieldset>
% end
    <div>
        <a href="/fix/{{proj_name}}/{{lname}}">Get another string</a>
        <input class="btn btn-primary pull-right" type="submit" value="Save Changes &amp; Get Next String"/>
    </div>
    <br />
</form>
<script type="text/javascript" onload="updatePlaceholder()">
function updatePlaceholder() {
    var def = document.getElementById("default_case");
    var text = def.value;
    var areas = document.getElementsByTagName("textarea");
    for (i = 0; i < areas.length; i++) {
        var child = areas[i];
        if (child == def) continue;
        child.placeholder = text;
    }
}
function copyText(srcid, destid) {
    var src = document.getElementById(srcid);
    var dest = document.getElementById(destid);
    dest.value = src.innerHTML;
}
</script>
