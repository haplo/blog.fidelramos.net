Title: Higiene de la cadena de suministro en Emacs: revisando actualizaciones mediante IA
Date: 2026-08-08
Lang: es
Category: Software
Tags: emacs,howto,programming,seguridad,software-libre
Slug: emacs-straight-ai-review

Emacs no tiene *sandbox*. Cada paquete que instalas ejecuta código Lisp arbitrario con todos tus privilegios: acceso a tus archivos, credenciales y red. Esto hace que me dé **mucho miedo** instalar paquetes nuevos o actualizar los existentes.

Los paquetes que usamos la mayoría de usuarios de Emacs no son verificados: MELPA los
compila a partir de algún commit de un repositorio (normalmente sin firma
criptográfica), muchos paquetes están mantenidos por una sola persona y nadie audita lo
que incluye cada actualización. Si secuestran la cuenta de un mantenedor o este vende el
repositorio a un nuevo propietario, `M-x package-upgrade-all` se convierte en una vía
directa para ejecutar código de forma remota en tu máquina. Incluso existe un vector más
sutil y propio de este ecosistema: la *redirección de recetas*. Un cambio de una sola
línea en una receta de MELPA puede hacer que el nombre de un paquete existente apunte
silenciosamente a otro repositorio.

La solución no es dejar de actualizar, sino hacerlo de forma **deliberada**: fijar cada
paquete a un commit exacto y revisar los diffs antes de fusionar nada.

Revisar los *diffs* a mano no solo es engorroso, sino que exige un alto nivel de
conocimientos de Emacs Lisp. Mi solución consiste en recurrir a un LLM para que realice
una primera auditoría de seguridad de los cambios antes de que lleguen a ejecutarse.

En este artículo muestro la configuración que utilizo, basada en
[straight.el](https://github.com/radian-software/straight.el),
[Magit](https://magit.vc/) y [gptel](https://github.com/karthink/gptel).

[TOC]

## Resumen de la configuración

1. El script de arranque de *straight.el* se verifica mediante una suma SHA-256
precalculada antes de evaluarlo.
2. Cada paquete (y cada repositorio de recetas) queda fijado a un *commit* y registrado
en un archivo (*lockfile*) sometido a control de versiones.
3. Primero se descargan las actualizaciones: `git fetch` obtiene los cambios entrantes,
mientras que `git merge` y la actualización propiamente dicha solo se ejecutan cuando
los cambios superan la revisión.
4. Una vista personalizada de *Magit* muestra los diffs de todos los cambios descargados
pero aún no fusionados en todos los repositorios de straight.
5. Un comando personalizado de *gptel* revisa el diff completo mediante un LLM.
6. Si los cambios son seguros, *straight.el* los fusiona y actualiza el archivo de
versiones.

[
![gptel revisando una actualización de paquetes de straight.el]({static}/images/emacs_straight_ai_review/emacs-straight-gptel-review.png "Haz clic para ver a pantalla completa"){:.align-center}
]({static}/images/emacs_straight_ai_review/emacs-straight-gptel-review.png "Haz clic para ver a pantalla completa"){:target="_blank"}

## Paso 1: verificar la instalación de straight.el

[*straight.el* se
instala](https://github.com/radian-software/straight.el#getting-started) descargando y
evaluando `install.el` durante el arranque. Esta es una puerta abierta a ejecución de
código remoto, así que mi `early-init.el` fija su SHA-256 a un valor conocido y detiene
el proceso si no coincide:

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

## Paso 2: fijar las versiones conocidas

*straight.el* instala los paquetes clonando sus repositorios *Git*, lo que facilita su
revisión. El archivo de versiones (*lockfile*) registra el estado de todos:

- `M-x straight-freeze-versions` escribe el commit exacto de cada paquete en
  `straight/versions/default.el`, tanto de los paquetes como de los los repositorios de
  recetas, MELPA entre ellos.
- Añade el archivo de versiones al repositorio. Revisar `git diff
  straight/versions/default.el` después de una actualización te permite ver exactamente
  qué ha cambiado.
- `M-x straight-thaw-versions` restaura esas revisiones si alguna vez necesitas volver
  atrás.

## Paso 3: revisar los diffs antes de fusionar

La clave para actualizar de forma segura es separar la descarga de los cambios de su fusión. `M-x straight-fetch-all` descarga los nuevos commits del repositorio remoto sin modificar ningún checkout. Después reviso, repositorio por repositorio, lo que cambiaría antes de que `M-x straight-merge-all` aplique nada.

A continuación, uso una función personalizada de Magit que muestra en una única vista combinada el diff de todos los repositorios que tienen commits entrantes en el upstream:

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

## Paso 4: revisión del diff mediante un LLM

Salvo que el diff sea muy sencillo, se lo paso a un LLM para que revise el código. Utilizo gptel, KWallet para guardar los secretos y Venice ([enlace de
referido](https://venice.ai/chat?ref=XPrCO2)) para la inferencia de IA:

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

Utiliza `C-c a R` para revisar el búfer completo o la región seleccionada. La auditoría se muestra progresivamente en un búfer de Org llamado `*gptel-review*`: cada hallazgo incluye la gravedad, el archivo y el hunk, una justificación y un veredicto final.

## Flujo de trabajo para las actualizaciones

1. Descargo los nuevos cambios a todos los paquetes con `M-x straight-fetch-all`.
2. Echo un vistazo a los cambios.
3. Ejecuto `C-c a R` sobre el búfer completo con los *diff*.
4. Espero a que termine la revisión de la IA.
5. Ejecuto `M-x straight-merge-all` cuando estoy conforme.
6. Reinicio Emacs y compruebo que todo funciona (*straight.el* habrá reconstruido los paquetes).
7. Ejecuto `M-x straight-freeze-versions` y registro los cambios al archivo de versiones en mi repositorio *Git*.

## Limitaciones y reflexiones finales

- **La auditoría por IA es un segundo par de ojos, no una garantía.** Las IA cometen
    errores, pueden pasar cosas por alto, y un adversario hábil puede escribir código
    que parezca inofensivo. En el caso de los paquetes críticos, sigue siendo buena idea
    leer el *diff* personalmente. Considera la auditoría como una herramienta de triaje:
    un hallazgo de gravedad «alta» significa que debes examinarlo más de cerca, no que
    el modelo tenga razón.
- **Los diffs salen de tu máquina.** Venice afirma aplicar una política de retención
    cero de datos, pero, si tu modelo de privacidad no lo permite, puedes configurar
    *gptel* para que utilice un servidor local. El código es el mismo; solo cambia el
    proveedor de *gptel*.

Sé que esta configuración no es perfecta, pero me da mucha más tranquilidad al instalar
o actualizar paquetes. Emacs es la pieza central de mi entorno informático y necesito
poder confiar plenamente en él.

¿Se te ocurre algún punto ciego, limitación o posible mejora? ¡Déjame un comentario!
