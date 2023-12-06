Title: Migrating to fish shell
Date: 2023-12-07
Lang: en
Category: Software
Tags: fish,shell,linux
Slug: fish-shell

I'm a heavy shell user.
As a programmer I enjoy the power and flexibility of the shell, so I always keep multiple terminals open (just one keystroke away thanks to [Yakuake](https://apps.kde.org/yakuake/)).

I have been using [Bash](https://www.gnu.org/software/bash/) for as long as I have been a GNU/Linux user, that's 24 years as of the time of this writing.
Back then I didn't think twice about my shell of choice, it was the default and it was much better than what I was used to in Windows and MS-DOS.

With time I discovered that there were other shells and that they were better than *Bash*.
I gave [zsh](https://www.zsh.org/) a good try, with [oh-my-zsh](https://ohmyz.sh/) of course, but it didn't stick.
I was too used to *Bash* and didn't want the hassle of installing a non-default shell.

Fast-forward to early 2023, I heard news that [fish shell](https://fishshell.com/) was [going to rewrite the full project in Rust](https://github.com/fish-shell/fish-shell/pull/9512).
[Full rewrites are dangerous](https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/), but sometimes they are the way to go.
I believe this is the case here: the project is of manageable size so the rewrite shouldn't take that long; it will bring a breath of fresh air and new contributors.

A few months later, the [rewrite is almost done](https://github.com/fish-shell/fish-shell/discussions/10123).
This is great news, it tells me the project is healthy with an enthusiastic community and maintainers.
Reading through the [comments on Hacker News](https://news.ycombinator.com/item?id=38423908) I see a lot of people loving *fish* shell, so I decide to read up more about it.

As I start seriously considering switching to *fish* as my main shell one thing really jumps at me: *fish* is **not** POSIX-compatible.
Do I really want to learn a new syntax?
Rewrite my existing functions and scripts?
I take a look at their documentation and I really like what I see: modern *sane* syntax.
Scripts are actually clean and readable.
Yes, learning new syntax and updating some configuration will be some effort, but I can enjoy it for the rest of my life.
The words "sunk cost fallacy" cross my mind, and I decide to make the jump.

In this article I will highlight the features that sold me on *fish*, go over details on how I ported my *Bash* configuration, mention which plugins I use and share some lessons I learned along the way and the gotchas that bit me.

[TOC]

## Features

I'm not going to go through all of *fish* features, their [tutorial](https://fishshell.com/docs/current/tutorial.html) does a good job at that.

In particular I'm not going to mention the syntax, but it's so much cleaner and readable, it's day and night compared with a POSIX shell like *Bash*.
For example check the `if`, `for` and `switch` syntax.
I also encourage you to compare the *Bash* and *fish* versions of some of my custom functions side-by-side (more on that in their dedicated section below).

Here I will focus on features that set *fish* apart and sold me on it.

### Autocomplete

You get a lot out of *fish* without writing any configuration.
For example the out-of-the-box autocomplete experience is amazing.
I encourage you to give it a try by just installing *fish* and running it, no configuration necessary!

Autocompleting commands:

[
![fish autocompletion for commands]({static}/images/migrating_fish_shell/autocomplete_command.webp "Click to see full size"){: .align-center}
]({static}/images/migrating_fish_shell/autocomplete_command.webp" "Click to see full size")

Autocompleting arguments, with help extracted from man pages!

[
![fish autocompletion for arguments]({static}/images/migrating_fish_shell/autocomplete_args.webp "Click to see full size"){: .align-center}
]({static}/images/migrating_fish_shell/autocomplete_args.webp" "Click to see full size")

### Multiline, autoindent, syntax highlighting

Another great feature is the [multiline support](https://fishshell.com/docs/current/interactive.html#multiline-editing) in interactive mode, with [automatic indent](https://fishshell.com/docs/current/cmds/fish_indent.html) and [syntax highlightning](https://fishshell.com/docs/current/tutorial.html#syntax-highlighting):

![Multiline edit with autoindent and syntax highlightning]({static}/images/migrating_fish_shell/multiline_autoindent.webp){: .align-center}

When bringing back a multiline command from history I can press *Ctrl+e* to move around it and edit it in the shell, or *Alt+e* to open it in my editor.
Oh and `fish_indent` also automatically formats my fish scripts in Emacs when using [fish-mode](https://github.com/wwwjfy/emacs-fish).
*Nice!*

It's worth mentioning that the syntax highlighting is not just the colors of functions, variables, strings, etc., but it also marks errors in red.
Quoting [the documentation](https://fishshell.com/docs/current/interactive.html#syntax-highlighting):

> Detected errors include:
>
> - Non-existing commands.
> - Reading from or appending to a non-existing file.
> - Incorrect use of output redirects
> - Mismatched parenthesis

### Colors, themes and prompts

Just run `fish_config` and you will get a nice web UI to interactively choose theme, change individual colors, change the prompt, browse through all defined functions, browse variables, search the history and remove individual records, and see and edit keybindings.

[
![fish_config web interface]({static}/images/migrating_fish_shell/fish_config_web.webp "Click to see full size"){: .align-center}
]({static}/images/migrating_fish_shell/fish_config_web.webp" "Click to see full size")

Don't like the web?
`fish_config theme show` will display available themes, with a preview:

[
![fish_config theme show]({static}/images/migrating_fish_shell/fish_config_theme_show.webp "Click to see full size"){: .align-center}
]({static}/images/migrating_fish_shell/fish_config_theme_show.webp" "Click to see full size")

`fish_config theme choose <theme>` will set the theme you want in the current session.
`fish_config theme save` will save the current selection as universal variables, applied on next startup.

Analogously `fish_config prompt show` will display different available prompts, `fish_config prompt choose <prompt>` will apply to current session, and `fish_config prompt save` will save the current configuration as universal variables.

See the full documentation for [fish_config](https://fishshell.com/docs/current/cmds/fish_config.html).

### And the list goes on

- [History search](https://fishshell.com/docs/current/interactive.html#searchable-command-history) with pagination and individual word search.
- [Directory history](https://fishshell.com/docs/current/interactive.html#id13).
- Expandable programmable [abbreviations](https://fishshell.com/docs/current/interactive.html#abbreviations).
- [Private mode](https://fishshell.com/docs/current/interactive.html#private-mode) which doesn't display past history nor records any.
- [Advanced argument parsing](https://fishshell.com/docs/current/cmds/argparse.html).
- [Debugging support](https://fishshell.com/docs/current/language.html#debugging-fish-scripts).
- [Event handlers](https://fishshell.com/docs/current/language.html#event-handlers).

## Porting my Bash configuration

My full configuration is at my [dotfiles repository](https://github.com/haplo/dotfiles).
*Fish* configuration is in [.config/fish/](https://github.com/haplo/dotfiles/tree/master/.config/fish).
It respects the [XDG Base Directory Specification](https://wiki.archlinux.org/title/XDG_Base_Directory), which is another thing I like about *fish* shell.

My *Bash* configuration was nothing terribly complicated, mostly some [aliases](https://github.com/haplo/dotfiles/blob/e24ef4d8d947cd40360223d90542873f1931c6bf/.aliases), [exports](https://github.com/haplo/dotfiles/blob/e24ef4d8d947cd40360223d90542873f1931c6bf/.exports) and [functions](https://github.com/haplo/dotfiles/blob/e24ef4d8d947cd40360223d90542873f1931c6bf/.functions), plus redefining the prompt, enabling autocompletion...

Porting to *fish* meant learning the new syntax and features.
Most of the time reading the fine [fish documentation](https://fishshell.com/docs/current/index.html) was enough to get me on my way.
Special kudos for their [fish for Bash users doc](https://fishshell.com/docs/current/fish_for_bash_users.html).

My porting process can be broken down like this:

1. Port environment exports.
2. Port aliases.
3. Port functions.
4. Add plugins.
5. Adjust my `init_dotfiles` script.
6. Script to update vendored plugins.

### Porting environment exports

This was fairly straightforward, just used `set -gx VAR value` in [`~/.config/fish/conf.d/exports.fish`](https://github.com/haplo/dotfiles/blob/master/.config/fish/conf.d/exports.fish).

Some exports I like to do conditionally, so the configuration works on a variety of systems that might not have my favored tools (e.g. prefer `most` over `less`, or `exa/eza` over `ls`).

```fish
if type -q most
    set -gx PAGER most
    set -gx MANPAGER most
else if type -q less
    set -gx PAGER less
    # don’t clear the screen after quitting a manual page
    set -gx MANPAGER 'less -X'
end
```

I will probably end up moving many of these global exports to universal variables installed by `init_dotfiles` script.
More on that below.

### Porting aliases

Initially I ported my [*Bash* aliases](https://github.com/haplo/dotfiles/blob/c4ce95ba9902aee856811df5902644e12adf0821/.aliases) using *fish* `alias` and didn't think twice about it.
Turns out that [*fish* aliases become functions under the hood](https://fishshell.com/docs/current/language.html#defining-aliases), i.e. *fish* `alias` is just a wrapper for creating functions.

I discovered that *fish* has something called [abbreviations](https://fishshell.com/docs/current/cmds/abbr.html), which get expanded into their full form after pressing *Space* or *Enter*.
This has a number of benefits:

1. Faster than functions.
2. Commands appear in full in history.
3. Can edit after expansion.
4. Can optionally be expanded anywhere in the prompt, not just at the beginning.

I [rewrote all my aliases into abbreviations](https://github.com/haplo/dotfiles/commit/c988edae4c93dfa3804dc78b569881a085f4d941), as they were all command expansions, appearing at the beginning of the prompt.

A *fish* abbreviation can be configured to appear anywhere in the prompt by using `--position anywhere`.
I'm not using this feature yet but will be on the lookout to see where it will come in handy.

Oh and if you want to keep *fish* from expanding an abbreviation just press *Ctrl+Space*.

### Porting functions

I have a few [Bash functions](https://github.com/haplo/dotfiles/blob/b9887e4b1525d08f8b9a4cf6a442e70a00bafa38/.functions) for some repetitive tasks.
I could have extracted them into separate scripts with `#!/bin/bash` shebangs and placed somewhere in `$PATH` to keep executing them same as before.
But I wanted to give *fish* a test ride, so I decided to rewrite them.
And boy was I glad I did!
Just this little practice made me feel comfortable with *fish* syntax and I learned some valuable lessons by reading the documentation.

These are my ported functions as of the time of this writing:

- [cbr2cbz](https://github.com/haplo/dotfiles/blob/master/.config/fish/functions/cbr2cbz.fish): to transform digital comic books in [CBR format to CBZ](https://en.wikipedia.org/wiki/Comic_book_archive).
- [mkd](https://github.com/haplo/dotfiles/blob/master/.config/fish/functions/mkd.fish): create a directory (with arbitrary level of nesting) and *cd* into it.
- [mts2mkv](https://github.com/haplo/dotfiles/blob/master/.config/fish/functions/mts2mkv.fish): transform MTS video files into MKV. Some of my digital cameras create MTS videos.
- [nds](https://github.com/haplo/dotfiles/blob/master/.config/fish/functions/nds.fish): get a [NodeJS](https://nodejs.org/) shell inside a [Podman](https://podman.io/) container. I don't trust *npm* installing gigabytes of unvetted dependencies in my systems.
- [pdf2cbz](https://github.com/haplo/dotfiles/blob/master/.config/fish/functions/pdf2cbz.fish): transform PDF into CBZ, meant for digital comic books. Internally uses `pdfextractimages` function.
- [pdfextractimages](https://github.com/haplo/dotfiles/blob/master/.config/fish/functions/pdfextractimages.fish): extract all JPEG and PNG images from a PDF.
- [splitflac](https://github.com/haplo/dotfiles/blob/master/.config/fish/functions/splitflac.fish): takes music in the form of a single big FLAC file + a CUE file and creates separate FLAC files for each track, with proper tags.
- [urldecode](https://github.com/haplo/dotfiles/blob/master/.config/fish/functions/urldecode.fish) and [urlencode](https://github.com/haplo/dotfiles/blob/master/.config/fish/functions/urlencode.fish): simple convenience functions to encode and decode URLs.

I'm still a fledgling *fish* user, so some bits might not be idiomatic.
If you want to help me improve them, pull requests are welcome!

### Plugins

One of the things I like about *fish* is that the default experience is already great with zero configuration.
That means if I ever found myself in a fresh or strange environment it wouldn't differ much from my custom setup.
But also that I would spend less time customizing.
I already spend too much time bikeshedding [my Emacs](https://github.com/haplo/dotemacs). 😁

Nonetheless there are some great plugins that are worth installing.
[awsm.fish](https://github.com/jorgebucaran/awsm.fish) has a curated list of plugins and other *fish* resources.

In my case I narrowed it down to three plugins, as I like to keep things simple:

- [pure prompt](https://github.com/pure-fish/pure)
- [fzf.fish](https://github.com/PatrickF1/fzf.fish)
- [foreign-env](https://github.com/oh-my-fish/plugin-foreign-env)

#### pure prompt

I considered the three main prompt plugins for fish:

- [tide](https://github.com/IlanCosman/tide)
- [pure](https://github.com/pure-fish/pure/)
- [hydro](https://github.com/jorgebucaran/hydro)

I liked *tide* the most, but to minimize dependencies and simplify setup for now I settled on *pure*.

I will probably review this decision in the future.

#### fzf.fish

[fzf](https://github.com/junegunn/fzf) is seriously amazing, a project that I can recommend hands down.
I have been using it with *Bash* for a while now, and it's the first integration I look for.

[fzf.fish](https://github.com/PatrickF1/fzf.fish) is the best fzf plugin for fish.
It allows you to:

- [Search the current directory](https://github.com/PatrickF1/fzf.fish#-search-directory) (recursively), with preview of the files as you scroll.
- [Search in git log](https://github.com/PatrickF1/fzf.fish#-search-git-log), with preview of the commits.
- [Search git status](https://github.com/PatrickF1/fzf.fish#-search-git-status), with diff of the changes of each file.
- [Search shell history](https://github.com/PatrickF1/fzf.fish#-search-history), improving upon fish's already good search.
- [Search processes](https://github.com/PatrickF1/fzf.fish#%EF%B8%8F-search-processes), showing details in the preview area.
- [Search variables](https://github.com/PatrickF1/fzf.fish#-search-variables).

I'm purposefully not including screenshots of *fzf.fish* as its README already includes a video and screenshots, do take a look at them.

#### foreign-env

[foreign-env](https://github.com/oh-my-fish/plugin-foreign-env) is a little plugin to load *Bash*-syntax exports directly onto fish, without having to instantiate *Bash*.
I use it to source /etc/profile so I can make *fish* my default shell, more details about that in the *Gotchas* section below.

#### Vendoring third-party plugins

Plugin managers like [fisher](https://github.com/jorgebucaran/fisher) or [oh-my-fish](https://github.com/oh-my-fish/oh-my-fish) are a convenient way of installing plugins, but the problem is that they download and run unsigned code.
This is something that I avoid doing as much as possible, as it's a big security hole.

For my fish configuration I decided to vendor them, i.e. include a full copy inside my configuration.
This way I have better assurances about the code that my computers will be running.
This is particularly important for the shell, even more when I aim to make it my global default.

I put the plugins code in a [dedicated vendor directory](https://github.com/haplo/dotfiles/tree/master/.config/fish/vendor).
Then my [init_dotfiles script](https://github.com/haplo/dotfiles/blob/b9887e4b1525d08f8b9a4cf6a442e70a00bafa38/init_dotfiles.sh#L15-L17) copies the vendor files into the right locations. I could have done without the *vendor* directory altogether, but I think keeping them separate is more respectful of the original creators.

The second part is to keep the plugins up to date.
I wrote the [update_vendor.fish script](https://github.com/haplo/dotfiles/blob/master/update_vendor.fish) that I will run from time to time.
It downloads the latest version of the plugins I use and puts the files in my [vendor directory](https://github.com/haplo/dotfiles/tree/master/.config/fish/vendor).
If there are any changes I can review them before committing them to my repository.

## Lessons learned

In the process of moving my *Bash* configuration to *fish* and reading through their documentation I learned some things I think are useful and not immediately obvious.
I will share them here in hope that they may be helpful to other people looking to migrate to *fish*.

### Lesson 1: function autoloading

*Fish* [autoloads functions](https://fishshell.com/docs/current/tutorial.html#autoloading-functions) when needed.
That means even if you have hundreds of files in your `~/.config/fish/functions` directory, they won't all be eagerly loaded when a shell starts, but only when you invoke a function with a name that matches the file name.

A function file can still define multiple functions, but it will only get loaded when the exact name **of the file** is invoked in a shell.

### Lesson 2: error handling with and/or chaining

[`and` and `or` combiners](https://fishshell.com/docs/current/language.html#combiners-and-or) are a neat way of handling command successes and errors.
For example:

```fish
tar xvf file.tgz
and echo "Extracted!"
or echo "Error!" && return 1
```

However the *fish* documentation advises not to overuse chaining with `and` and `or`, as it can lead to wrong code paths being taken.
Instead it recommends using `if` even if a bit more verbose:

```fish
if tar xvzf file.tgz
    echo "Extracted!"
else
    echo "Error!"
    return 1
end
```

### Lesson 3: string built-in

The [`string` builtin](https://fishshell.com/docs/current/cmds/string.html#match-subcommand) is powerful, ergonomic and readable, worth learning and using.

[`string match`](https://fishshell.com/docs/current/cmds/string.html#match-subcommand) has both simple globbing syntax or Perl-compatible regexes (I wonder if the syntax will change to Rust's regexes after the rewrite).
It can capture groups, ignore case, do partial or entire string match...
An example from my `pdfextractimages` function:

```fish
# check that $pdffile ends in .pdf
else if not string match -q -i -e '*.pdf' $pdffile
    echo "$pdffile doesn't seem to be a PDF file"
    return 3
```

[`string split`](https://fishshell.com/docs/current/cmds/string.html#split-and-split0-subcommands) is a nice replacement for `cut`:

```fish
> string split . example.com
example
com

# one single split on the right
> string split -r -m1 / /usr/local/bin/fish
/usr/local/bin
fish
```

[`string replace`](https://fishshell.com/docs/current/cmds/string.html#replace-subcommand) is featureful and clean, can do simple string replacement or regex, including capturing groups:

```fish
# simple substitution blue -> red, first appearance only!
> string replace blue red 'blue is my favorite blue'
red is my favorite blue

# substitute all appearances with -a
> string replace -a blue red 'blue is my favorite blue'
red is my favorite red

# replace .pdf extension with .cbz using a regex
> string replace -r '.pdf$' .cbz somedocument.pdf
somedocument.cbz
```

I found this idiom with `string replace --filter ...` where it first attempts to match input with the given pattern.
I pair that with `and` and `or` for error control.
For example in my `cbr2cbz` function I replace the *.cbr* extension with *.cbz* and at the same time detect if the input is invalid:

```fish
set cbzfile (string replace -f -r '.cbr$' .cbz $cbrfile)
or echo "$cbrfile doesn't seem to be a .cbr file" && return 2
```

One last example is that `string escape` and `string unescape` support multiple styles, so I was able to [refactor my urlencode and urldecode functions](https://github.com/haplo/dotfiles/commit/820dd0b21dcb9e39c0ee72a382cbc29b54ba3315) to drop their Python dependency.

### Lesson 4: globbing

An important difference with *Bash* and other shells is [globbing behavior](https://fishshell.com/docs/current/fish_for_bash_users.html#wildcards-globs).

An empty glob results in an error in *fish* when used on a command, but not with `set`, `for` or `count`.
This is often a good thing to avoid gotchas.

For example this code was failing sometimes because the glob was empty (no images to zip):

```fish
zip -9 --move --junk-paths --quiet $cbzfile $tmpdir/*.{jpg,JPG,jpeg,JPEG,png,PNG}
```

I rewrote it to use `set`:

```fish
set images $tmpdir/*.{jpg,JPG,jpeg,JPEG,png,PNG}
if test (count $images) -eq 0
    echo "No images extracted, stopping"
    return 7
end

zip -9 --move --junk-paths --quiet $cbzfile $images
```

Also of note is that *fish* [deprecated the `?` single-character glob](https://fishshell.com/docs/current/language.html#wildcards-globbing), and will disable it in the future.
I like it because it makes working with URLs in the shell easier.
In the same vein I like that *fish* only treats `&` as the special character to [run a program in background](https://fishshell.com/docs/current/language.html#job-control) if it's followed by a non-separating character.
No more having `wget`, `curl` or `yt-dlp` run as a background job because I forgot to quote the URL.

### Lesson 5: variable defaults

There is no way in *fish* to set a default value for a variable, something that can come in handy when defining functions.

Currently I use code like this:

```fish
set output $argv[2]
# default to current directory
test -z $output; and set output .
```

### Lesson 6: array variables and slices

*Bash* supports [arrays](https://www.gnu.org/software/bash/manual/html_node/Arrays.html), both index-based and associative.
But the syntax is ugly and hard to remember.
Access elements with `${array[i]}`, instead of just `$array[i]`.
Count the number of elements with `${#array[@]}` (notice the `#`?).
I rarely used arrays in *Bash*, and when I did I had to constantly look at references.

*fish* has [lists](https://fishshell.com/docs/current/language.html#variables-lists), which are functionally the same, but the syntax is what you would expect coming from other programming languages:

```fish
> set fruit apple orange banana mango pineapple

# indexes are 1-based
> echo $fruit[1]
apple

# negative indexing
❯ echo $fruit[-1]
pineapple

# slices
❯ echo $fruit[1..3]
apple orange banana

# reverse slices
❯ echo $fruit[3..1]
banana orange apple

# multiple indexes in one expression
❯ echo $fruit[3 5 2]
banana pineapple orange

# multiple slices in one expression, even with repetitions
❯ echo $fruit[1..3 2..4]
apple orange banana orange banana mango

# number of elements
❯ count $fruit
5
```

Do note that [path variables](https://fishshell.com/docs/current/language.html#variables-path) (those ending with `PATH`) are treated especially: the elements are joined with colons when exported.
This is for compatibility with other shells and programs that might not support arrays.

### Lesson 7: keybindings

Do read on [fish keybindings](https://fishshell.com/docs/current/interactive.html#shared-bindings), there are some hidden gems.
Some highlights:

- *Alt+←* moves to the previous directory in the [directory history](https://fishshell.com/docs/current/interactive.html#id13), *Alt+→* moves forward.
- *Alt+↑* and *Alt+↓* search through history for **tokens** containing the token under cursor.
If for example you are looking for PDF files used in the history, you can type `.pdf` and then *Alt+↑* will search for other tokens with that component.
- *Alt+H* opens the man page for the current command.
I don't know about you but I find myself opening new shells to look up man pages for the command I'm trying to use all the time.
This and *fish* autocomplete are an invaluable help.
- *Alt+O* opens the file under cursor in the `$PAGER`.
- *Alt+E* or *Alt+V* open the current prompt in the `$EDITOR`.
Useful for editing multi-line prompts comfortably.

There is support for both [Emacs style](https://fishshell.com/docs/current/interactive.html#emacs-mode-commands) and [Vi style](https://fishshell.com/docs/current/interactive.html#vi-mode-commands) modes.

*fish* makes it easy to [add new bindings](https://fishshell.com/docs/current/interactive.html#custom-bindings).

## Gotchas

### Sourcing /etc/profile

[One](https://github.com/fish-shell/fish-shell/issues/3665) [common](https://github.com/fish-shell/fish-shell/issues/9887) [issue](https://github.com/sddm/sddm/issues/1059) when running *fish* as default shell (hint: `chsh`) is that it doesn't run */etc/profile* and */etc/profile.d/\** scripts, as they are not in *fish* syntax.
For me this manifested in a blank screen when loading my graphical environment.
I had to get to the console, login as root and change my user's default shell back to *Bash*.

A workaround is to leave *Bash* as default shell and run *fish* only interactively.
One way of doing this is to add this to the end of `~/.bashrc` (as proposed [here](https://github.com/fish-shell/fish-shell/issues/3665#issuecomment-326806107)):

```bash
[ "$PS1" -a -x /bin/fish ] && exec fish
```

This loads up *Bash*, but replaces the process with *fish*.
It's inefficient but probably negligible with today's computers.
Still it leaves a bad taste in my mouth.

The [Archlinux Wiki on fish](https://wiki.archlinux.org/title/Fish#Source_/etc/profile_on_login) documents this way of sourcing `/etc/profile` in login shells by using *Bash* and then replacing it with a *fish* process:

```fish
# add to ~/.config/fish/config.fish
if status is-login
    exec bash -c "test -e /etc/profile && source /etc/profile;\
    exec fish"
end
```

However this was not working for me, my desktop environment was still not loading.

My current solution is to use the [foreign-env plugin](https://github.com/oh-my-fish/plugin-foreign-env) to load the profile:

```fish
# add to ~/.config/fish/config.fish
if status is-login && test -e /etc/profile
    fenv source /etc/profile
end
```

This works for me in Kubuntu 22.04 LTS, I now have *fish* as my default shell, login and interactive.

## Closing words

It's only been a few days with *fish* as my main driver, but I have been pleasantly surprised by its features.
Time will tell whether I find any bumps along the road, but I get the feeling that if anything I will regret not making the switch *sooner*.

One thing that was bugging me is whether this change would be productive or worth it.
It's still early to answer that question, but I can tell you that it was **fun** and **joyful**, like a good vacation.
And sometimes that makes it worth it.

Looking forward to that Rust rewrite!

Thank you *fish* team!
