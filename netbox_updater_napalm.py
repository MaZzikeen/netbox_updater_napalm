import re
import argparse
import logging
import concurrent.futures

import napalm
import pynetbox
from napalm.base.exceptions import (
    ConnectAuthError,
    ConnectionException,
    ConnectionClosedException,
    ConnectTimeoutError
)
from netmiko import NetMikoAuthenticationException
from ncclient.transport.errors import AuthenticationError
from jnpr.junos.exception import ConnectAuthError as JuniperConnectionAuthError
from pan.xapi import PanXapiError


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


def read_from_huawei_devices(device_driver):
    """Reads from Huawei devices

    As get_facts() may return unknown depending on the Huawei switch model,
    seprated funcation is defined for huawei devices to send cli command
    display version.
    """
    try:
        device_driver.open()
        send_command = str(device_driver.cli(['dis ver | include VRP']))
        os_version = re.search(r'VRP .*(V\d.*)\)', send_command).group(1)
        device_driver.close()
        return os_version
    except ConnectAuthError as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except ConnectTimeoutError as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except ConnectionClosedException as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except NetMikoAuthenticationException as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except ConnectionException as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except Exception as e:
        logging.error('%s: %s', e, device_driver.hostname)


def read_from_other_devices(device_driver):
    """Read from other platform devices

    Supported devcies:
    Cisco IOS,NX-OS,ASA,ARUBA OS,PaloAlto PAN-OS,Juniper Junos,Arista EOS
    """
    try:
        device_driver.open()
        get_facts = device_driver.get_facts()
        device_driver.close()
        return get_facts['os_version']
    except ConnectAuthError as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except ConnectTimeoutError as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except ConnectionClosedException as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except NetMikoAuthenticationException as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except AuthenticationError as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except JuniperConnectionAuthError as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except PanXapiError as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except ConnectionException as e:
        logging.error('%s: %s', e, device_driver.hostname)
    except Exception as e:
        logging.error('%s: %s', e, device_driver.hostname)


def update_netbox(device, device_driver):
    """Stores the updates on the netbox"""
    device_platform = str(device.platform)

    if device_platform == 'Huawei VRP':
        device_version = read_from_huawei_devices(device_driver)
        device.custom_fields = {'sw_version': device_version}
        device.save()
        return device.custom_fields
    elif device_platform in driver_platform.keys():
        device_version = read_from_other_devices(device_driver)
        device.custom_fields = {'sw_version': device_version}
        device.save()
        return device.custom_fields
    else:
        device_version = 'device platform is not defined'
        logging.error('%s is not defined on netbox, device ip is: %s ',
                      device_platform)
        return


def read_from_netbox(url, token):
    """Reads from netbox filtering on tenant and status"""
    nb = pynetbox.api(url=url, token=token)
    devices = nb.dcim.devices.filter(tenant='noc', status='active')
    return devices


def generate_device_drivers(devices, device_user, device_password):
    """A utility function"""
    device_driver_map = []
    for device in devices:
        device_ip = device.primary_ip.address.split('/')[0]
        device_platform = str(device.platform)
        driver = napalm.get_network_driver(driver_platform[device_platform])
        device_driver = driver(hostname=device_ip, username=device_user,
                               password=device_password)
        device_driver_map.append((device, device_driver))
    return device_driver_map


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Reads devices from netbox and stores back the updates.'
    )
    parser.add_argument('--netbox-url', required=True)
    parser.add_argument('--netbox-token', required=True)
    parser.add_argument('--device-username', required=True)
    parser.add_argument('--device-password', required=True)
    args = parser.parse_args()

    device_user = args.device_username
    device_password = args.device_password
    devices = read_from_netbox(args.netbox_url, args.netbox_token)

    device_driver_map = generate_device_drivers(devices,
                                                device_user,
                                                device_password)

    executor = concurrent.futures.ThreadPoolExecutor(5)
    futures = [
        executor.submit(update_netbox, device, device_driver)
        for device, device_driver in device_driver_map
    ]
    concurrent.futures.wait(futures)
