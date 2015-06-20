%rebase('main_template', title='Editing ' + sname)
%from webtranslate import utils
<h1>
    <a class="eint-header-link" href="/project/{{proj_name}}">{{pdata.human_name}}</a>
</h1>
<a class="pull-right" target="_blank" href="http://bundles.openttdcoop.org/eints/nightlies/LATEST/docs/strings.html">String editing Manual</a>
<hr />
<h2 class="eint-heading-icon eint-icon-document-1-edit">
    <a class="eint-header-link" href="/translation/{{proj_name}}/{{lname}}">{{lname}}</a> - Edit Strings
    <span class="muted pull-right">{{sname}}</span>
</h2>
<div class="clearfix"/>
<form class="form-horizontal" action="/string/{{proj_name}}/{{lname}}/{{sname}}" method="post" enctype="multipart/form-data">
    % for tc in tcs:
        <fieldset class="well">

            <!-- Header -->
            % if len(tc.case) == 0:
                <div class="control-group">
                    <!-- Display old base language text, if base changed. -->
                    % if tc.transl[0].current_base != tc.transl[0].trans_base:
                        <span class="control-label">Previous base language text:</span>
                        <span class="eint-form-value-as-text span8"><strong>{{utils.create_displayed_base_text(pdata, tc.transl[0].trans_base)}}</strong></span>
                    % end

                    <!-- Display current base language text. -->
                    <div>
                        <span class="control-label">Base lang string:</span>
                        <span class="eint-form-value-as-text span8"><strong id="base_{{tc.case}}">{{utils.create_displayed_base_text(pdata, tc.transl[0].current_base)}}</strong></span>
                    </div>

                    <!-- Display current language text of related languages. -->
                    % for rel_lang, rel_text in related_languages:
                        <div>
                            <span class="control-label">{{rel_lang}}:</span>
                            <span class="eint-form-value-as-text span8"><strong id="reltrans_{{rel_lang}}">{{rel_text.new_text.text}}</strong></span>
                        </div>
                    % end
                </div>
            % end

            <div class="control-group">
                <!-- Display case name -->
                <span class="control-label" style="text-align:left">
                    % if len(tc.case) != 0:
                        Case: {{tc.case}}
                    % end
                </span>
                <span class="eint-form-value-as-text span8">
                    <span>Status: {{tc.transl[0].state}}</span>
                    <span class="pull-right">
                        % if len(tc.case) != 0:
                            <button class="btn btn-mini" type="button" onclick="copyValue('text_', 'text_{{tc.case}}')">Copy Default</button>
                        % end
                        % for rel_lang, rel_text in related_languages:
                            <button class="btn btn-mini" type="button" onclick="copyText('reltrans_{{rel_lang}}', 'text_{{tc.case}}')">Copy {{rel_lang}}</button>
                        % end
                        <button class="btn btn-mini" type="button" onclick="copyText('base_', 'text_{{tc.case}}')">Copy Base</button>
                    </span>
                </span>
            </div>

            <input type="hidden" name="base" value="{{tc.transl[0].current_base.text}}"/>

            <!-- Display case, status, translation, errors. -->
            <div class="control-group {{('error','')[len(tc.transl[0].errors) == 0]}}">
                <label class="control-label">Translation:</label>
                <div class="controls">
                    <textarea class="span8" name="text_{{tc.case}}" id="text_{{tc.case}}" rows="4"
                    % if len(tc.case) == 0:
                        id="default_case" oninput="updatePlaceholder()"
                    % end
                    >{{tc.transl[0].text.text}}</textarea>
                    % if len(tc.case) == 0:
                        <p>Allow empty input: <input type="checkbox" name="allow_empty_default"/>
                    % else:
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

            <!-- Collapsable history of the translation. -->
            <div class="control-group">
                % if len(tc.transl) > 1:
                    <span class="control-label">
                        <button class="btn btn-mini" type="button" data-toggle="collapse" data-target="#history_{{tc.case}}" aria-expanded="false" aria-controls="history_{{tc.case}}">
                            History
                        </button>
                    </span>
                % end
                % if tc.transl[0].saved and tc.transl[0].user is not None:
                    <div class="controls">
                        <span class="help-block">Translation created by "{{tc.transl[0].user}}"
                            % if tc.transl[0].stamp_desc is not None:
                                ({{tc.transl[0].stamp_desc}} ago)
                            % end
                        </span>
                    </div>
                % end
            </div>

            % if len(tc.transl) > 1:
                <div class="collapse" id="history_{{tc.case}}">
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
                </div>
            % end

            <!-- Gender / case help -->
            % if len(tc.case) == 0:
                <div class="control-group">
                    % if len(plurals) > 1:
                        <div>
                            <span class="control-label">Plural syntax:</span>
                            <span class="eint-form-value-as-text span8">
                                {P <abbr title="Optional parameter reference index (counting from 0); by default plural forms refer to the previous parameter.">[index]</abbr>
                                    % for p in plurals:
                                        "{{p}}"
                                    % end
                                }  
                            </span>
                        </div>
                    % end
                    % if len(genders) > 1:
                        <div>
                            <span class="control-label">Gender syntax:</span>
                            <span class="eint-form-value-as-text span8">
                                {G <abbr title="Optional parameter reference index (counting from 0); by default gender forms refer to the next parameter.">[index]</abbr>
                                    % for g in genders:
                                        "{{g}}"
                                    % end
                                }
                            </span>
                        </div>
                    % end                        
                </div>
            % end

            <!-- Related strings -->
            % if len(tc.case) == 0 and len(tc.related) > 0:
                <h5>Related Strings</h5>
                    <dl class="dl-horizontal">
                        % for rel in tc.related:
                            <dt style="width: 23em; text-align: left"><a href="/string/{{proj_name}}/{{lname}}/{{rel.sname}}" title="{{rel.sname}}">{{rel.sname}}</a></dt>
                            <dd style="margin-left: 25em">{{rel.text.text}}<p/></dd>
                        % end
                    </dl>
            % end
        </fieldset>

        % if len(tcs) > 1 and len(tc.case) == 0:
            <!-- Begin of collapsable cases -->
            <button class="btn btn-primary" type="button" data-toggle="collapse" data-target="#cases"
                % if sum(len(c.transl[0].text.text) for c in tcs if len(c.case) != 0) != 0:
                    aria-expanded="true"
                % else:
                    aria-expanded="false"
                % end
                aria-controls="cases">
                Translations for Cases
            </button>
            <div
                % if sum(len(c.transl[0].text.text) for c in tcs if len(c.case) != 0) != 0:
                    class="collapse in"
                % else:
                    class="collapse"
                % end
                id="cases">
        % end
    % end

    % if len(tcs) > 1:
        <!-- End of collapsable cases -->
        </div>
        <hr />
    % end
    
    <div>
        <a class="btn btn-primary" href="/fix/{{proj_name}}/{{lname}}">Get another string</a>
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
    dest.value = src.textContent;
}
function copyValue(srcid, destid) {
    var src = document.getElementById(srcid);
    var dest = document.getElementById(destid);
    dest.value = src.value;
}
</script>
