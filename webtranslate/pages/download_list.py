"""
Download a list of existing languages.
Example::
    en_UK,56767567,http://example.org/download/<prjname>/en_UK

"""
from webtranslate.bottle import route, template, abort, response, request
from webtranslate.protect import protected
from webtranslate import config, data

def get_newest_change(lang):
    """
    Decide when the provided language was last changed.

    @param lang: Language to inspect.
    @type  lang: L{Language}

    @return: Time stamp of the last change, if it exists.
    @rtype:  C{None} or L{Stamp}
    """
    newest = None

    for chgs in lang.changes.values():
        for chg in chgs:
            if newest is None or newest < chg.stamp:
                newest = chg.stamp
    return newest

@route('/download-list/<prjname>', method = 'GET')
@protected(['download-list', 'prjname', '-'])
def download_list(user, prjname):
    pmd = config.cache.get_pmd(prjname)
    if pmd is None:
        abort(404, "Page not found")
        return

    #print("url=" + repr(request.url))
    #print("urlparts=" + repr(request.urlparts))
    #print("request=", request)
    pdata = pmd.pdata
    response.content_type = 'text/plain; charset=UTF-8'
    lines = []
    for lng, ldata in pdata.languages.items():
        tstamp = get_newest_change(ldata)
        if tstamp is None:
            text = "????"
        else:
            text = str(tstamp)
        urlparts = request.urlparts
        url = urlparts.scheme + "://" + urlparts.netloc + "/download/" + prjname + "/" + ldata.name
        line = "{},{},0x{:02x},{}".format(ldata.name, text, ldata.grflangid, url)
        lines.append(line)

    return '\n'.join(lines) + '\n'

