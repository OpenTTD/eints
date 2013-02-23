%from webtranslate.bottle import url, request
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
    <title>{{title or 'No title'}}</title>
    <link type="text/css" href="{{ url('static', path='css/bootstrap.min.css') }}" rel="stylesheet">
    <!-- load order is significant for css, our over-rides on bootstrap must load after bootstrap -->
    <link type="text/css" href="{{ url('static', path='css/style.css') }}" rel="stylesheet">
    <script type="text/javascript" src="{{ url('static', path='js/jquery-1.9.1.min.js') }}"></script>
    <script type="text/javascript" src="{{ url('static', path='js/bootstrap-filestyle-0.1.0.js') }}"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            $(":file").filestyle({classButton:"btn-info"});
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="navbar eint-navbar">
            <div class="navbar-inner">
                <ul class="nav">
                    <li><a href="/">Home</a></li>
                    <li><a href="/projects">Projects</a></li>
                    <li><a href="/newproject">New Project</a></li>
                </ul>
            </div>
        </div>

        %if len(request.query.get('message', '')) > 0:
        <div id="message-slot" class="alert alert-info">
            {{request.query.get('message', '')}}
        </div>
        %end

        <!-- content from calling template -->
        %include

        <div class="footer">
            <a href="http://dev.openttdcoop.org/projects/eints">Web Translator</a> from <a href="http://dev.openttdcoop.org">#openttdcoop</a>
        </div>
    </div>
</body>
</html>
