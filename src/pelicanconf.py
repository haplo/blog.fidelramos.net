#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Fidel Ramos'
SITENAME = 'blog.fidelramos.net'
SITETITLE = AUTHOR
SITESUBTITLE = ''
SITEDESCRIPTION = 'Fidel Ramos personal blog'
SITEURL = ''
SITELOGO = SITEURL + '/images/fidel.jpg'
FAVICON = SITEURL + '/images/favicon.ico'

CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}
COPYRIGHT_YEAR = 2019

PATH = 'content'

TIMEZONE = 'Europe/Madrid'

DEFAULT_DATE = 'fs'

LOAD_CONTENT_CACHE = False

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Main menu, above the article
MAIN_MENU = True
MENUITEMS = (
    ('Archive', '/archives#archives'),
    ('Categories', '/categories#categories'),
    ('Tags', '/tags#tags'),
)

LINKS = (
    ('Archive', '/archives#archives'),
    ('Categories', '/categories#categories'),
    ('Tags', '/tags#tags'),
    ('DuckDuckGo', 'https://duckduckgo.com')
)

# Social widget
GITHUB_URL = 'https://github.com/haplo'
SOCIAL = (
    ('twitter', 'https://twitter.com/ampajaro'),
#    ('mastodon', ''),
    ('github', GITHUB_URL),
    ('flickr', 'https://www.flickr.com/photos/fidelramos/'),
    ('linkedin', 'https://www.linkedin.com/in/fidelramos/'),
    ('rss', SITEURL+'/atom.xml'),
)

TWITTER_USERNAME = 'ampajaro'

DEFAULT_PAGINATION = 10

ROBOTS = 'index,follow'

THEME = '../../pelican-theme-Flex'
EXTRA_PATH_METADATA = {
    'extra/custom.css': {'path': 'static/custom.css'},
}
CUSTOM_CSS = 'static/custom.css'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

PLUGIN_PATHS = ['/home/user/Code/pelican-plugins']
PLUGINS = ['i18n_subsites']

JINJA_ENVIRONMENT = {
    'extensions': ['jinja2.ext.i18n'],
}

# i18n and language configuration
DEFAULT_LANG = 'en'
OG_LOCALE = 'en_US'
LOCALE = 'en_US'

I18N_SUBSITES = {
    'es': {
        'INDEX_DESCRIPTION': 'Blog personal de Fidel Ramos',
        'OG_LOCALE': 'es_ES',
        'LOCALE': 'es_ES',
        'MENUITEMS': (
            ('Archivo', SITEURL+'/es/archives#archives'),
            ('Categorías', SITEURL+'/es/categories#categories'),
            ('Etiquetas', SITEURL+'/es/tags#tags'),
        ),
    },
}

DATE_FORMATS = {
    'en': '%Y-%m-%d',
    'es': '%Y-%m-%d',
}
