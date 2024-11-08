import os
import shutil
import logging

from USBManager import USBManager


class DeviceHandler:
    def __init__(self):
        self.mount_dir = "/mnt"

    def handle_device_event(self, action, device):
        if action == "add":
            self.mount_device(device)
        elif action == "remove":
            self.unmount_device(device)

    def mount_device(self, device):
        device_path = device.device_node
        mount_path = os.path.join(self.mount_dir, os.path.basename(device_path))
        try:
            if not os.path.ismount(mount_path):
                os.makedirs(mount_path, exist_ok=True)
                os.system(f"mount {device_path} {mount_path}")
                logging.info(f"Устройство {device_path} смонтировано в {mount_path}")
            else:
                logging.info(f"Устройство {device_path} уже смонтировано")
        except Exception as e:
            logging.error(f"Ошибка при монтировании устройства {device_path}: {str(e)}")

    def unmount_device(self, device):
        device_path = device.device_node
        mount_path = os.path.join(self.mount_dir, os.path.basename(device_path))
        try:
            if os.path.ismount(mount_path):
                os.system(f"umount {mount_path}")
                os.rmdir(mount_path)
                logging.info(f"Устройство {device_path} размонтировано с {mount_path}")
            else:
                logging.info(f"Устройство {device_path} не смонтировано")
        except Exception as e:
            logging.error(f"Ошибка при размонтировании устройства {device_path}: {str(e)}")
