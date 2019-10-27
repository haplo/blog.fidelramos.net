#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = 'https://blog.fidelramos.net'
SITELOGO = SITEURL + '/images/fidel.jpg'

RELATIVE_URLS = False

# Drop .html from all URLs
# These settings should be the same as pelicanconf just without .html
ARTICLE_URL = '{category}/{slug}'
ARTICLE_SAVE_AS = '{category}/{slug}'
PAGE_URL = 'pages/{slug}'
PAGE_SAVE_AS = 'pages/{slug}'
TAG_URL = 'tag/{slug}'
TAG_SAVE_AS = 'tag/{slug}'
CATEGORY_URL = 'category/{slug}'
CATEGORY_SAVE_AS = 'category/{slug}'

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'
TRANSLATION_FEED_ATOM = 'feeds/{lang}.atom.xml'

DELETE_OUTPUT_DIRECTORY = True
