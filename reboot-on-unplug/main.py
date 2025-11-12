import pyudev
import re
import sys
import traceback
import os
import subprocess
from typing import Tuple


VENDOR_ID = os.getenv("USB_VENDOR_ID")
if not VENDOR_ID:
    print("missing env var USB_VENDOR_ID")
    sys.exit(1)

MODEL_ID = os.getenv("USB_MODEL_ID")
if not MODEL_ID:
    print("missing env var USB_MODEL_ID")
    sys.exit(1)

device_re = re.compile(r"Bus +(?P<bus>\d+) +Device +(?P<device>\d+).+ID (?P<vendorid>\w+):(?P<modelid>\w+) (?P<tag>.+)$", re.I)

def get_usb_device() -> Tuple[str, str]:
    try:
        res = subprocess.check_output("lsusb")
        for device in res.split(b'\n'):
            if device:
                info = device_re.match(device.decode("utf-8"))
                if info:
                    info_dict = info.groupdict()
                    if info_dict.get("vendorid") == VENDOR_ID and info_dict.get("modelid") == MODEL_ID:
                        # This is our device!
                        bus = info_dict.get("bus")
                        device = info_dict.get("device")
                        if not (bus and device):
                            raise Exception(f"failed to parse output of lsusb {res.decode("utf-8")}")
                        return (bus, device)
    except subprocess.CalledProcessError as e:
        print("failed to run lsusb", e)
        traceback.print_stack()
        sys.exit(1)
    raise Exception(f"usb device with VENDOR_ID: {VENDOR_ID} and MODEL_ID: {MODEL_ID} not found")

def main():
    bus, device = "", ""
    try:
        bus, device = get_usb_device()
    except Exception as e:
        print(e)
        traceback.print_stack()
        sys.exit(1)
    print("bus", bus, "device", device)

    # special character device file tied to the usb device
    devname = f"/dev/bus/usb/{bus}/{device}"

    print("starting udev monitoring...")
    monitor = pyudev.Monitor.from_netlink(pyudev.Context())
    for device in iter(monitor.poll, None):
        if device.action == "remove" and device.device_node == devname:
            print(f"USB {devname} has been removed")
            break
    if os.getenv("ENV") == "PROD":
        subprocess.run(["shutdown", "-r", "+1"])
    else:
        print("would've rebooted if I was running on PROD :)")


if __name__ == "__main__":
    main()
