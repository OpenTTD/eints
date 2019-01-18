# Eints

## About

Eints Is a Newgrf Translation Service.
Though now it is also used for Game Scripts and OpenTTD itself.

Eints is written in [Python 3](http://www.python.org/).

You can find more details in docs/manual.

## Licensing

Eints software uses the [GPL V2](http://www.gnu.org/licenses/gpl-2.0.html).
For stand-alone use (which is useful for development and testing), no other software is needed.

Internally, it uses:

- [Bottle](http://bottlepy.org/), a Python framework for writing web applications.
    - Location: webtranslate/bottle.py
    - Licensed under [MIT License](http://bottlepy.org/docs/dev/#license)
- [Twitter Boostrap](http://twitter.github.com/bootstrap/), a CSS, JS and glyphicon framework
  for web application user interfaces.
    - Locations: static/css static/img static/js
    - Code licensed under [Apache License v2.0](http://www.apache.org/licenses/LICENSE-2.0),
    - Documentation licensed under [CC BY 3.0](http://creativecommons.org/licenses/by/3.0/).
    - Glyphicons Free licensed under [CC BY 3.0](http://creativecommons.org/licenses/by/3.0/).
- [WooCons #1](http://www.woothemes.com/2010/08/woocons1/), an icon library.
    - Location: static/img/woocons1
    - Licensed under [GPL v3](http://www.gnu.org/licenses/gpl.html)

The Eints repository includes files of the above projects for your
convenience. They are however not part of Eints.
