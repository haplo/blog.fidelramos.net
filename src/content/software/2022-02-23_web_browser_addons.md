Title: Web browser add-ons I use
Date: 2022-02-23
Modified: 2022-11-19
Lang: en
Category: Software
Tags: firefox,web,addons,privacy,security,cryptocurrency
Slug: web-browser-addons

This article lists the web browser extensions I use and why. I will keep it updated from
time to time.

I use [Firefox](https://www.mozilla.org/en-US/firefox/new/) as my main web browser,
because despite its shortcomings I think it's still the best available option for me, for
reasons that would be worthy of a full article. Some of these extensions are also
available in other web browsers anyway. I will link to the main project's website whenever
that is the case.

I try to be careful with the browser extensions I install, as they have deep access to
browser data, so a compromised add-on can quickly become a nightmare if it manages for
example to steal the credentials for my email account (although 2FA should mitigate that
risk). For this reason I don't use some add-ons that are potentially useful but that I
think I could live without. The ones I use are usually popular, with thousands of users
and often editor-picked.

Without further delay, these are the add-ons I'm currently using on Firefox, in
alphabetical order:

- [ClearURLs](https://addons.mozilla.org/firefox/addon/clearurls/): removes unnecessary
  tracking parameters from URLs, such as the ubiquitous `utm_*` or the long URLs that
  Amazon generates and that can be shortened aggressively.
- [Decentraleyes](https://decentraleyes.org/): many websites use assets from public CDNs
  (e.g. [Google has many hosted
  libraries](https://developers.google.com/speed/libraries/)) to save on network bandwidth
  and/or to serve those assets faster. The downside is that the CDN provider gets a peek
  on who is accessing which website, and that undermines our privacy. Decentraleyes hosts
  a local copy of those assets and prevents the request to the CDN being made, thus
  improving privacy.
- [HTTPS Everywhere](https://www.eff.org/https-everywhere): An [EFF](https://www.eff.org/)
  project which transparently upgrades (and optionally enforces) connections to use HTTPS,
  and therefore secure against eavesdropping or middleman attacks. It's transparent and
  shouldn't break any page, so it's a strong recommendation for every user.
- [KeepassXC-Browser](https://keepassxc.org/docs/KeePassXC_GettingStarted.html#_setup_browser_integration):
  I use [KeepassXC](https://keepassxc.org/) to hold my passwords and secrets, this is its
  official browser extension which enables form autocomplete. It works pretty well
  although not as well as competitors such as Lastpass or 1Password, but I wouldn't trust
  them with my data.
- [Tally Ho!](https://tallyho.org/): an open-source cryptocurrency wallet, gateway to the
  Web 3.0, Dapps, NFTs, ICOs, ERC20 tokens... For me it has replaced Metamask, which is
  closed source. As of Nov 2022 it supports [Ethereum](https://ethereum.org/en/),
  [Polygon](https://polygon.technology/), [Optimism](https://www.optimism.io/) and
  [Arbitrum](https://arbitrum.io/), with support for more blockchains being added often.
- [Firefox Multi-Account
  Container](https://addons.mozilla.org/en-US/firefox/addon/multi-account-containers/):
  while Firefox has built-in support for containers, this extensions is needed to manage
  them. It's an official add-on from the Firefox team itself, so I fully trust it. What
  are containers? They are a way of categorizing tabs, in order to isolate the information
  that is accessible. For example I set up my bank's website to open in a _Banking_
  container, so a potential attacker that makes my browser run code with a security
  exploit in a different tab wouldn't have access to it unless it was opened in the same
  _Banking_ container. I also use it to isolate logged-in tracking, for example I have a
  _Google_ container where I'm signed-in to Google, but in other containers I'm
  logged-out. I use a bunch of other containers: _Gov_ for government websites, _Personal_
  for my self-hosted web apps, _Shopping_ whenever I'm buying something...
- [NoScript](https://noscript.net/): A powerful add-on that blocks the execution of
  scripts on any page, and allow to selectively enable them as necessary. By default all
  scripts get blocked, and finding out which ones are required for some sites to work can
  be painful, but still I think it's worth it for the protection it grants. It also has
  checks against some web attacks such as [XSS](https://en.wikipedia.org/wiki/Xss),
  [Clickjacking](https://en.wikipedia.org/wiki/Clickjacking) or internet-to-intranet.
- [Privacy Badger](https://privacybadger.org/): another EFF extension that _automatically
  learns to block invisible trackers_. It's pretty unobstrusive, which is why I also have
  it in addition to NoScript and uBlock Origin, even if it overlaps with them for the most
  part. Like HTTPS Everywhere it shouldn't break any page, so it's recommended for
  everyone.
- [uBlock Origin](https://ublockorigin.com/): the best ad blocker there is (that I know
  of, if you know of a better one by all means let me know!). It uses little CPU and RAM,
  it usually saves more than it consumes, i.e. web pages load faster without all the crap
  they usually have (banners, tracking scripts, etc.). Especially on mobile it can be
  *very* noticeable.
- [Sidebery](https://addons.mozilla.org/en-US/firefox/addon/sidebery/): a tab manager for
  Firefox. If you are like me and have not dozens, but hundreds of tabs, this is a game
  changer. Having so many opened tabs goes from being an inconvenience to actually being
  an advantage. You have a tree hierarchy of tabs; can group tabs in different ways
  (groups and panes); have tabs go to a pane depending on the container they are opened on
  (see the Firefox Multi-Account Container add-on mention above); unload tabs and whole
  panes (remove them from memory); and a lot more. It's insanely configurable, and I am a
  guy who *loves* configurability. I keep discovering features and ways to have Sidebery
  help my workflows.

Updates:

- 2022-11-19: Replaced Metamask with Tally Ho; add Sidebery.
