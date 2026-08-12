Title: Custom git trailers with Magit
Date: 2026-08-12
Lang: en
Category: Software
Tags: ai,emacs,free-software,howto,programming
Slug: emacs-custom-magit-trailers

Git trailers are just lines of text at the bottom of a commit that take note of some
metadata. Common ones are `Co-Authored-By`, `Reported-By`, `Reviewed-By` or
`Signed-Off-By`, all of them autodescriptive I think.

Magit has a way of adding trailers, just press `C-c TAB` or `C-c C-i` in commit
view. Magit will then display a transient menu with some options:

![Magit insert trailer menu]({static}/images/emacs_magit_custom_trailer/emacs-magit-insert-trailer-menu.png)

Nowadays it's becoming commonplace to use the [`Assisted-by:`
trailer](https://github.com/microsoft/vscode/issues/313962) to credit AI coding agents,
and I wanted to start using it as I'm doing most of my coding with AI support now.
Magit doesn't support this trailer (yet!), but I had my AI figure out how to add it.

In this small HOWTO I will show you how to add a new kind of commit trailer to Magit, so
it will be just a `C-c TAB` away. I will use the `Assisted-by` example, but you can
tweak it to anything you need. It prompts for a value (free text, e.g. `Kimi K3` or
`venice/zai-org-glm-5-2`) and appends it to the commit buffer as `Assisted-by: <value>`
after any other existing trailers.

It remembers previously entered values, which are offered as completion. As a bonus I
will show how to configure Emacs' built-in `savehist` package to persist that history
across Emacs sessions.

## Magit config

```elisp
(use-package magit
  :preface
  (defvar my-git-commit-assisted-history nil
    "History of values entered for `my-git-commit-assisted'.")
  (defun my-git-commit-assisted ()
    "Insert an \"Assisted-by\" trailer crediting an AI coding agent.
Prompt for the agent description (free text, e.g. \"Claude Opus 4.7\"),
offering previously entered values as completion."
    (interactive)
    (let ((value (completing-read "Assisted by: "
                                  my-git-commit-assisted-history
                                  nil nil nil
                                  'my-git-commit-assisted-history)))
      (when (string-empty-p value)
        (user-error "Empty agent description"))
      ;; NOTE: `git-commit--insert-trailer' is a private API; magit
      ;; offers no public function for inserting an arbitrary trailer.
      (git-commit--insert-trailer "Assisted-by" value)))
  :config
  ;; C-c TAB A or C-c C-i A inserts the trailer
  (transient-append-suffix 'git-commit-insert-trailer 'git-commit-test
                           '("A" "Assisted" my-git-commit-assisted))
  (add-to-list 'git-commit-trailers "Assisted-by"))
```

How it works:

- `transient-append-suffix` appends the command to
  `git-commit-insert-trailer` (`C-c TAB`) right after the built-in
  "Co-developed" entry, so it shows up as `A` in the trailer menu.
- Prompt for the value happens by `completing-read` in the minibuffer, so you get your
  configured completion system (I use [vertico](https://github.com/minad/vertico)) to
  pick among the candidates, or input free text.
- Insertion goes through the same internal helper magit uses for
  `Signed-off-by`, so the trailer lands after existing trailers and
  before the comment/diff section regardless of buffer layout.
- Adding `"Assisted-by"` to `git-commit-trailers` makes the token
  font-lock like the built-in ones.  This is needed because values are
  free text; magit only highlights arbitrary tokens when they have the
  `Name <email>` shape.
- A note for old Magit users: the trailer menu used to be
  `git-commit-insert-pseudo-header`; it is now an obsolete alias for
  `git-commit-insert-trailer`.

## Bonus: remember values across sessions with savehist

Out of the box the completion history dies with the Emacs session, which is unfortunate
because most of the time we will be entering the same values again and again. By
enabling `savehist-mode`, every minibuffer history variable is saved automatically once
used — this history included — so often *nothing extra is needed besides having the mode
enabled*.  If you'd rather state the intent explicitly (or you save only a whitelist by
setting `savehist-save-minibuffer-history` to `nil`), register it:

```elisp
(use-package savehist
  :config
  (setq savehist-additional-variables
        '(my-git-commit-assisted-history))
  (savehist-mode +1))
```

Ordering matters: `savehist-mode` restores once when enabling it, so if you put it
before setting `savehist-additional-variables` then you would see the new variables
(`my-git-commit-assisted-history` in my case) get stored in the `savehist` file, but
they would not be restored when Emacs starts again. Ask me how I know.

## Closing thoughts

I dislike having to use a private var like `git-commit--insert-trailer`, it's something
that might break at any point. But I'm OK with it because it's very localized and in a
non-critical functionality that I won't mind if it ever breaks. If it happens I will
remember to update this post.

About `Assisted-by`, I plan on using it extensively, I want to be very honest about my
AI use.

Are you using `Assisted-by` or other commit trailers?
