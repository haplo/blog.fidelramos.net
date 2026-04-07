Title: Pre-estableciendo conexiones maestras de SSH para Ansible, o cómo usar OnlyKey con  Ansible sin morir en el intento
Date: 2026-04-07
Lang: es
Category: Software
Tags: ansible,automation,howto,linux,security
Slug: ansible-ssh-master-connections

Uso una [OnlyKey](https://onlykey.io/) como dispositivo de seguridad de hardware para varios propósitos:

- Las contraseñas comunes se escriben automáticamente con solo pulsar un botón.
- Como segundo factor en mi gestor de contraseñas (KeepassXC), usando HMAC aplicado a la contraseña.
- Conexiones SSH.
- Cifrado y firma GPG.

![OnlyKey]({static}/images/ansible_and_onlykey/onlykey.webp){: .align-center}

Las conexiones SSH se manejan a través del [onlykey-agent](https://docs.onlykey.io/onlykey-agent.html), y funciona bastante bien.
Sin embargo, con Ansible se convierte en una pesadilla, ya que pide docenas y docenas de pulsaciones de teclas:

[
![Parte de una sesión de Ansible con onlykey-agent]({static}/images/ansible_and_onlykey/ansible_onlykey.webp "Haz clic para pantalla completa"){: .align-center}
]({static}/images/ansible_and_onlykey/ansible_onlykey.webp "Haz clic para pantalla completa")

Este dolor de cabeza me estaba haciendo usar Ansible cada vez menos para mis automatizaciones, así que decidí encontrar una solución.
El objetivo es necesitar solo **una pulsación de OnlyKey por cada servidor**, con un comportamiento bien definido y razonablemente seguro.

Me alegra decir que he logrado una solución razonable, que documento aquí con la esperanza de que sea útil para otras personas.
Podría ayudar no solo a los usuarios de OnlyKey, sino a cualquiera con una **configuración de SSH que requiera intervención manual** en el momento de la conexión, y para la que por alguna razón la reutilización de conexiones SSH de Ansible no esté funcionando.

---

## El problema

Ansible a menudo abre más de una sesión SSH por servidor durante su ejecución.
Incluso con una buena configuración, es posible que sigas viendo conexiones repetidas para tareas, recopilación de información (*fact gathering*), escalada de privilegios y otras operaciones.

Cuando se usan claves SSH normales, todo esto es casi invisible.
Se pierde rendimiento por las conexiones extras a la red y el cifrado adicional, pero funcionaría.

Con `onlykey-agent`, cada nueva autenticación SSH requiere confirmación física.
Eso hace que todas las conexiones repetidas se convierte rápidamente en un auténtico coñazo.

## Lo que observé

La solución a alto nivel es obvia: **reutilizar las conexiones SSH**.

Y la cuestión es que [Ansible soporta la reutilización de conexiones](https://www.lisenet.com/2022/speed-up-ansible-ssh-with-multiplexing/) mediante la multiplexación de conexiones de OpenSSH.

De forma resumida, OpenSSH puede establecer una conexión como maestra, dejar un *socket* abierto y hacer que las nuevas conexiones al mismo servidor/usuario/puerto lo reutilicen automáticamente.

Sin embargo, cuando intenté configurarlo con Ansible no funcionó, seguía recibiendo las mismas peticiones en la OnlyKey.

Cuando miraba el directorio de los *sockets* veía cómo se creaban, sólo para desaparecer momentos después.

Entonces probé la multiplexación SSH **fuera de Ansible**, y funcionó.

Configuré `ControlMaster` en `~/.ssh/config`, y una vez que me conecté a un servidor con `onlykey-agent` pude abrir una nueva conexión **sin otra petición de la OnlyKey**.

Sin embargo, cuando cerraba la conexión, el socket desaparecía.

Supongo que Ansible está cerrando las conexiones por alguna razón, pero no he descubierto exactamente por qué ni cómo.

---

## La solución

Aprovechando que las conexiones abiertas mantenían el socket abierto, planteé una solución que funcionase de forma consistente:

1. Configurar la multiplexación SSH normalmente.
2. Configurar Ansible para que use los mismos *sockets*.
3. Ejecutar Ansible dentro de un *script* que:
    1. Lea la lista de servidores del inventario de Ansible.
    2. Establezca una conexión maestra de SSH para cada servidor.
    3. Mantenga vivo cada maestro con un `sleep` remoto.
    4. Ejecute `ansible-playbook` con todos los argumentos originales sin cambios.
    5. Termine las conexiones maestras al completar.

## Configuración de SSH

Primero, asegúrate de que tu configuración de SSH habilite la multiplexación y use un *control path* estable.

Añade esto a `~/.ssh/config`:

```sshconfig
Host *
    ControlMaster auto
    ControlPersist 10m
    ControlPath ~/.ssh/sockets/%h-%r-%p
```

Luego crea el directorio para los sockets:

```bash
mkdir -p ~/.ssh/sockets
chmod 0700 ~/.ssh/sockets
```

También me gusta configurar usuarios y puertos en la configuración de SSH, por ejemplo:

```sshconfig
Host blog.fidelramos.net
    User fidel
    Port 22022
```

## Configuración de Ansible

Usa un `ansible.cfg` como este:

```ini
[defaults]
transport = ssh

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ServerAliveInterval=30 -o ServerAliveCountMax=3
control_path_dir = ~/.ssh/sockets
control_path = %(directory)s/%%h-%%r-%%p
pipelining = True
```

- `transport = ssh` fuerza el uso de OpenSSH en lugar de Paramiko, que no permite multiplexación SSH.
  Este debería ser el comportamiento predeterminado en las versiones recientes de Ansible.

- `control_path_dir` y `control_path` hacen que Ansible use el mismo patrón de nomenclatura de sockets que SSH, para que reutilice los que el *script* ha establecido previamente.

- `pipelining = True` reduce parte de la sobrecarga de SSH y la rotación de archivos temporales remotos. Esta es una buena idea incluso sin multiplexación para reducir el número de conexiones y acelerar la ejecución de Ansible.

## El script

Aquí está el *script* completo.

Intencionadamente **no** intenta gestionar por sí mismo los nombres de usuario o puertos por servidor.
Esos son aplicados por la configuración de SSH, y Ansible también los reutiliza.

El *script* pasa todos los argumentos a `ansible-playbook` exactamente como se proporcionan.
Mira los ejemplos de uso más abajo.

También [publiqué el *script* como un Gist](https://gist.github.com/haplo/5a6a1194b6f84ec3dad2429d1b3af58b).

### `ansible-ssh-masters.sh`

```bash
#!/usr/bin/env bash
# ansible-ssh-masters.sh
#
# Establish one SSH master connection per host, keep it alive with a
# remote sleep, run ansible-playbook with all original arguments, then
# clean up only the masters this script started.
#
# Useful when SSH authentication has a per-connection human cost:
# hardware security keys, passphrase prompts, FIDO2/U2F, etc.
#
# Usage (timeout in seconds):
#   ANSIBLE_SSH_MASTERS_TIMEOUT=3600 ./ansible-ssh-masters.sh playbook.yml [args...]

set -euo pipefail

TIMEOUT_SECONDS="${ANSIBLE_SSH_MASTERS_TIMEOUT:-3600}"
SOCKET_DIR="${HOME}/.ssh/sockets"

PIDS=()
STARTED_HOSTS=()
ARGS=("$@")
INVENTORY="inventory"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[+]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[-]${NC} $*" >&2; }

parse_inventory_arg() {
    local i
    for ((i=0; i<${#ARGS[@]}; i++)); do
        case "${ARGS[$i]}" in
            -i|--inventory)
                if (( i + 1 >= ${#ARGS[@]} )); then
                    err "Missing value after ${ARGS[$i]}"
                    exit 1
                fi
                INVENTORY="${ARGS[$((i + 1))]}"
                ;;
            --inventory=*)
                INVENTORY="${ARGS[$i]#--inventory=}"
                ;;
        esac
    done
}

cleanup() {
    echo
    log "Closing master connections..."

    local i pid host

    for i in "${!PIDS[@]}"; do
        pid="${PIDS[$i]}"
        host="${STARTED_HOSTS[$i]}"

        if kill -0 "$pid" 2>/dev/null; then
            if kill "$pid" 2>/dev/null; then
                wait "$pid" 2>/dev/null || true
                log "Closed master for ${host} (pid ${pid})"
            else
                err "Failed to kill master for ${host} (pid ${pid})"
            fi
        else
            warn "Master for ${host} was already gone (pid ${pid})"
        fi
    done

    log "Done."
}

trap cleanup EXIT INT TERM

parse_inventory_arg

mkdir -p "$SOCKET_DIR"
chmod 0700 "$SOCKET_DIR"

# Remove stale sockets (no process behind them)
find "$SOCKET_DIR" -maxdepth 1 -type s ! -exec fuser -s {} \; -delete 2>/dev/null || true

if ! ansible-inventory -i "$INVENTORY" --graph >/dev/null 2>&1; then
    err "Inventory could not be parsed: $INVENTORY"
    exit 1
fi

mapfile -t HOSTS < <(
    ansible-inventory -i "$INVENTORY" --graph |
    awk '
        /@/ { next }
        {
            line = $0
            gsub(/^[[:space:]|]+/, "", line)
            sub(/^--/, "", line)
            if (line != "") {
                print line
            }
        }
    ' |
    sort -u
)

if (( ${#HOSTS[@]} == 0 )); then
    err "No hosts found in inventory: $INVENTORY"
    exit 1
fi

log "Found ${#HOSTS[@]} hosts in inventory: $INVENTORY"
log "Per-host connection lifetime: ${TIMEOUT_SECONDS} seconds"
log "Establishing master connections (authentication may be required)..."
echo

count=0
for host in "${HOSTS[@]}"; do
    ((count+=1))

    if ssh -O check -o "ControlPath=${SOCKET_DIR}/%h-%r-%p" "$host" >/dev/null 2>&1; then
        log "[$count/${#HOSTS[@]}] ${host}: reusing existing master"
        continue
    fi

    warn "[$count/${#HOSTS[@]}] ${host}: connecting..."

    ssh \
        -o ControlMaster=yes \
        -o "ControlPath=${SOCKET_DIR}/%h-%r-%p" \
        -o ServerAliveInterval=30 \
        -o ServerAliveCountMax=3 \
        -o ForwardAgent=no \
        -o ForwardX11=no \
        -o ClearAllForwardings=yes \
        "$host" "sleep ${TIMEOUT_SECONDS}" &

    pid=$!

    for _ in $(seq 1 15); do
        if ssh -O check -o "ControlPath=${SOCKET_DIR}/%h-%r-%p" "$host" >/dev/null 2>&1; then
            break
        fi
        sleep 1
    done

    if ssh -O check -o "ControlPath=${SOCKET_DIR}/%h-%r-%p" "$host" >/dev/null 2>&1; then
        log "[$count/${#HOSTS[@]}] ${host}: master established (pid ${pid})"
        PIDS+=("$pid")
        STARTED_HOSTS+=("$host")
    else
        err "[$count/${#HOSTS[@]}] ${host}: failed to establish master"
        if kill -0 "$pid" 2>/dev/null; then
            if kill "$pid" 2>/dev/null; then
                wait "$pid" 2>/dev/null || true
            else
                err "[$count/${#HOSTS[@]}] ${host}: failed to stop failed SSH process (pid ${pid})"
            fi
        fi
    fi
    echo
done

echo
log "Running: ansible-playbook $*"

set +e
ansible-playbook "$@"
ANSIBLE_EXIT=$?
set -e

exit "$ANSIBLE_EXIT"
```

Make it executable:

```bash
chmod +x ansible-ssh-masters.sh
```

### Captura de pantalla

[
![ansible-ssh-masters en acción]({static}/images/ansible_and_onlykey/ansible_ssh_masters.webp "Haz clic para ver a pantalla completa"){: .align-center}
]({static}/images/ansible_and_onlykey/ansible_ssh_masters.webp "Haz clic para ver a pantalla completa")


### Uso

Simplemente reemplaza `ansible-playbook` por `ansible-ssh-masters.sh`:

```bash
./ansible-ssh-masters.sh playbook.yml
```

En mi caso, antepongo `onlykey-agent` con la clave correcta:

```bash
onlykey-agent fidelramos.net -- ./ansible-ssh-masters.sh playbook.yml
```

También puedes iniciar una [subshell de `onlykey-agent`](https://docs.onlykey.io/onlykey-agent.html#start-multiple-ssh-sessions-from-a-sub-shell) y luego ejecutar `ansible-ssh-masters.sh` dentro:

```bash
onlykey-agent fidelramos.net -s
./ansible-ssh-masters.sh playbook.yml
```

Puedes pasar cualquier número de argumentos, o usar otras fuentes de inventario; se pasan tal cual a `ansible-playbook`:

```bash
./ansible-ssh-masters.sh -i production.ini playbook.yml --limit web --tags deploy -v
```

Para cambiar el tiempo máximo que pueden vivir las sesiones maestras, establece el tiempo de espera en **segundos**:

```bash
ANSIBLE_ONLYKEY_TIMEOUT=7200 ./ansible-ssh-masters.sh long-playbook.yml
```

### Puntos clave de diseño del script

Voy a ahondar en algunas decisiones deliberadas de diseño.

#### 1. Cerrar conexiones al finalizar o salir

Con el uso de `trap`, el *script* se asegura de que las conexiones se cierren tan pronto como ya no sean necesarias, o también si el *script* se interrumpe por alguna razón (Ctrl-C, proceso terminado o shell cerrada, por ejemplo).

#### 2. Limpia lo que inició

El *script* solo mata los procesos maestros de SSH que creó.

**No** limpia todo el directorio de sockets.
Puede haber otras sesiones de SSH o herramientas usando el mismo directorio de multiplexación.

#### 3. Análisis de inventario flexible

El *script* detecta el uso del argumento `-i/--inventory` y lo analiza con `ansible-inventory` para obtener los servidores donde se ejecutará el playbook.
Eso significa que cualquiera de los formatos de `--inventory` funcionará, no se limita a un archivo de inventario.

#### 4. Usa la configuración de SSH como fuente de la verdad

En lugar de extraer datos de ficheros de configuración, utiliza transparentemente la configuración de SSH.

El *script* no intenta adivinar nombres de usuario, puertos o alias de servidor desde Ansible.

Todo eso se queda en la configuración de SSH, donde pertenece.

---

## Notas de seguridad

Esta configuración **mejora la usabilidad**, pero a cambio de **disminuir la seguridad** mientras el *script* se está ejecutando.

### El compromiso fundamental

Después de autenticar un servidor con OnlyKey, esa conexión maestra de SSH permanece abierta durante el tiempo de vida configurado o hasta que el *script* termina.

Eso significa que:

- Las sesiones SSH posteriores pueden reutilizar la conexión maestra..
- No hace falta interactuar con la OnlyKey mientras esa conexión maestra siga viva.

Ese es el objetivo de la solución, pero también significa que es aún más importante proteger tu sesión local durante esa ventana temporal.

Si hubiese otros programas corriendo en el ordenador con acceso al directorio de sockets SSH podrían obtener acceso directo al servidor remoto.
Y esa es precisamente una de las principales razones para usar un dispositivo de seguridad de hardware como OnlyKey.

### Cosas que hace esta configuración para limitar el riesgo

- Los sockets viven en `~/.ssh/sockets`.
- El directorio tiene permisos `0700`, o sea sólo para el usuario propietario.
- El reenvío del agente SSH (*Agent forwarding*) está desactivado.
- El reenvío de X11 (*X11 forwarding*) está desactivado.
- El *script* cierra las conexiones al terminar.
- El tiempo de espera es explícito y finito en caso de que la limpieza automática falle por alguna razón.

Además, personalmente uso [Firejail](https://github.com/netblue30/firejail/) para aislar (*sandbox*) la mayor parte del software que se ejecuta en mi ordenador.
Mi configuración de Firejail bloquea el acceso a `~/.ssh` para la mayoría de los programas, así que me siento un poco más seguro con este enfoque.

### Por qué la limpieza automática se mantiene activada

El *script* siempre cierra todas las conexiones maestras cuando termina (vía `trap`).
Esta es una decisión de diseño para incrementar la seguridad.

Sería aún más simple dejar las conexiones abiertas hasta que se agotase su tiempo establecido.
Esto también haría que se pudiese ejecutar Ansible más veces sin nuevas autenticaciones.

Personalmente no quería eso, y no lo recomendaría como opción predeterminada ya que reduce aún más la seguridad, pero ya es cuestión de cada cuál el equilibrar la facilidad de uso con la seguridad.

Cuanto menos tiempo permanezcan abiertas las conexiones, menos probable es que puedan ser aprovechadas por un atacante o software malicioso.

---

## Reflexiones finales

Me entristece no haber podido llegar al fondo de por qué la reutilización de conexiones de Ansible no funcionaba correctamente, pero no pude dedicar más tiempo a esa investigación.

Me alegra haber encontrado esta solución alternativa, que es un punto medio razonable entre comodidad y seguridad.
Si esto no hubiera funcionado, estaba a punto de volver a las claves SSH normales, lo que habría reducido considerablemente la seguridad de mis servidores.

Si, como yo, tienes una forma engorrosa para conectar por SSH, espero que este *script* te ayude a disfrutar más de Ansible.

Si has llegado hasta aquí y tienes una idea de cómo solucionarlo *Como $DEITY manda*, ¡por favor deja un comentario!
