#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Ainsley Escorce-Jones'
SITENAME = u'Ainsley Escorce-Jones | ains.co'
SITEURL = '/'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

DEFAULT_PAGINATION = 10

THEME = "fukasawa"

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

ARCHIVES_SAVE_AS = 'blog/index.html'
ARTICLE_URL = 'blog/{slug}.html'
ARTICLE_SAVE_AS = 'blog/{slug}.html'

PLUGIN_PATHS = ['plugins']
PLUGINS = ['assets']