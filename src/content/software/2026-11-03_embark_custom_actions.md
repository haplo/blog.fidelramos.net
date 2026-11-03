Title: Supercharging Embark: custom actions for Org, Magit and gptel
Date: 2026-11-03
Lang: en
Category: Software
Tags: emacs,howto
Slug: embark-custom-actions

[Embark](https://github.com/oantolin/embark/) is a package for Emacs that turns whatever
is at point (a file, URL, region, symbol) into a *target* with a context menu of
actions, invoked with `embark-act` (I bind it to `C-.`). Think of it like right-click
with the mouse over an item. It's very handy when you start doing something,
e.g. finding a file to open it, but wish to execute a different action over it instead.

In this HOWTO I present some custom embark actions I have added to my Emacs configuration:

1. Storing Org links to files, dirs, URLs and Magit commits
2. Open Magit and terminals on directories
3. Sending things to an LLM
4. A few tweaks to use *jinx* and *helpful*.

Each section shows the code and the keybinding I define.

[TOC]

## Prerequisites

I assume [use-package](https://www.gnu.org/software/emacs/manual/use-package.html)
(built into Emacs 29+) and embark installed and bound:

```elisp
(use-package embark
  :bind (("C-." . embark-act))
  :config [...]
  )
```

Every snippet below goes inside that block's `:config`. The pattern is always the same:
define a command that receives the target through its interactive spec, then
`keymap-set` it into the right `embark-*-map`.

## Storing Org links to files and URLs

When using org-mode one calls `M-x org-store-link` to save the location of the thing at
point, and then insert a link to it somewhere else using `C-c C-l` (`org-insert-link`).

`embark-org` (auto-loaded with embark) binds `org-store-link` on `C-. l` for Org
headings, agenda items and `consult-org-heading` candidates. However I often wanted to
save links to local files or directories, or to an URL.

I defined two actions to call `org-stored-link`, so now I can save these links easily
and insert them in my Org files with `C-c C-l`:

```elisp
(defvar org-stored-links)
(defun my-embark-org-store-file-link (file)
  "Store an Org link to FILE in `org-stored-links'."
  (interactive "fStore Org link to file: ")
  (push (list (concat "file:" (expand-file-name file))
              (file-name-nondirectory file))
        org-stored-links)
  (message "Stored Org link to %s" file))
(defun my-embark-org-store-url-link (url)
  "Store an Org link to URL in `org-stored-links'."
  (interactive "sStore Org link to URL: ")
  (push (list url nil) org-stored-links)
  (message "Stored Org link to %s" url))
(keymap-set embark-file-map "l" #'my-embark-org-store-file-link)
(keymap-set embark-url-map "l" #'my-embark-org-store-url-link)
```

Note that `l` in `embark-file-map` displaces the default `load-file` binding.

## Acting on Magit commits

I use [orgit](https://github.com/magit/orgit) to have links to git commits in my org
files. The usual flow is to open a commit in detail, then call `M-x orgit-store-link` to
save the link to it. With Embark I can avoid opening the commit, for example while
browsing the log.

I define a new target type, `magit-commit`, for the commit at point in any Magit buffer
(log, status, refs, revision), found with the public `magit-commit-at-point`. Then the
actions: `RET` shows the commit, `C-. l` stores an `orgit-rev:` link, and `C-. w` copies
the hash (from `embark-general-map`).

```elisp
;; Registered near the front of `embark-target-finders' so the commit
;; target beats the generic identifier target on hashes (mirrors
;; embark-org's approach).
(defun my-embark-target-magit-commit ()
  "Target the commit at point in a Magit buffer."
  (when (derived-mode-p 'magit-mode)
    (when-let* ((rev (magit-commit-at-point)))
      (if-let* ((bounds (bounds-of-thing-at-point 'git-revision)))
          `(magit-commit ,rev ,(car bounds) . ,(cdr bounds))
        (cons 'magit-commit rev)))))
(defun my-embark-org-store-commit-link (rev)
  "Store an Org link to commit REV via orgit."
  (interactive (list (or (magit-commit-at-point)
                         (magit-read-branch-or-commit
                          "Store Org link to commit"))))
  (unless (require 'orgit nil t)
    (user-error "Storing Org links to commits requires the orgit package"))
  (save-window-excursion
    ;; `magit-show-commit' selects the revision window, so
    ;; `org-store-link' runs in the revision buffer and orgit
    ;; stores an orgit-rev link.
    (magit-show-commit rev)
    (org-store-link nil t)))
(defvar-keymap my-embark-magit-commit-map
  :doc "Keymap for Embark actions on Magit commits."
  :parent embark-general-map
  "RET" #'magit-show-commit
  "l" #'my-embark-org-store-commit-link)
(let ((tail (memq 'embark-target-active-region embark-target-finders)))
  (cl-pushnew 'my-embark-target-magit-commit (cdr tail)))
(add-to-list 'embark-keymap-alist
             '(magit-commit my-embark-magit-commit-map))
```

The [embark-vc](https://github.com/elken/embark-vc) package also
targets commits, but finds them via a margin-hash regexp and is
forge-centric; this target is section-based, so it works anywhere
`magit-commit-at-point` does, and focuses on Org links.

## Git and terminal actions on files and directories

`C-. g` runs `magit-status` for the directory; this also works on project roots in
`project-switch-project`, because Embark turns those candidates into directory
targets.

`C-. T` opens a file's history with
[git-timemachine](https://codeberg.org/pidu/git-timemachine)

`C-. t` opens a terminal in the directory:

```elisp
(defun my-embark-magit-status (dir)
  "Run `magit-status' for the repository containing DIR."
  (interactive "DMagit status: ")
  (magit-status dir))
(defun my-embark-git-timemachine (file)
  "Visit FILE and browse its history with `git-timemachine'."
  (interactive "fFile: ")
  (find-file file)
  (git-timemachine))
(defun my-embark-ghostel (dir)
  "Open a Ghostel terminal in DIR."
  (interactive "DTerminal in directory: ")
  (let ((default-directory (if (file-directory-p dir)
                               (file-name-as-directory dir)
                             (file-name-directory (expand-file-name dir)))))
    (ghostel)))
(keymap-set embark-file-map "g" #'my-embark-magit-status)
(keymap-set embark-file-map "T" #'my-embark-git-timemachine)
(keymap-set embark-file-map "t" #'my-embark-ghostel)
```

Swap `ghostel` for `eshell`, `vterm` or whichever terminal you use.

## LLM actions with gptel

I use a global `C-c a` prefix for AI actions through
[gptel](https://github.com/karthink/gptel): `r` rewrite, `a` add to context, `s` send,
`R` security review. I mimic the same keys in the embark map, plus `C-. a` on a file to
add it to the gptel context, and `C-. a` on a Flymake diagnostic asks the LLM to explain
it:

```elisp
;; Displaces `align' in `embark-region-map' (`align-regexp' stays on "A").
(defvar-keymap my-embark-gptel-map
  :doc "Keymap for Embark actions sending the region to gptel."
  "r" #'gptel-rewrite
  "a" #'gptel-add
  "s" #'gptel-send
  "R" #'my-gptel-review-malicious-code) ; my own review command
(fset 'my-embark-gptel-map my-embark-gptel-map)
(keymap-set embark-region-map "a" 'my-embark-gptel-map)
(keymap-set embark-file-map "a" #'gptel-add-file)

(defun my-embark-gptel-explain-diagnostic ()
  "Ask gptel to explain the Flymake diagnostic at point."
  (interactive)
  (require 'gptel)
  (if-let* ((diag (car (flymake-diagnostics (point)))))
      (let* ((text (format
                    "Explain this diagnostic in %s and suggest a fix.\n\n\
Diagnostic (%s): %s\n\nCode:\n%s"
                    (buffer-name)
                    (flymake-diagnostic-type diag)
                    (flymake-diagnostic-text diag)
                    (buffer-substring-no-properties
                     (flymake-diagnostic-beg diag)
                     (flymake-diagnostic-end diag))))
             (buffer (get-buffer-create "*gptel-diagnostic*"))
             (marker (with-current-buffer buffer
                       (erase-buffer)
                       (org-mode)
                       (point-marker))))
        (pop-to-buffer buffer)
        (gptel-request text
                       :system "You are a concise programming assistant."
                       :stream t
                       :buffer buffer
                       :position marker))
    (user-error "No Flymake diagnostic at point")))
(keymap-set embark-flymake-map "a" #'my-embark-gptel-explain-diagnostic)
```

## Smaller quality-of-life tweaks

Three one-liners: spell-correct with [jinx](https://github.com/minad/jinx) instead of
ispell; open [helpful](https://github.com/Wilfred/helpful) buffers instead of
`describe-*`; and find references with
[elisp-refs](https://github.com/Wilfred/elisp-refs):

```elisp
(keymap-set embark-identifier-map "$" #'jinx-correct)

(keymap-set embark-symbol-map "h" #'helpful-symbol)
(keymap-set embark-variable-map "h" #'helpful-variable)
(keymap-set embark-function-map "h" #'helpful-callable)
(keymap-set embark-command-map "h" #'helpful-command)

(keymap-set embark-symbol-map "R" #'elisp-refs-symbol)
```

## Cheat sheet

| Target | Keys | Action |
|---|---|---|
| File or URL | `C-. l` | Store Org link for `C-c C-l` in org-mode |
| Magit commit | `C-. RET` / `l` / `w` | Show / store orgit link / copy hash |
| Directory | `C-. g` | `magit-status` (also project roots) |
| File | `C-. T` | `git-timemachine` |
| Directory | `C-. t` | Terminal in directory |
| Region | `C-. a r/a/s/R` | gptel rewrite / add / send / review |
| File | `C-. a` | Add file to gptel context |
| Flymake diagnostic | `C-. a` | Explain and fix with gptel |
| Identifier | `C-. $` | `jinx-correct` |
| Symbol | `C-. h` / `C-. R` | helpful / find references |

## Closing

Embark is a truly useful package because it is original in its functionality, it really
adds something new to the Emacs experience. Even if you don't find any of these examples
directly useful to you, may they serve as inspiration to craft your own.
