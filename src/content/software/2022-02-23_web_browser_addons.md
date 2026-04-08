Title: Web browser add-ons I use
Date: 2022-02-23
Modified: 2026-03-31
Lang: en
Category: Software
Tags: browser,firefox,web,addons,privacy,security,cryptocurrency
Slug: web-browser-addons

This article lists the web browser extensions I use and why.
I will keep it updated from time to time.

Currently I use [Brave](https://brave.com/) as my main web browser, and is the one I recommend to everyone.
It offers a great experience by default, with features such as a built-in ad blocker, built-in [Tor](https://en.wikipedia.org/wiki/Tor_(network)) integration, vertical and grouped tabs, a decent cryptocurrency wallet, [IPFS](https://en.wikipedia.org/wiki/InterPlanetary_File_System) support, built-in [video calls](https://talk.brave.com/).
The out-of-the-box experience is better than the alternatives in my opinion, especially for regular users who don't know or don't want to tweak their software.

I previously used [Firefox](https://www.mozilla.org/en-US/firefox/new/).
I appreciate that it is the only major browser with its own rendering engine (Gecko) that is not based on the hegemoneous WebKit that is the base of virtually all the other web browsers.
As a web developer I know how dangerous it is to have a monoculture around a single web browser engine, that is what we suffered in the late 90s and early 00s with Internet Explorer.

I try to be careful with the browser extensions I install, as they have deep access to
browser data.
This means a malicious or compromised add-on can quickly become a nightmare if it manages for
example to steal the credentials for my email account (although 2FA should mitigate that
risk).
For this reason I carefully weigh the usefulness of the add-ons versus that risk.
The ones I use are usually popular, with thousands of users
and often editor-picked.

Without further delay, these are the add-ons I'm currently using on Brave:

- [KeepassXC-Browser](https://keepassxc.org/docs/KeePassXC_GettingStarted.html#_setup_browser_integration):
  I use [KeepassXC](https://keepassxc.org/) to hold my passwords and secrets, this is its
  official browser extension which enables form autocomplete. It works pretty well
  although not as well as competitors such as Lastpass or 1Password, but I wouldn't trust
  them with my data.

In Firefox I used to use these extensions:

- [uBlock Origin](https://ublockorigin.com/): the best ad blocker there is. It uses little
  CPU and RAM, usually saves more than it consumes, i.e. web pages load faster without all
  the crap they usually have (banners, tracking scripts, etc.). Especially on mobile it
  can be *very* noticeable. I used to use a bunch of other privacy-related extensions
  (NoScript, ClearURLs, PrivacyBadger, HTTPSEverywhere and DecentralEyes), but after
  reading [this article on
  Arkenfox](https://github.com/arkenfox/user.js/wiki/4.1-Extensions) I learned that they
  are superfluous if uBlock Origin is properly configured.
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
- [Skip Redirect](https://addons.mozilla.org/en-US/firefox/addon/skip-redirect/): detects
  and skips redirects, to avoid unnecessary tracking. For example if you look closely you
  will notice that when clicking on a Google result the URL points to Google, which then
  redirects you to the target. This way Google knows which results you visit. This
  extension extracts the target and goes to it directly, thus avoiding tracking.

Updates:

- 2022-11-19: Replaced Metamask with Tally Ho; added Sidebery.
- 2023-01-20: Added Skip Redirect; removed NoScript, ClearURLs, PrivacyBadger, HTTPSEverywhere, DecentralEyes.
- 2023-04-20: Updated Tally Ho to Taho, they [rebranded in Feb 21, 2023](https://blog.taho.xyz/rename-announcement/).
- 2026-03-31: I now use Brave as my main web browser.
