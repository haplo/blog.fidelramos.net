Title: Announcing Reflex, a Pelican theme
Date: 2026-02-16
Lang: en
Category: Software
Tags: free-software,pelican
Slug: announce-reflex-theme

I'm happy to announce the public availability of my Pelican theme: [Reflex](https://github.com/haplo/python-theme-reflex).
It is [published on PyPI](https://pypi.org/project/pelican-reflex/), which should be the best way for most users to install it.

When I first started this blog I decided on Pelican because I had lots of experience with Python, so it would make it easier for me to get involved and contribute.
I then looked at all the [Pelican themes](http://www.pelicanthemes.com/) and settled on the [Flex theme by Alexandre
Vizenzi](https://github.com/alexandrevicenzi/Flex) because it checked all my requirements:

- Minimalistic and beautiful.
- Responsive layout.
- Archives, categories, tags support.
- Pygments support for code highlighting.
- Light/Dark modes support.

As it was inevitable I eventually hit some missing features and small tweaks I wanted to implement.
That is the beauty of open-source, and I started [contributing to Flex](https://github.com/alexandrevicenzi/Flex/pulls?q=is%3Apr+author%3Ahaplo+).
However some of my desired changes were too deep, and they didn't fit in Flex as the project was in maintenance mode.
After some thinking I decided to fork the theme to introduce my more breaking changes, and that is when Reflex was born.

The **main differences with Flex** for now:

- Style for Table of Contents created by the *toc* markdown extension.
- Styles for `figure` and `figcaption` HTML elements.
- Shynet tracking support (see [my article on self-hosted comments]({filename}2025-02-10_self_hosted_comments.md)).
- In-repo documentation instead of Github wiki.
- Display language flags for alternative article languages.
- X social icon.
- Improvements to developer experience: gulp watch support for instant changes, AGENTS.md for AI development, revamped GitHub Actions workflows.
- Updated Pygments styles and FontAwesome.

I don't have a long roadmap planned for Reflex, I will mostly implement changes that I find useful for this blog.
I'm open to new integrations and ideas, so collaborators are welcome!

For known bugs and planned features take a look at the [open issues](https://github.com/haplo/pelican-theme-reflex/issues).
For any questions feel free to open a [discussion](https://github.com/haplo/pelican-theme-reflex/discussions).

If you use Reflex feel free to add your site to the [list of Reflex users](https://github.com/haplo/pelican-theme-reflex?tab=readme-ov-file#sites-using-reflex), I would love to hear from you!
