Title: Añadir nuevos git trailers a Magit
Date: 2026-08-12
Lang: es
Category: Software
Tags: ai,emacs,free-software,howto,programming
Slug: emacs-custom-magit-trailers

Los *trailers* de Git no son más que líneas de texto al final de un *commit* que
registran algunos metadatos. Algunos de los más comunes son `Co-Authored-By`
(*co-escrito con*), `Reported-By` (*reportado por*), `Reviewed-By` (*revisado por*) o
`Signed-Off-By` (*aprobado por*).

Magit tiene una forma cómoda de añadir *trailers*: basta con pulsar `C-c TAB` o `C-c
C-i` en la vista de *commit*. Magit mostrará entonces un menú transient con algunas
opciones:

![Menú de inserción de trailer de Magit]({static}/images/emacs_magit_custom_trailer/emacs-magit-insert-trailer-menu.png)

Hoy en día se está volviendo habitual usar el [*trailer*
`Assisted-by:`](https://github.com/microsoft/vscode/issues/313962) para acreditar a los
agentes de IA de programación, y yo quería empezar a usarlo, ya que ahora hago la mayor
parte de mi código con ayuda de IA. Magit no soporta este *trailer* (¡por ahora!), pero
hice que mi IA averiguara cómo añadirlo.

En esta pequeña guía os mostraré cómo añadir un nuevo tipo de *trailer* a Magit, para
que quede a solo un `C-c TAB` de distancia. Usaré el ejemplo de `Assisted-by`, pero
podéis adaptarlo a otros si os hiciese falta. Al usarlo pide un valor (texto libre,
p. ej. `Kimi K3` o `venice/zai-org-glm-5-2`) y lo añade al buffer de *commit* como
`Assisted-by: <value>`, después de cualquier otro *trailer* existente.

Recuerda los valores introducidos anteriormente, que se ofrecerán como opciones de
completado. Como bonus también mostraré cómo configurar el paquete `savehist` incluido
en Emacs para conservar ese historial entre sesiones.

## Configuración de Magit

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

Cómo funciona:

- `transient-append-suffix` añade el comando a `git-commit-insert-trailer` (`C-c TAB`),
  justo después de la entrada integrada "Co-developed", de modo que aparece como `A` en
  el menú de *trailers*.
- El valor se pide con `completing-read` en el minibúfer, así que podéis usar vuestro
  sistema de completado configurado (yo uso [vertico](https://github.com/minad/vertico))
  para elegir entre los candidatos, o escribir texto libre.
- La inserción pasa por el mismo helper interno que Magit usa para `Signed-off-by`, de
  modo que el *trailer* se coloca después de los *trailers* existentes y antes de la
  sección de comentarios/diff, independientemente de la disposición del buffer.
- Añadir `"Assisted-by"` a `git-commit-trailers` hace que el token se resalte con
  font-lock como los integrados. Esto es necesario porque los valores son texto libre;
  Magit solo resalta tokens arbitrarios cuando tienen la forma `Name <email>`.
- Una nota para quienes usen versiones antiguas de Magit: el menú de *trailers* solía
  llamarse `git-commit-insert-pseudo-header`; ahora es un alias obsoleto de
  `git-commit-insert-trailer`.

## Bonus: recordando los valores entre sesiones con savehist

Emacs olvida el historial de completado cuando termina la sesión, lo cuál es un fastidio
porque normalmente estaremos introduciendo los mismos valores una y otra vez. Activando
`savehist-mode`, las variables de historial del minibúfer se guardan automáticamente una
vez usadas, así que a menudo *no hace falta nada más que tener el modo activado*. Si
prefieres ser explícito (o si solo guardas una lista blanca estableciendo
`savehist-save-minibuffer-history` a `nil`), registradla como variable adicional:

```elisp
(use-package savehist
  :config
  (setq savehist-additional-variables
        '(my-git-commit-assisted-history))
  (savehist-mode +1))
```

El orden importa: `savehist-mode` restaura las variables una sola vez al activarse, así que si lo ponéis antes de establecer `savehist-additional-variables`, veréis que las nuevas variables (`my-git-commit-assisted-history` en mi caso) se guardan en el archivo de `savehist`, pero no se restauran cuando Emacs arranca de nuevo. Pregúntame cómo lo sé.

## Reflexiones finales

No me gusta tener que usar una variable privada como `git-commit--insert-trailer`, es
algo que podría romperse en cualquier momento. En este caso me parece aceptable porque
es un uso muy localizado y en una funcionalidad no crítica que no me importaría que se
rompiera. Si ocurriese procuraré actualizar este artículo.

En cuanto a `Assisted-by`, planeo usarlo mucho; quiero ser honesto sobre mi uso de IA.

¿Usas `Assisted-by` u otros *trailers* en tus *commit*?
