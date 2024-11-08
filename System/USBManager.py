import logging

import pyudev
import threading


logging.basicConfig(filename='super_app.log', level=logging.INFO, format='%(asctime)s - %(message)s')
class USBManager:
    def __init__(self, app):
        self.app = app
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='block', device_type='partition')
        self.observer = pyudev.MonitorObserver(self.monitor, self.device_event)
        self.thread = threading.Thread(target=self.start_observer)
        self.original_paths = {}

    def start(self):
        self.thread.start()

    def start_observer(self):
        self.observer.start()

    def device_event(self, action, device):
        logging.info(f"Action: {action}, Device: {device}")
        for attribute in device.items():
            logging.info(f"Attribute: {attribute[0]} = {attribute[1]}")
        self.app.handle_device_event(action, device)
