from webtranslate.bottle import Bottle, run, route, static_file, view, template, post, request, url

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')
