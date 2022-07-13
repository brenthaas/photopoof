import bluetooth, os, struct, sys
from PyOBEX import client, headers, responses


class Printer():
    def __init__(self, filename):
        self.printer_address = self.get_printer()
        if self.printer_address:
            print("Found Printer! ({})".format(self.printer_address))
            service = self.get_service(self.printer_address)
            print("Service:")
            print(service)
            
            print("Connecting...")
            self.client = client.Client(self.printer_address, service["port"])
            self.connect_client()
            print("Printing!")
            self.print_image(filename)
        else:
            print("No printer returned")

    def connect_client(self):
        response = self.client.connect(
            header_list=(headers.Target("OBEXObjectPush".encode()),)
        )
            
        if not isinstance(response, responses.ConnectSuccess):
            sys.stderr.write("Failed to connect.\n")
            sys.exit(1)
    
    def disconnect_client(self):
        self.client.disconnect()

    def get_printer(self):
        devices = None

        while not devices:
            devices = bluetooth.discover_devices()
            if not devices: print("No bluetooth devices found... retrying")

        for device in devices:
            device_name = bluetooth.lookup_name(device)
            if device_name == "LG PD251(35:40)":
                return device
    
    def get_service(self, device_address):
        services = bluetooth.find_service(address=device_address)
        for service in services: 
            if service["name"] == "OPP": return service
    
    def print_image(self, filename):
       self.client.put(filename, open(filename, "rb").read()) 

    
if __name__ == '__main__': 
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("No Argument provided")
        
    printer=Printer(filename)