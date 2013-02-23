%from webtranslate.bottle import url
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <title>{{title or 'No title'}}</title>
  <link type="text/css" href="{{ url('static', path='css/test.css') }}" rel="stylesheet">
  <link type="text/css" href="{{ url('static', path='css/bootstrap.min.css') }}" rel="stylesheet">
</head>
<body>
    <div class="navbar navbar-static-top">
        <div class="navbar-inner">
            <ul class="nav">
                <li><a href="/">Home</a></li>
                <li><a href="/projects">Projects</a></li>
                <li><a href="/newproject">New Project</a></li>
            </ul>
        </div>
    </div>

    %include

    <hr />
    <div>
        <a href="http://dev.openttdcoop.org/projects/eints">Web Translator</a> from <a href="http://dev.openttdcoop.org">#openttdcoop</a>
    </div>
</body>
</html>
