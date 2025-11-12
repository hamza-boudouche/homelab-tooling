# Reboot on unplug

A small utility script that reboots its host when it detects that a USB device
was unplugged. It is used during the headless install of servers in my homelab.

The USB is identified with its vendor ID and model ID given as parameters.

The script uses `lsusb` to list USB devices and identify the one we intend to monitor, and [pyudev](https://pypi.org/project/pyudev/)
to actually monitor it.

Build with `uvx pex . -r requirements.txt -e main:main -o ./dist/reboot-on-unplug.pex`
and run `./dist/reboot-on-unplug.pex`.
