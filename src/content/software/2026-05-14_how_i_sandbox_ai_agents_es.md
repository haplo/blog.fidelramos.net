Title: Cómo aislo mis agentes IA
Date: 2026-05-14
Lang: es
Category: Software
Tags: ai,firejail,linux,security
Slug: how-i-sandbox-ai-agents

He estado usando [Opencode](https://opencode.ai/) como mi agente de programación por IA.
No tengo una larga lista de razones por las que lo elegí entre las muchas alternativas existentes, algo impropio de mí.
Solo quería empezar con un sistema de agentes que cumpliera mis requisitos principales:

- Debe ser completamente de código abierto.
- Popular, lo que significa que probablemente durará. No quiero perder el tiempo aprendiendo a usar un programa solo para que desaparezca en unos meses.
- Extensible y configurable.
- Que soporte muchos proveedores de IA, incluida mi elección actual, Venice.ai (¡aquí hay un [enlace con referencia](https://venice.ai/chat?ref=XPrCO2) para los interesados!)

Una de las cosas que no me gusta de Opencode es que no usa sandboxing, y eso no es un descuido sino una decisión consciente de diseño.
Sí, Opencode pregunta antes de que un agente intente acceder a un archivo fuera del proyecto, pero el software de Opencode en sí no está restringido y tiene acceso al sistema completo.

Mi solución es simple: envuelvo Opencode con [Firejail](https://github.com/netblue30/firejail), que ya estoy usando para la mayoría de los otros programas en mis ordenadores.
De esta manera, restrinjo Opencode para que no tenga acceso a lo que no debe (¡como mis claves SSH!) a nivel del *kernel*.

[
![Opencode aislado no tiene acecso a mis claves SSH]({static}/images/how_i_sandbox_my_ai_agents/opencode_ssh_keys.webp "Cliquea para pantalla completa"){: .align-center}
]({static}/images/how_i_sandbox_my_ai_agents/opencode_ssh_keys.webp "Cliquea para pantalla completa")

## Configuración de Firejail

Firejail [ya integró un perfil de Opencode](https://github.com/netblue30/firejail/pull/7135) pero no está en una versión estable en el momento de escribir estas palabras.
Por ahora, uso mi propio perfil de firejail en *~/.config/firejail/opencode.profile*:

```
# Firejail profile for opencode
# Description: An open source AI coding agent.
# This file is overwritten after every install/update
quiet
# Persistent local customizations
include opencode.local
# Persistent global definitions
include globals.local

# allow executables in HOME, see disable-exec.inc
ignore noexec ${HOME}

# blacklisted by disable-programs.inc
noblacklist ${HOME}/.cache/opencode
noblacklist ${HOME}/.config/opencode
noblacklist ${HOME}/.local/share/opencode

# Allows files commonly used by IDEs
include allow-common-devel.inc

# Disable Wayland
blacklist ${RUNUSER}/wayland-*
# Disable RUNUSER (cli only; supersedes Disable Wayland)
blacklist ${RUNUSER}
# Remove the next blacklist if your system has no /usr/libexec dir,
# otherwise try to add it.
blacklist /usr/libexec

# disable-*.inc includes
include disable-proc.inc
include disable-write-mnt.inc
include disable-x11.inc
include disable-xdg.inc

mkdir ${HOME}/.cache/opencode
whitelist ${HOME}/.cache/opencode
mkdir ${HOME}/.config/opencode
whitelist ${HOME}/.config/opencode
mkdir ${HOME}/.local/share/opencode
whitelist ${HOME}/.local/share/opencode

# Commands that reduce access to resources.
caps.drop all
##caps.keep CAPS
##hostname NAME
# CLI only
ipc-namespace
machine-id
no3d
nodvd
nogroups
noinput
nonewprivs
noprinters
noroot
nosound
notv
nou2f
novideo
protocol unix,inet,inet6
seccomp
#tracelog

disable-mnt
private-cache
private-dev
private-etc alternatives,ca-certificates,crypto-policies,dconf,fonts,ld.so.cache,ld.so.preload,machine-id,pki,resolv.conf,ssl
private-tmp

dbus-user none
dbus-system none

env NO_BROWSER=true
restrict-namespaces
```

Este perfil utiliza un modelo de lista blanca (*whitelist*), por lo que Opencode solo tendrá acceso a esos directorios específicos y ni siquiera verá el resto.
Eso significa que al invocar Opencode necesito incluir en la lista blanca el directorio del proyecto en el que quiero que trabaje.
Lo hago así:

```bash
~/Code/someproject$ firejail --profile=opencode --whitelist=(pwd) /usr/bin/opencode
```

Como escribir todo eso se volvería rápidamente aburrido, tengo `opencode` configurado como un `abbr`, por lo que se expandirá automáticamente a lo anterior.

Un `abbr` es una [construcción de fish shell](https://fishshell.com/docs/current/cmds/abbr.html) que funciona como un alias, pero es editable al expandirse.
Esto es muy útil en caso de que quiera editar el comando, como en este caso podría necesitar incluir en la lista blanca alguna ruta adicional.

## Resultados y próximos pasos

He estado usando esta configuración durante un mes y ha sido sólida una vez que ajusté la configuración del perfil de Firejail.
Ahora puedo usar agentes con la seguridad de que no exfiltrarán datos privados, o que un error en Opencode podría afectar a mis archivos o mi sistema.

A continuación, quiero extender esta configuración para poder usar Opencode con un modelo LLM local a través de llama.cpp, pero sin acceso a Internet.
Quiero que esto funcione en proyectos altamente personales donde no confiaría ni siquiera en los modelos privados de Venice.ai, como la configuración de [mi homelab]({file}2023-12-29_homelab.md).

También he desarrollado mis propios agentes de investigación en Opencode, para gestionar proyectos de investigación de larga duración como un conjunto de archivos Markdown que sirven como memoria.
Utiliza una extensión del perfil de Firejail, además de configuración adicional de Opencode y prompts para el agente investigador y los subagentes buscadores.
Sigo refinándolo, pero ya está demostrando ser útil, así que probablemente terminaré escribiendo una publicación al respecto.
