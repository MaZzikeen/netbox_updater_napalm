## netbox_updater_napalm

netbox_updater_napalm is written in Python3.

## Setup

Clone the project:
```
git clone https://github.com/MaZzikeen/netbox_updater_napalm
and then go to ./netbox_updater_napalm directory
```

Create a virtual environment to run the script(optional):
```

python3 -m venv venv
source venv/bin/activate
```

Install required libraries:
```
pip3 install -r requirements.txt 
```

Run the script in below format:
```
python netbox_updater_napalm.py  --netbox-url NETBOXURL  --netbox-token TOKEN --device-username USERNAME --device-password PASSWORD 
##if password includes special characters put it in the " ".
```

Run the Pytest in below format:
```
pytest test_netbox_updater_napalm.py 
```

## Architecture
The script aim is to get OS Version from Network devices and Update the custom_field {sw_version} part in the Netbox.

The script includes 5 functions:

1.read_from_netbox(url, token)

2.generate_device_drivers(devices, device_user, device_password)

3.read_from_huawei_devices(device_driver)

4.read_from_other_devices(device_driver) #Cisco IOS,NX-OS,ASA,ARUBA OS,PaloAlto PAN-OS,Juniper Junos,Arista EOS

5.update_netbox(device, device_driver)

#read_from_netbox(url, token):

Gets devices from netbox . In this script filter is used to only get devices with status: “active" and tenant:"noc".
pynetbox library is used to interact with Netbox.

#generate_device_drivers(devices, device_user, device_password)

Generates a list of tuples(driver,device_driver)
```
driver: napalm.get_network_driver(driver_platform[device_platform])
NOTE: in this script platforms defined as below dictionary keys in the netbox
driver_platform = {
    'Cisco IOS': 'ios',
    'Cisco Nexus': 'nxos',
    'Cisco ASA': 'asa',
    'Aruba OS': 'aos',
    'PaloAlto PAN-OS': 'panos',
    'Juniper Junos': 'junos',
    'Arista EOS': 'eos',
    'Huawei VRP': 'huawei_vrp'
}
If these platforms defined diffently on your netbox
You should change the driver_platform keys in the script based what you defined on
Netbox.
```
napalm library uses different driver for connecting to different platforms.
in the script driver is specified based on device_platform.
```
device_driver:driver(hostname=device_ip, username=device_user, password=device_password)                            
```
napalm library uses driver,device IP,device user,device password to connect to devices

#read_from_huawei_devices(device_driver)

As napalm get_facts() may return unknown depending on the Huawei switch model, separated function is defined for Huawei devices to send cli command of
display version. 

#read_from_other_devices(device_driver) 

Napalm get_facts() is used to get OS version of Cisco IOS,NX-OS,ASA,ARUBA OS,PaloAlto PAN-OS,Juniper Junos,Arista EOS platforms
 
#Note: Napalm by default supports below Operating Systems:

• Arista EOS
• Cisco IOS
• Cisco IOS-XR
• Cisco NX-OS
• Juniper JunOS

For rest of platforms required driver should be installed.

#Note some devices may not be able to work with Napalm library. For instance napalm asa driver makes use of the Cisco ASA REST API. 
The REST API is not available on all ASA models. 
For devices which are not able to use napalm library you can use Netmiko library.

#update_netbox(device, device_driver)

Get the OS Version from read_from_huawei_devices/read_from_other_devices functions and updates the custom_field {sw_version} part in the Netbox.

#For Multi-Threading concurrent.futures is used.
