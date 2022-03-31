import copy

AUTHOR = 'Fidel Ramos'
SITENAME = 'blog.fidelramos.net'
SITETITLE = AUTHOR
SITESUBTITLE = ''
SITEDESCRIPTION = 'Fidel Ramos personal blog'
SITEURL = 'http://localhost:8000'
SITELOGO = SITEURL + '/images/fidel.jpg'
FAVICON = 'https://fidelramos.net/favicon.ico'

CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}
COPYRIGHT_YEAR = 2019

PATH = 'content'
STATIC_PATHS = ['images']

TIMEZONE = 'Europe/Madrid'

DEFAULT_DATE = 'fs'

LOAD_CONTENT_CACHE = False

ARTICLE_URL = '{category}/{slug}'
ARTICLE_SAVE_AS = '{category}/{slug}.html'
AUTHOR_SAVE_AS = ''
AUTHORS_SAVE_AS = ''
CATEGORIES_URL = 'categories/'
CATEGORIES_SAVE_AS = 'categories/index.html'
CATEGORY_URL = 'categories/{slug}'
CATEGORY_SAVE_AS = 'categories/{slug}.html'
TAGS_URL = 'tags/'
TAGS_SAVE_AS = 'tags/index.html'
TAG_URL = 'tags/{slug}'
TAG_SAVE_AS = 'tags/{slug}.html'

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
    ('Atom', '/feeds/en.atom.xml'),
    ('RSS', '/feeds/en.rss.xml'),
)

LINKS = (
    ('Español', '/es/'),
)
LINKS_IN_NEW_TAB = 'external'

GITHUB_URL = 'https://github.com/haplo'
SOCIAL = [
    ('twitter', 'https://twitter.com/ampajaro'),
    ('mastodon', 'https://mastodon.social/@fidel'),
    ('github', GITHUB_URL),
    ('flickr', 'https://www.flickr.com/photos/fidelramos/'),
    ('linkedin', 'https://www.linkedin.com/in/fidelramos/'),
    ('rss', '/feeds/en.atom.xml'),
]

TWITTER_USERNAME = 'ampajaro'

DEFAULT_PAGINATION = 10

ROBOTS = 'index,follow'

THEME = '../../pelican-theme-Flex'
EXTRA_PATH_METADATA = {
    'extra/custom.css': {'path': 'static/custom.css'},
}
CUSTOM_CSS = 'static/custom.css'

USE_GOOGLE_FONTS = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# PLUGIN_PATHS *MUST* be strings, otherwise plugins will fail to import
PLUGIN_PATHS = ['../../pelican-plugins']
PLUGINS = ['i18n_subsites']

JINJA_ENVIRONMENT = {
    'extensions': ['jinja2.ext.i18n'],
}

MARKDOWN = {
    'extensions': [
        'markdown_captions',
    ],
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown.extensions.footnotes': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.toc': {
            'title': 'Table of Contents'
        },
    },
    'output_format': 'html5',
}

# i18n and language configuration
DEFAULT_LANG = 'en'
# use "locale -a" in GNU/Linux to see available locales
LOCALE = ['en_US.utf8', 'es_ES.utf8']

I18N_SUBSITES = {
    'es': {
        'SITEDESCRIPTION': 'Blog personal de Fidel Ramos',
        'OG_LOCALE': 'es_ES',
        'LOCALE': 'es_ES',
        'LINKS': (
            ('English', '/'),
        ),
        'SOCIAL': SOCIAL[:-1] + [
            ('rss', '/es/feeds/es.atom.xml'),
        ],
        'MENUITEMS': (
            ('Archivo', '/es/archivos#archives'),
            ('Categorías', '/es/categorias#categories'),
            ('Etiquetas', '/es/etiquetas#tags'),
            ('Atom', '/es/feeds/es.atom.xml'),
            ('RSS', '/es/feeds/es.rss.xml'),
        ),
        'ARCHIVES_URL': 'archivos/',
        'ARCHIVES_SAVE_AS': 'archivos/index.html',
        'CATEGORIES_URL': 'categorias/',
        'CATEGORIES_SAVE_AS': 'categorias/index.html',
        'CATEGORY_URL': 'categorias/{slug}',
        'CATEGORY_SAVE_AS': 'categorias/{slug}.html',
        'PAGE_URL': 'paginas/{slug}',
        'PAGE_SAVE_AS': 'paginas/{slug}.html',
        'TAGS_URL': 'etiquetas/',
        'TAGS_SAVE_AS': 'etiquetas/index.html',
        'TAG_URL': 'etiquetas/{slug}',
        'TAG_SAVE_AS': 'etiquetas/{slug}.html',
        'MARKDOWN': copy.deepcopy(MARKDOWN),  # copy to override later
    },
}
I18N_SUBSITES['es']['MARKDOWN']['extension_configs']['markdown.extensions.toc']['title'] = 'Índice de contenidos'

I18N_UNTRANSLATED_ARTICLES = 'remove'
I18N_UNTRANSLATED_PAGES = 'remove'

DATE_FORMATS = {
    # ISO 8601 FTW
    'en': '%Y-%m-%d',
    'es': '%Y-%m-%d',
}
