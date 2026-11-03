Title: Potenciando Embark: acciones personalizadas para Org, Magit y gptel
Date: 2026-11-03
Lang: es
Category: Software
Tags: emacs,howto
Slug: embark-custom-actions

[Embark](https://github.com/oantolin/embark/) es un paquete para Emacs que convierte lo
que está bajo el cursor (un archivo, una URL, una región, un símbolo...) en un
*objetivo* con un menú contextual de acciones, que se activa con `embark-act` (yo lo
tengo asignado a `C-.`). Imagínate como hacer clic con el botón derecho del ratón sobre
un elemento. Resulta muy útil cuando empiezas a hacer algo, por ejemplo, buscar un
archivo para abrirlo, pero prefieres ejecutar una acción diferente sobre él.

En este tutorial presento algunas acciones personalizadas de *embark* que he añadido a
mi configuración de Emacs:

1. Almacenar enlaces Org a archivos, directorios, URL y commits de Magit
2. Abrir Magit y terminales en directorios
3. Enviar cosas a una IA
4. Algunos ajustes para usar *jinx* y *helpful*

Cada sección muestra el código y la combinación de teclas.

[TOC]

## Prerrequisitos

Supongo el uso de
[use-package](https://www.gnu.org/software/emacs/manual/use-package.html) (integrado en
Emacs 29+) para instalar y configurar *embark*:

```elisp
(use-package embark
  :bind (("C-." . embark-act))
  :config [...]
  )
```

Cada fragmento de código que aparece a continuación va dentro del `:config` de ese
bloque. El patrón es siempre el mismo: definir un comando que reciba el destino a través
de su especificación interactiva y, a continuación, asignarlo con `keymap-set` al
`embark-*-map` adecuado.

## Guardar enlaces Org a archivos y URL

Usando [Org Mode](https://orgmode.org/) se ejecuta `M-x org-store-link` para guardar la
ubicación del elemento bajo el cursor, y a continuación se inserta un enlace al mismo en
otro lugar mediante `M-x org-insert-link`.

`embark-org` (que se carga automáticamente con embark) asocia `org-store-link` a `C-. l`
para los encabezados de Org, los elementos de la agenda y los candidatos de
`consult-org-heading`. Sin embargo, a menudo quería guardar enlaces a archivos o
directorios locales, o a una URL.

He definido dos acciones para llamar a `org-stored-link`, así que ahora puedo guardar
estos enlaces fácilmente e insertarlos en mis archivos Org con `C-c C-l`:

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

Nótese que `embark-file-map` ya definía la `l` para ejecutar `load-file`.

## Acciones sobre *commits* de Magit

Utilizo [orgit](https://github.com/magit/orgit) para incluir enlaces a *commits* de Git
en mis archivos Org. El procedimiento habitual implica abrir la vista en detalle de un
commit y, a continuación, ejecutar `M-x orgit-store-link` para guardar el enlace al
mismo. Con Embark puedo evitar tener que abrirlo, puedo ejecutar la acción desde
cualquier otra vista de Magit.

Defino un nuevo tipo de destino, `magit-commit`, que aplica sobre cualquier *commit*
bajo el cursor en cualquier búfer de Magit, mediante la función pública
`magit-commit-at-point`. A continuación defino las acciones: `RET` muestra el *commit*,
`C-. l` guarda un enlace `orgit-rev:` y `C-. w` copia el hash.

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

El paquete [embark-vc](https://github.com/elken/embark-vc) también se centra en los
commits, pero los localiza mediante una expresión regular y está orientado a *Forge*;
este objetivo se basa en secciones, por lo que funciona en cualquier lugar donde lo haga
`magit-commit-at-point`, y se centra en los enlaces Org y los *hashes*.

## Acciones de Git y terminales sobre archivos y directorios

`C-. g` ejecuta `magit-status` sobre un directorio; esto también funciona en las raíces
de los proyectos al usar `M-x project-switch-project`, ya que Embark convierte esos candidatos en
destinos de directorio.

`C-. T` abre el historial de un archivo con
[git-timemachine](https://codeberg.org/pidu/git-timemachine).

`C-. t` abre una terminal en el directorio.

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

Cambia `ghostel` por `eshell`, `vterm` o el terminal que utilices.

## Acciones de LLM con gptel

Utilizo el prefijo global `C-c a` para acciones de IA a través de
[gptel](https://github.com/karthink/gptel): `r` reescribir, `a` añadir al contexto, `s`
enviar, `R` revisión de seguridad. Imito las mismas teclas en el mapa de Embark, además
de `C-. a` sobre un archivo para añadirlo al contexto de gptel, y `C-. a` sobre un
diagnóstico de Flymake para pedirle al LLM que lo explique:

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

## Pequeños ajustes de calidad de vida

Tres pequeños cambios para aprovechar los paquetes que ya uso en otras partes de mi
configuración (y que recomiendo): revisión de ortografía con
[jinx](https://github.com/minad/jinx) en lugar de ispell; abrir la ayuda con
[helpful](https://github.com/Wilfred/helpful) en vez de con `describe-*`; y buscar
referencias con [elisp-refs](https://github.com/Wilfred/elisp-refs):

```elisp
(keymap-set embark-identifier-map "$" #'jinx-correct)

(keymap-set embark-symbol-map "h" #'helpful-symbol)
(keymap-set embark-variable-map "h" #'helpful-variable)
(keymap-set embark-function-map "h" #'helpful-callable)
(keymap-set embark-command-map "h" #'helpful-command)

(keymap-set embark-symbol-map "R" #'elisp-refs-symbol)
```

## Referencia de comandos

| Destino | Tecla | Acción |
|---|---|---|
| Archivo o URL | `C-. l` | Guardar enlace Org para `C-c C-l` en Org-mode |
| Commit de Magit | `C-. RET` / `l` / `w` | Mostrar / guardar enlace Orgit / copiar hash |
| Directorio | `C-. g` | `magit-status` (también raíces de proyectos) |
| Archivo | `C-. T` | `git-timemachine` |
| Directorio | `C-. t` | Terminal en el directorio |
| Región | `C-. a r/a/s/R` | Reescribir / añadir / enviar / revisar con gptel |
| Archivo | `C-. a` | Añadir archivo al contexto de gptel |
| Diagnóstico de Flymake | `C-. a` | Explicar y corregir con gptel |
| Identificador | `C-. $` | `jinx-correct` |
| Símbolo | `C-. h` / `C-. R` | útil / buscar referencias |

## Conclusión

Embark es un paquete realmente útil porque ofrece una funcionalidad original que aporta
algo nuevo a la experiencia con Emacs. Incluso aunque ninguno de estos ejemplos te
resulte directamente útil, espero que te sirvan de inspiración para crear los tuyos
propios.
