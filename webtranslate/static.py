from webtranslate.bottle import route, static_file, url

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')
