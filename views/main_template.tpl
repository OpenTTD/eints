%from urllib.parse import quote
%from webtranslate.bottle import url, request
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
    <title>{{title or 'No title'}}</title>
    <link type="text/css" href="{{ url('static', path='css/bootstrap.min.css') }}" rel="stylesheet">
    <!-- load order is significant for css, our over-rides on bootstrap must load after bootstrap -->
    <link type="text/css" href="{{ url('static', path='css/style.css') }}" rel="stylesheet">
    <script type="text/javascript" src="{{ url('static', path='js/bootstrap.min.js') }}"></script>
</head>
<body>
    <div class="container">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary eint-navbar">
            <div class="container-fluid">
                <ul class="navbar-nav">
                    <li class="nav-item"><a class="nav-link" href="/"><i class="icon-home"></i> Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/languages"><i class="icon-list-alt"></i> Languages</a></li>
                    <li class="nav-item"><a class="nav-link" href="/projects"><i class="icon-list-alt"></i> Projects</a></li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item"><a class="nav-link" target="_blank" href="/static/docs/usage.html"><i class="icon-book"></i> Manual</a></li>
                    %if userauth.is_auth:
                        <li class="nav-item"><a class="nav-link" href="/userprofile"><i class="icon-user"></i> Profile ({{ userauth.name }})</a></li>
                        <li class="nav-item"><a class="nav-link" href="/logout"><i class="icon-user"></i> Logout</a></li>
                    %else:
                        <li class="nav-item"><a class="nav-link" href="/login?redirect={{ quote(request.path) }}"><i class="icon-user"></i> Login</a></li>
                    %end
                </ul>
            </div>
        </nav>

        %for message in messages:
            <div id="message-slot" class="alert {{message['class']}}">
                {{message['content']}}
            </div>
        %end
        <!-- content from calling template -->
        {{!base}}

        <footer class="py-3 my-4">
            <ul class="nav justify-content-center border-top pb-3 mb-3">
                <li class="nav-item"><a class="nav-link px-2 text-muted" href="https://github.com/OpenTTD/eints">Web Translator</a></li>
                <li class="nav-item"><a class="nav-link px-2 text-muted" href="https://github.com/OpenTTD/eints/issues">Report a bug</a></li>
            </ul>
        </footer>
    </div>
</body>
</html>
