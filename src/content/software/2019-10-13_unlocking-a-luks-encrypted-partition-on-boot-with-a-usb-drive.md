Title: Unlocking a LUKS-encrypted partition on boot with an USB drive
Date: 2019-10-13
Lang: en
Category: Software
Tags: linux,encryption,security,howto
Slug: unlock-luks-usb-drive

The use case I wanted to solve was this: I have a headless server with
a LUKS software-encrypted hard drive, and I want to be able to reboot
it without having to input the password on a keyboard. The solution I
implemented is to create a LUKS keyfile on a USB drive, so if it is
plugged on boot the keyfile will be used instead of the password.

Before we begin, a few words on the security of this approach:

* Whoever gets access to the USB drive will be able to decrypt the
  target device. Consider the security requirements of the USB drive:
  could be put on a safe box, hidden away or you could always carry it
  with you.

* It's best if the USB drive is only used for this purpose, as any
  other system where the drive is plugged in can potentially read and
  leak the encryption key.

* This is clearly reducing security to gain in usability. Sometimes
  that is the balance that we are looking for, but oftentimes it's
  not. It's up to you to decide the value of what you are protecting,
  potential attack scenarios and how much security it needs.

OK, I'm assumming you have a formatted USB drive that you have mounted
on the computer with the LUKS device you want to unlock on boot,
e.g. on `/mnt`. Then create a key file with random information:

``` text
# dd if=/dev/urandom of=/mnt/key bs=4096 count=1
```

Add the generated key to LUKS, so it can be used to decrypt the root
device:

``` text
# cryptsetup luksAddKey /dev/sda3 /mnt/key
```

`/dev/sda3` should be the encrypted partition that holds your root
filesystem.

Next we will update `/etc/crypttab`, which defines encrypted volumes
that can be handled by LUKS. Your `crypttab` file should have an entry
similar to this one:

``` text
cryptroot UUID=452ac6ac-8bbb-484f-b508-a11a5585e031 none luks
```

We need to update this line to use the `passdev` script provided by
`cryptsetup`. This script handles waiting for a device to become
available, then mounting it and reading the key from a file. It's a
good idea to refer to the USB drive using a device that won't change
unexpectedly. I'm using `/dev/disk/by-label/<LABEL>`, which is a
symlink to the device based on the partition label. After updating
`/etc/crypttab` it should look like this:

``` text
cryptroot UUID=452ac6ac-8bbb-484f-b508-a11a5585e031 /dev/disk/by-label/FIDELRAMOS.NET:/key:20 luks,keyscript=/lib/cryptsetup/scripts/passdev
```

Leave the original mapper name (`cryptroot` in this example) and UUID
of your encrypted root, otherwise things will break as the mapper name
is referenced in `/etc/fstab`. Just change the `none` and add the
keyscript to the options.

Last step is to regenerate the initramfs image so that it includes the
`passdev` script, otherwise the boot process would fail:

``` text
# update-initramfs -k all -u
```

And that's it! When rebooting the system it should mount the USB drive
automatically and decrypt the root partition using the created key
file. If the USB drive is not present it should fall back to reading
the passphrase from keyboard in 20 seconds.
