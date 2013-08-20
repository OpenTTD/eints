import os
os.chdir(os.path.dirname(__file__))


from webtranslate import main
from webtranslate import bottle

main.run()

# ... build or import your bottle application here ...
# Do NOT use bottle.run() with mod_wsgi
application = bottle.default_app()


