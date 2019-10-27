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

CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'
CATEGORY_FEED_RSS = 'feeds/{slug}.rss.xml'
TRANSLATION_FEED_ATOM = 'feeds/{lang}.atom.xml'
TRANSLATION_FEED_RSS = 'feeds/{lang}.rss.xml'

DELETE_OUTPUT_DIRECTORY = True
