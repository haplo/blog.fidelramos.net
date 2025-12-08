Title: Periodic script to back up installed OS packages
Date: 2025-12-08
Lang: en
Category: Software
Tags: backup,fish,free-software,howto,linux,shell
Slug: backup-installed-packages

A while ago I [switched to yadm](https://github.com/haplo/dotfiles/commit/0f7aedfa2ee71ca4a5d709d2f2a21c57a83be264) for managing my dotfiles.
One of its features I have been enjoying is its [bootstrap support](https://yadm.io/docs/bootstrap).
I have been adding idempotent setup operations

My latest addition is a script that creates backup files with all installed OS packages.
In case of disaster if I have to reinstall the OS I can just feed the package manager the latest backup list for that host.
I'm working on a different set up for my data backup, that will be the subject of a future post.

On to the script, it is simple and tailored for my systems.
It only supports APT (I use Debian for my headless servers) and pacman (I use Arch Linux on my desktop), but adding DNF or other package managers should be easy enough.
I wrote it in fish shell, because it is [my preferred shell now]({filename}2023-12-07_migrating_to_fish_shell.md).

You can see the [commit in my dotfiles](https://github.com/haplo/dotfiles/commit/3d9c8e0f545a9f7636148cce050dbd88c447ea29) for the full changes, but I will be reproducing them below as of the time of writing this article.

The main script I put in *~/.local/bin/backup_installed_packages_list.fish*:

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

I made the `get_hostname` helper because my Arch Linux setup didn't have the `hostname` command available, only `hostnamectl`.

`notify-send` is nice to get desktop notifications, I have been using it frequently in my new scripts, especially those running in the background like this one.
Note that it requires *libnotify* to be installed (*libnotify-bin* in Debian-based installations).
I install it as a common package in my yadm bootstrap configuration.

I then define systemd service and timer units, in *~/.config/systemd/user/backup-installed-packages.service* and *~/.config/systemd/user/backup-installed-packages.timer*:

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

Then just enable the timer:

```
$ systemctl --user daemon-reload
$ systemctl --user enable --now backup-installed-packages.timer
```

I enable the systemd timer in my [yadm bootstrap](https://github.com/haplo/dotfiles/blob/master/.config/yadm/bootstrap) file.
