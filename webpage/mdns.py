import socket
import time
from typing import cast
import zeroconf
#https://github.com/mnishig/mdns-discover/blob/master/ServiceDiscover.py
class ZeroconfListener(zeroconf.ServiceListener):
    def __init__(self) -> None:
        super().__init__()
        self.services = []

    def remove_service(self, zc: 'Zeroconf', type_: str, name: str) -> None:
        # print('{} service: removed'.format(name) )
        info = zc.get_service_info(type_, name)

        for service in self.services:
            if service['name'] == name:
                self.services.remove(service)

    def add_service(self, zc: 'Zeroconf', type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        addr_str = []
        for item in info.addresses:
            addr_str.append(socket.inet_ntoa(cast(bytes, item)))

        # print(name, addr_str)
        item = {
            'name': info.name,
            'type': info.type,
            'server': info.server,
            'addresses': addr_str,
            'port': info.port,
        }

        self.services.append(item)

    def update_service(self, zc: 'Zeroconf', type_: str, name: str) -> None:
        pass

    def get_services(self) -> list:
        return self.services

class ServiceDiscover:
    def __init__(self) -> None:
        # self.zeroconf = zeroconf.Zeroconf()
        self.browser = None

        self.types = []
        self.services = []
        self.get_servicetypes()

    def get_servicetypes(self) -> None:
        self.types = zeroconf.ZeroconfServiceTypes.find()

    def browse(self) -> None:
        zc = zeroconf.Zeroconf()
        listener = ZeroconfListener()

        for type in self.types:
            counter = 0
            browser = zeroconf.ServiceBrowser(zc, type, listener)
            while counter < 5:
                time.sleep(0.1)
                counter += 1

            browser.cancel()
            self.services = listener.services


if __name__ == "__main__":
    sd = ServiceDiscover()
    sd.browse()

    for item in sd.services:
        print(item)