Title: Omarchy and my Security Sweet Spot
Date: 2026-09-01
Lang: en
Category: Software
Tags: free-software,linux,personal,privacy,security
Slug: omarchy-security-sweet-spot

[Omarchy](https://omarchy.org/), the [omakase](https://en.wikipedia.org/wiki/Omakase)
Linux distribution created by [David Heinemeier Hansson](https://x.com/dhh) of Ruby on
Rails fame, is currently a hot topic among the open source crowd. [Some people love
it](https://x.com/bonkcity_/status/2094225788987961854?s=20), [some people hate
it](https://x.com/jpschroeder/status/2094494281129918592?s=20).

I will be clear: I'm on the love wagon for Omarchy. There is a lot to like at first
sight: the optimism; the can-do will-do attitude ([we can fix
everything](https://x.com/dhh/status/2094501042306113598?s=20)); [bringing people
together](https://x.com/dhh/status/2092129715662242179?s=20); [making computers fun
again](https://x.com/dhh/status/1963822469829329203?s=20); [distancing from
politics](https://x.com/dhh/status/2093681834265567463?s=20); [focus on
performance](https://x.com/dhh/status/2092479124807852504?s=20)... Heck, I **love the
default UX**: the modern tiling WM; the keyboard-driven approach; even the aesthetics. I
am in the target demographic, I would be using it with few changes off the defaults.

This article however will focus on the technical reasons **why I won't be installing
Omarchy yet**. It boils down to what I call the **security sweet spot**.

## Security sweet spot

I take security and privacy seriously, as I believe our digital lives have an ever
growing importance. I want to protect my data, to be conscious of where it lives, who
has access to what, and not to hand it over to third parties when I can avoid
it. Towards this end I put a lot of effort into my security and privacy practices, which
means I spend hours reading, learning, planning and implementing changes. But besides
that it also adds day-to-day friction and pain, because the choices I make determine how
I interact with my devices. Finding the **right balance** of security and privacy **for
me** is something that I have been pondering for years.

I like to think about the intersection of my data and my computing devices as circles,
with the most trusted devices having access to the most intimate data.

[
![Data Trust Zones]({static}/images/omarchy_security_sweet_spot/data_trust_zones.webp "Click for full screen"){:.align-center}
]({static}/images/omarchy_security_sweet_spot/data_trust_zones.webp "Click for full screen"){:target="_blank"}

Under this diagram I have to trust the integrity of my computer more than I trust my
mobile devices (cellphone, tablet). This makes not only my choice of OS, but how I
configure and use it, a key decision.

# The evolution of my sweet spot

To better understand how my security sweet spot has shifted, I'll walk through the
history of my computer OS of choice:

<div align="center">
ZX Spectrum (late 80s)<br/>
↓<br/>
MS-DOS (early 90s)<br/>
↓<br/>
Windows (late 90s)<br/>
↓<br/>
Debian (00s)<br/>
↓<br/>
Kubuntu (early 10s)<br/>
↓<br/>
Qubes OS (late 10s)<br/>
↓<br/>
Arch Linux (20s until now)<br/>
</div>

I started my computing journey on a ZX Spectrum+ in 1988, it was just games and some
[BASIC](https://en.wikipedia.org/wiki/BASIC). An IBM PC with
[MS-DOS](https://en.wikipedia.org/wiki/MS-DOS) came a few years later, and eventually
Windows 3.11. With no Internet access to be had at home, and virtually no personal data
on my devices (just some schoolwork), privacy wasn't on anybody's mind, or rather it was
taken for granted.

Then with Windows 95 I eventually got on the Internet through dial-up, and later ADSL. I
started interacting in online communities, downloading media and software. I was a
teenager, but luckily sensible enough to use a nickname and not to post names or
addresses publicly.

The move from Windows to Debian (after experimenting with other Linux distributions
first) was almost an inevitability after getting pilled by the [free-software
movement](https://www.gnu.org/philosophy/). I realized I couldn't trust closed-source
software, and felt increasingly uncomfortable with Windows. Once I switched I missed my
games (only a few I managed to run with [Wine](https://www.winehq.org/)), but I decided
to move to console gaming to scratch that itch. My digital sovereignty was more
important.

Debian is an amazing distribution, and still my chosen one for servers to this day, but
its long gaps between stable releases has always made it a harder sell for
desktops. Yes, I used [backports](https://backports.debian.org/), and I ended up running
[sid](https://www.debian.org/releases/sid/), but that meant more instability and
breakages occurring from time to time. That's why I ended up moving my laptop to Ubuntu
(eventually settling on its [Kubuntu](https://kubuntu.org/) flavor), and it was good for
a while.

Then I was introduced to [Qubes OS](https://www.qubes-os.org/) by a friend in 2016, and
I was blown away by its improved security posture. If you don't know about Qubes OS you
might want to [read its
introduction](https://doc.qubes-os.org/en/latest/introduction/intro.html) to realize how
different a desktop computer OS could be. If you are feeling lazy the summary is this:
in a traditional computer OS all running software gets full access to the computer, to
all its files and devices; in Qubes OS however there is a very thin core component of
the OS (what they call *Dom0*) with minimal trusted software, and then absolutely
everything else runs in **independent isolated virtual machines**. That means if you
ever run malicious software (virus, trojans, spyware, ransomware, supply chain
attacks...), it wouldn't automatically hijack the whole computer and all its
data. Breaking the barriers of a VM is not impossible but it is a much harder
proposition than other containerization options. It's considered the gold standard of
software security, barring running in separate hardware altogether.

I ended up getting a new laptop in 2017 and I installed Qubes OS. I ran it successfully
for several years. I felt empowered, confident to run any software with the peace of
mind that it couldn't harm my computer, nor access any data it wasn't meant to. However
the day-to-day pain proved to be too much for me. The slowness, even with
hardware-accelerated VMs, made daily tasks more painful: browsing the web, opening
images or PDFs, and particularly my [photography
workflow]({filename}/photography/2022-03-31_photography_workflow.md) was heavily
impacted. After a few years I decided that this much security was not warranted for my
personal needs, and that I had tilted the balance too much in that direction.

This led me to my last transition. I got a new desktop computer, and settled on Arch
Linux for its breadth of up-to-date software and malleability to configure it how I
wanted to. I implemented some security practices that would move me towards my sweet
spot of security, privacy and UX, like [UKI-based end-to-end Secure
Boot](https://github.com/max-baz/arch-secure-boot) and [lightweight sandboxing of
software](https://github.com/netblue30/firejail/). I use [KDE](https://kde.org/) because
it's familiar and very configurable, but modern tiling WMs are very appealing to me, I just
cannot justify the time to set one up right now.

## What I will be looking for in my future desktop OS

I'm in a happy place right now, with a personal ecosystem that is comfortable and secure enough for my needs. However the hacker mind is restless, and I'm always thinking of how it could be improved.

This is my wish list of features I'd like to see in my next desktop OS:

1. **Great UX out of the box**. Fast. Responsive. Enjoyable day-to-day. Keyboard-driven. Beautiful. Omarchy already fulfills this point for me, which is what prompted me to write this article.

2. **Sandboxed software**. Most programs should run in a sandbox by default, in a way
   that is abstracted away from the user so UX is not impacted. I don't mind prompts for
   permissions, usually they will be one-time for each program, and a good compromise
   for security. Have a good GUI to manage permissions, including which files or
   directories a program has access to (read and/or write).
   
3. **Audited updates**. After [implementing AI review for the upgrade of my Emacs
   packages]({filename}/software/2026-08-08_emacs_straight_ai_review.md) I've been
   thinking how much I'd like to have the same for my whole OS. I want some guarantee
   that the software has been audited before it lands on my machine. This is no simple
   proposition, there are many challenges to overcome, first of all being the sheer size
   and cost, but I believe there might be solutions through crowdfunding. I think this
   could be a killer app for Linux, as a closed-source OS wouldn't be able to compete in
   this arena; you have to trust a third party and can't just trust the code. I'm
   planning an article to expand on this idea, and maybe I'll work on it as a future
   project if nobody else picks it up first.

4. **Declarative configuration**. I kinda regret not jumping onto the
   [NixOS](https://nixos.org/) bandwagon instead of deciding on Arch Linux as my latest
   OS. The reproducibility, ability to share complex configs and to rollback mistakes is
   very powerful. Plus AI agents simplify making changes. Which leads me to my next
   point.

5. **AI-first**. As readers of my blog are already aware of, I've already embraced AI
   and I'm using it heavily. I'm fully convinced it's here to stay and we need to
   integrate it and build new systems around it to better serve us. I use it to code, to
   research, to debug, to learn, to create. However [constraining
   AIs]({filename}/software/2026-05-14_how_i_sandbox_ai_agents.md) to satisfy my desire
   for security and privacy hasn't been as straightforward as I'd like. I want my agents
   to have restricted access to only what they need to get the job done. I want to see
   an execution plan that I can review and approve. I won't trust an AI with my most
   personal data unless it runs on my own premises. My ideal OS would integrate AI, but
   properly sandboxed to cover these and probably other use cases. **Omarchy already
   integrates AI** at the OS level, but I'd ask for it to be properly sandboxed.

Nowadays I'm busy with other projects that demand my attention, including a big home
remodeling and executing on my [new
homelab]({filename}/software/2026-01-25_self_hosted_home_1.md). These endeavors will
keep me entertained for several months, during which I would rather not get distracted
by also moving my main computer to another OS. However once the house and the homelab
are fully up and running I plan on revisiting my choice of desktop OS, at which point I
will come back to this wish list and see which Linux distributions implement some of
these goals.

Omarchy is improving at an astonishing pace, growing its user base and number of
contributors by the thousands. Most of the improvements I read about seem to focus on
the desktop and UX, but I wish this humble list gives some food for thought about deeper
OS architecture in terms of security and privacy.

In any case I really hope that the positivity that I see in Omarchy lives on. I, for
one, am rooting for them.

Got any ideas or feedback? I'd love to hear from you in the comments below, or you can
[mention me on X](https://x.com/ampajaro).
