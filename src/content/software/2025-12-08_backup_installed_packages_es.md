Title: Periodic script to back up installed OS packages
Date: 2025-12-08
Lang: es
Category: Software
Tags: backup,fish,free-software,howto,linux,shell
Slug: backup-installed-packages

Hace un tiempo [me pasé a yadm](https://github.com/haplo/dotfiles/commit/0f7aedfa2ee71ca4a5d709d2f2a21c57a83be264) para gestionar mis dotfiles.
Una de las características que más me gustan es su [soporte para el arranque (bootstrap)](https://yadm.io/docs/bootstrap).
He estado añadiendo operaciones de configuración idempotentes.

Mi última incorporación es un script que crea archivos de copia de seguridad con todos los paquetes instalados en el sistema operativo.
En caso de desastre, si tengo que reinstalar el sistema operativo, solo tengo que pasarle al gestor de paquetes la última lista respaldada para ese host.
Para la copia de seguridad de los datos estoy trabajando en una configuración aparte, ese será tema para un futuro artículo.

En cuanto al *script*, es sencillo y está adaptado a mis sistemas.
Solo es compatible con APT (uso Debian en mis servidores sin interfaz gráfica) y *pacman* (uso Arch Linux en mi ordenador de sobremesa), pero añadir DNF u otros gestores de paquetes debería ser bastante fácil.
Lo escribí en fish shell, porque ahora es [mi shell preferida]({filename}2023-12-07_migrating_to_fish_shell.md).

Puedes ver el [commit en mis dotfiles](https://github.com/haplo/dotfiles/commit/3d9c8e0f545a9f7636148cce050dbd88c447ea29) para ver todos los cambios, pero los reproduciré a continuación tal y como estaban en el momento de escribir este artículo.

El script principal lo he puesto en *~/.local/bin/backup_installed_packages_list.fish*:

```fish
#!/usr/bin/env fish

function get_hostname
    if type -q hostname
        hostname
    else if type -q hostnamectl
        hostnamectl --static
    else if test -f /etc/hostname
        read -l host_from_file < /etc/hostname
        echo $host_from_file | string trim
    else
        echo "Error: cannot reliably get hostname" >&2
        exit 2
    end
end

set current_hostname (get_hostname)
set current_date (date +%Y-%m-%d)
set backup_dir "$HOME/Backups/$current_hostname/packages"
set temp_file (mktemp)

function save_if_changed -a input_file -a suffix
    set -l target_file "$backup_dir/$current_date$suffix.txt"

    # regex matches YYYY-MM-DD followed optionally by suffix, ending in .txt
    set -l pattern
    if test -z "$suffix"
        set pattern '^\d{4}-\d{2}-\d{2}\.txt$'
    else
        set pattern "^\d{4}-\d{2}-\d{2}$suffix\.txt\$"
    end

    # find the most recent backup file that matches the specific pattern
    set -l latest_backup_name (ls -1 $backup_dir 2>/dev/null | string match -r $pattern | sort | tail -n 1)

    if test -n "$latest_backup_name"
        set -l latest_backup_path "$backup_dir/$latest_backup_name"

        if cmp -s $input_file $latest_backup_path
            echo "No changes in package list compared to $latest_backup_path. Skipping."
            rm $input_file
            return
        end
    end

    # if we reach here, either no backup exists or content is different
    mv $input_file $target_file
    echo "Installed packages backup saved: $target_file"
    notify-send \
        --urgency=normal \
        --wait \
        --icon=backup \
        "New backup of installed OS packages: $target_file"
end

mkdir -p $backup_dir

if type -q apt
    # https://www.debian.org/doc/manuals/debian-reference/ch10.en.html#_backup_and_recovery_policy
    dpkg --get-selections > $temp_file
    save_if_changed $temp_file ""
else if type -q pacman
    # https://wiki.archlinux.org/title/Migrate_installation_to_new_hardware#List_of_installed_packages
    pacman -Qqen > $temp_file
    save_if_changed $temp_file ""
    pacman -Qqem > $temp_file
    save_if_changed $temp_file "_aur"
else
    echo "Error: Neither apt nor pacman found." >&2
    rm $temp_file
    exit 1
end
```

Creé la función de ayuda `get_hostname` porque mi instalación de Arch Linux no tenía disponible el comando `hostname`, solo `hostnamectl`.

`notify-send` es muy útil para recibir notificaciones de escritorio, lo he estado usando con frecuencia en mis nuevos *scripts*, sobre todo en los que se ejecutan en segundo plano como este.
Ten en cuenta que requiere tener instalado *libnotify* (*libnotify-bin* en instalaciones basadas en Debian).
Yo lo instalo como un paquete común en mi configuración de arranque de yadm.

Luego defino las unidades de servicio y temporizador de systemd, en *~/.config/systemd/user/backup-installed-packages.service* y *~/.config/systemd/user/backup-installed-packages.timer*:

```systemd
[Unit]
Description=Backup list of installed OS packages
After=graphical-session.target

[Service]
Type=oneshot
ExecStart=%h/.local/bin/backup_installed_packages_list.fish
StandardOutput=journal
StandardError=journal
```

```systemd
[Unit]
Description=Timer to backup list of installed OS packages

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Y después activa el temporizador:

```
$ systemctl --user daemon-reload
$ systemctl --user enable --now backup-installed-packages.timer
```

Activo el temporizador de systemd en mi archivo de [arranque de yadm](https://github.com/haplo/dotfiles/blob/master/.config/yadm/bootstrap).
