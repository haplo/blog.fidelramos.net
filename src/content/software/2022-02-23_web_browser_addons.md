Title: Web browser add-ons I use
Date: 2022-02-23
Modified: 2023-04-20
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

- [uBlock Origin](https://ublockorigin.com/): the best ad blocker there is. It uses little
  CPU and RAM, usually saves more than it consumes, i.e. web pages load faster without all
  the crap they usually have (banners, tracking scripts, etc.). Especially on mobile it
  can be *very* noticeable. I used to use a bunch of other privacy-related extensions
  (NoScript, ClearURLs, PrivacyBadger, HTTPSEverywhere and DecentralEyes), but after
  reading [this article on
  Arkenfox](https://github.com/arkenfox/user.js/wiki/4.1-Extensions) I learned that they
  are superfluous if uBlock Origin is properly configured. Let me tell you one more thing:
  after removing the extensions and leaving only uBlock Origin my Firefox *flies*.
- [KeepassXC-Browser](https://keepassxc.org/docs/KeePassXC_GettingStarted.html#_setup_browser_integration):
  I use [KeepassXC](https://keepassxc.org/) to hold my passwords and secrets, this is its
  official browser extension which enables form autocomplete. It works pretty well
  although not as well as competitors such as Lastpass or 1Password, but I wouldn't trust
  them with my data.
- [Taho](https://taho.xyz/): an open-source cryptocurrency wallet, gateway to the
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
- [Sidebery](https://addons.mozilla.org/en-US/firefox/addon/sidebery/): a tab manager for
  Firefox. If you are like me and have not dozens, but hundreds of tabs, this is a game
  changer. Having so many opened tabs goes from being an inconvenience to actually being
  an advantage. You have a tree hierarchy of tabs; can group tabs in different ways
  (groups and panes); have tabs go to a pane depending on the container they are opened on
  (see the Firefox Multi-Account Container add-on mention above); unload tabs and whole
  panes (remove them from memory); and a lot more. It's insanely configurable, and I am a
  guy who *loves* configurability. I keep discovering features and ways to have Sidebery
  help my workflows.
- [Skip Redirect](https://addons.mozilla.org/en-US/firefox/addon/skip-redirect/): detects
  and skips redirects, to avoid unnecessary tracking. For example if you look closely you
  will notice that when clicking on a Google result the URL points to Google, which then
  redirects you to the target. This way Google knows which results you visit. This
  extension extracts the target and goes to it directly, thus avoiding tracking.

Updates:

- 2022-11-19: Replaced Metamask with Tally Ho; added Sidebery.
- 2023-01-20: Added Skip Redirect; removed NoScript, ClearURLs, PrivacyBadger, HTTPSEverywhere, DecentralEyes.
- 2023-04-20: Updated Tally Ho to Taho, they [rebranded in Feb 21, 2023](https://blog.taho.xyz/rename-announcement/).
