Title: Supply-chain hygiene for Emacs: LLM review of package upgrades
Date: 2026-08-08
Lang: en
Category: Software
Tags: emacs,free-software,howto,programming,security
Slug: emacs-straight-ai-review

Emacs has no sandbox. Every package you install runs arbitrary Lisp with your full
privileges: your files, your credentials, your network. This makes me **really scared** of
installing new packages, or upgrading existing ones.

The packages most of us use are not vetted artifacts: MELPA builds from some repository
(usually unsigned) commit, many packages are maintained by a single person, and nobody
audits what lands in a given update. A maintainer's account takeover, or a repository
sold to a new owner, turns `M-x package-upgrade-all` into remote code execution on your
machine. There is even a subtler vector unique to this ecosystem: *recipe
redirection*. A one-line change to a MELPA recipe can silently point an existing package
name at a different repository.

The answer isn't to stop upgrading, but to make upgrades **deliberate**: pin every package
to an exact commit and review the diffs before merging anything.

Manually reviewing diffs is not only cumbersome but needs a high level of expertise in
Emacs Lisp, so my solution is to have an LLM do a first-pass security audit of the
changes before they get to execute.

This post showcases the setup I use, built on
[straight.el](https://github.com/radian-software/straight.el),
[Magit](https://magit.vc/) and [gptel](https://github.com/karthink/gptel).

[TOC]

## The setup at a glance

1. *straight.el*'s own bootstrap script is verified against a pinned SHA-256 checksum
   before it is evaluated.
2. Every package (and every recipe repository) is pinned to a commit in a lockfile under
   version control.
3. Upgrades are fetch-first: `git fetch` to pull new incoming changes, `git merge` and
   actually upgrade only what passes review.
4. A custom *Magit* view displays all incoming fetched-but-unmerged diffs across all
straight repos.
5. A custom *gptel* command reviews the full diff using an LLM.
6. If the changes are clean, have *straight.el* merge the changes and update the
lockfile.

[
![gptel reviewing a straight.el packages upgrade]({static}/images/emacs_straight_ai_review/emacs-straight-gptel-review.png "Click for full screen"){:.align-center}
]({static}/images/emacs_straight_ai_review/emacs-straight-gptel-review.png "Click for full screen"){:target="_blank"}

## Step 1: verify the straight.el bootstrap

[*straight.el* installs
itself](https://github.com/radian-software/straight.el#getting-started) by downloading
and evaluating `install.el` at startup. That's remote code at face value, so my
`early-init.el` pins its SHA-256 and stops on mismatch:

```elisp
;; SHA-256 of straight.el's install.el; update after reviewing changes at
;; https://github.com/radian-software/straight.el/commits/develop/install.el
(defconst my-straight-install-el-sha256
  "e29e07d52d16d4136971f0a822cb6a1a6e1e764a1cb9fe67cccbc7c048aba553")

(defvar bootstrap-version)
(let ((bootstrap-file
       (expand-file-name
        "straight/repos/straight.el/bootstrap.el"
        (or (bound-and-true-p straight-base-dir)
            user-emacs-directory)))
      (bootstrap-version 7))
  (unless (file-exists-p bootstrap-file)
    (with-current-buffer
        (url-retrieve-synchronously
         "https://raw.githubusercontent.com/radian-software/straight.el/develop/install.el"
         'silent 'inhibit-cookies)
      ;; verify bootstrap script against its pinned checksum before eval
      (require 'url-http)
      (when url-http-end-of-headers
        (delete-region (point-min) url-http-end-of-headers)
        (delete-region (point-min)
                       (progn (skip-chars-forward " \t\n") (point))))
      (let ((checksum (secure-hash 'sha256 (current-buffer))))
        (unless (string= checksum my-straight-install-el-sha256)
          (error "straight.el bootstrap checksum mismatch!")))
      (goto-char (point-max))
      (eval-print-last-sexp)))
  (load bootstrap-file nil 'nomessage))
```

## Step 2: pin everything

*straight.el* installs packages as git clones, which makes review natural. The lockfile pins
them all:

- `M-x straight-freeze-versions` writes every package's exact commit to
  `straight/versions/default.el` (packages *and* recipe repositories, MELPA
  included).
- Commit the lockfile. Reviewing `git diff straight/versions/default.el` after an
  upgrade tells you exactly what moved.
- `M-x straight-thaw-versions` restores those revisions if you ever need to roll back.

## Step 3: review diffs before merging

The key to a safe upgrade is that fetching and merging are separate steps.  `M-x
straight-fetch-all` downloads new upstream commits without changing any checkout. Then I
review what would change, per repo, before `M-x straight-merge-all` applies anything.

I then use a custom Magit function to display a single combined diff view of every repo
with incoming upstream commits:

```elisp
;; https://magit.vc/
(use-package magit
  :bind (("C-c v U" . my-straight-incoming-diffs))
  :preface
  (defun my-straight-repo-behind-p (repo)
    "Return non-nil if REPO's current branch is behind its upstream."
    (let* ((default-directory repo)
           (lines (magit-git-lines "status" "--porcelain=2" "--branch")))
      (seq-some (lambda (line)
                  (string-match-p "^# branch\\.ab [+][0-9]+ -[1-9]" line))
                lines)))
  (defun my-straight-incoming-diffs ()
    "Concatenate the full patches of all incoming upstream changes.
Create a `diff-mode' buffer listing, for every straight.el checkout
that is behind its upstream, the incoming commits with author and
date, followed by the net patch that merging would apply.  The
buffer is left writable so hunks can be trimmed before feeding it
to a reviewing agent."
    (interactive)
    (let* ((repos (magit-list-repos-1
                   (expand-file-name "straight/repos" user-emacs-directory)
                   1))
           (behind (seq-filter #'my-straight-repo-behind-p repos)))
      (if (null behind)
          (message "No incoming upstream changes")
        (with-current-buffer (get-buffer-create "*straight-incoming-diffs*")
          (erase-buffer)
          (dolist (repo behind)
            (let* ((default-directory repo)
                   (branch (magit-git-string "rev-parse" "--abbrev-ref"
                                             "HEAD"))
                   (upstream (magit-git-string "rev-parse" "--abbrev-ref"
                                               "@{upstream}"))
                   (commits (magit-git-lines
                             "log" "--format=%h  %ad  %an <%ae>  %s"
                             "--date=short" "HEAD..@{upstream}"))
                   (n (length commits)))
              (insert (make-string 80 ?=) "\n")
              (insert
               (format "%s  (%s <- %s, %d commit%s)\n"
                       (file-name-nondirectory (directory-file-name repo))
                       (or branch "HEAD") (or upstream "?")
                       n (if (= n 1) "" "s")))
              (insert (make-string 80 ?-) "\n")
              (insert (string-join commits "\n") "\n\n")
              (magit-git-insert "diff" "HEAD...@{upstream}")
              (insert "\n")))
          (diff-mode)
          (goto-char (point-min))
          (pop-to-buffer (current-buffer))))))
  (defun my-straight-incoming-diffs-after-fetch (&rest _)
    "Show incoming full diffs after an interactive `straight-fetch-all'."
    (when (eq this-command 'straight-fetch-all)
      (condition-case err
          (my-straight-incoming-diffs)
        (error (message "my-straight-incoming-diffs failed: %S"
                        (error-message-string err))))))
  :init
  ;; automatically show the incoming diffs after fetching all remotes
  (with-eval-after-load 'straight
    (advice-add 'straight-fetch-all
                :after #'my-straight-incoming-diffs-after-fetch)))
```

## Step 4: LLM-powered review of the diff

Unless the diff is really straightforward I pass it to an LLM for a code review.  I use
gptel with KWallet for secret storing and Venice ([referral
link](https://venice.ai/chat?ref=XPrCO2)) for AI inference:

```elisp
;; API key from KWallet via the freedesktop Secret Service API; or put
;;   machine api.venice.ai login apikey password <your-key>
;; in ~/.authinfo.gpg and drop the secrets: entry.
(setq auth-sources '("secrets:kdewallet" "~/.authinfo.gpg" "~/.authinfo"))

(use-package gptel
  :bind (("C-c a R" . my-gptel-review-malicious-code))
  :preface
  (defvar my-gptel-review-system-prompt
    "You are a meticulous security reviewer auditing third-party code
before it is merged or used. The user will show you one or more git
diffs, each preceded by the list of incoming commits with author and
date.

Scan for anything that could act maliciously once merged or called:
- backdoors, remote code execution, persistence mechanisms
- credential, token, key or data exfiltration (also covert channels)
- unexpected network activity, downloads or connections to new hosts
- obfuscation designed to hide behavior (heavy encoding, dead stores)
- tampering with build, installation or packaging scripts
- anomalous commit authorship: new maintainer, changed email address,
  commits by someone unrelated to the project

For every finding, state: severity (high/medium/low), the file and
hunk, and a one-paragraph rationale.  Close with an overall verdict:
whether the changes look safe to merge.  If nothing is suspicious,
say so plainly and briefly; do not invent findings."
    "System prompt for `my-gptel-review-malicious-code'.")
  (defun my-gptel-review-malicious-code ()
    "Review the region, or the whole buffer, for malicious code.
Send the text to the LLM with a security-audit system prompt and
show the response in the *gptel-review* buffer."
    (interactive)
    (require 'gptel)
    (let* ((text (buffer-substring-no-properties
                  (if (use-region-p) (region-beginning) (point-min))
                  (if (use-region-p) (region-end) (point-max))))
           (buffer (get-buffer-create "*gptel-review*"))
           (marker (with-current-buffer buffer
                     (erase-buffer)
                     (org-mode)
                     (goto-char (point-min))
                     (point-marker))))
      (pop-to-buffer buffer)
      (gptel-request
       (format
        "Review the following content from %s for malicious code or \
exploits.\n\n%s"
        (buffer-name) text)
       :system my-gptel-review-system-prompt
       :stream t
       :buffer buffer
       :position marker)))
  :config
  (setq gptel-backend
        (gptel-make-openai "Venice"
          :host "api.venice.ai"
          :endpoint "/api/v1/chat/completions"
          :key #'gptel-api-key   ; auth-source, see above
          :stream t
          :models '(kimi-k3
                    claude-opus-5
                    openai-gpt-56-sol
                    grok-4-5
                    zai-org-glm-5-2
                    deepseek-v4-flash-0731))
        gptel-model 'deepseek-v4-flash-0731))
```

Use `C-c a R` to review either a whole buffer or the selected region. The audit streams
into a `*gptel-review*` Org buffer: findings with severity, file and hunk, rationale,
and a final verdict.

## The upgrade workflow

1. `M-x straight-fetch-all`: fetches remotes, changes nothing; the review buffer pops up
   on its own.
2. Eyeball the diff.
3. `C-c a R` on the whole buffer, or on a selected region.
4. Wait for the AI review.
5. `M-x straight-merge-all` when satisfied.
6. Restart Emacs, verify everything works (*straight.el* would have built the new packages).
7. `M-x straight-freeze-versions` and commit the lockfile.

## Caveats and final thoughts

- **The LLM audit is a second pair of eyes, not a guarantee.** Models miss
  things, and a clever adversary writes code that reads as benign. For critical
  packages, still read the diff yourself. Treat the audit as triage: a "high"
  finding means look closer, not that the model is right.
- **Diffs leave your machine.** Venice advertises zero data retention, but if
  your threat model doesn't allow it, point gptel at a local llama.cpp server
  instead. Code is the same, just a different gptel provider.

I know this setup won't be perfect, but it gives me much more peace of mind when
installing or upgrading packages, because Emacs is the center piece of my computer setup
and I need to trust it fully

Do you have any ideas on blind spots, shortcomings or a better setup? Drop a comment below!
