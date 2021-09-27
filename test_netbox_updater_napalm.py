import json
from unittest.mock import patch

import napalm
import pytest
import pynetbox
from netbox_updater_napalm import (
    read_from_huawei_devices,
    read_from_other_devices,
    read_from_netbox,
    update_netbox,
    generate_device_drivers
)


class Response(object):

    def __init__(self, fixture=None, status_code=200, ok=True, content=None):

        self.status_code = status_code
        self.content = (
            json.dumps(content) if content else self.load_fixture(fixture)
        )
        self.ok = ok

    def load_fixture(self, path):
        with open(path, "r") as f:
            return f.read()

    def json(self):
        return json.loads(self.content)


@pytest.fixture
def other_driver_except():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={'path': 'OtherPatforms/exceptions/except'}
    )
    yield device_driver


@pytest.fixture
def other_driver_connect_timeout_error():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={'path': 'OtherPatforms/exceptions/ConnectTimeoutError'}
    )
    yield device_driver


@pytest.fixture
def other_driver_connection_exception():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={'path': 'OtherPatforms/exceptions/ConnectionException/'}
    )
    yield device_driver


@pytest.fixture
def huawei_driver():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={'path': 'Huawei/cli'}
    )
    yield device_driver


@pytest.fixture
def huawei_driver_connection_closed_exception():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={'path': 'Huawei/exceptions/ConnectionClosedException'}
    )
    yield device_driver


@pytest.fixture
def huawei_driver_netmiko_authentication_exception():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={
            'path': 'Huawei/exceptions/NetMikoAuthenticationException'
        }
    )
    yield device_driver


@pytest.fixture
def huawei_driver_connection_exception():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={'path': 'Huawei/exceptions/ConnectionException'}
    )
    yield device_driver


@pytest.fixture
def huawei_driver_connect_timeout_error():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={'path': 'Huawei/exceptions/ConnectTimeoutError/'}
    )
    yield device_driver


@pytest.fixture
def huawei_driver_except():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={'path': 'Huawei/exceptions/except'}
    )
    yield device_driver


@pytest.fixture
def huawei_driver_ConnectAuthError():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={'path': 'Huawei/exceptions/ConnectAuthError'}
    )
    yield device_driver


@pytest.fixture
def other_driver():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={'path': 'OtherPatforms/getfacts/'}
    )
    yield device_driver


@pytest.fixture
def other_driver_connection_closed_exception():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={
            'path': 'OtherPatforms/exceptions/ConnectionClosedException'
        }
    )
    yield device_driver


@pytest.fixture
def other_driver_netmiko_authentication_exception():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={
            'path': 'OtherPatforms/exceptions/NetMikoAuthenticationException'
        }
    )
    yield device_driver


@pytest.fixture
def other_driver_ConnectAuthError():
    driver = napalm.get_network_driver('mock')
    device_driver = driver(
        hostname='foo',
        username='user',
        password='pass',
        optional_args={'path': 'OtherPatforms/exceptions//ConnectAuthError/'}
    )
    yield device_driver


@pytest.fixture
def netbox_sample():
    with patch(
        "requests.sessions.Session.get",
        return_value=Response(fixture='alldevices.json'),
    ):
        with patch(
            "requests.sessions.Session.patch",
            return_value=Response(fixture='alldevices.json'),
        ):
            yield pynetbox.api('http://0.0.0.0:8000/', **{})


def test_read_from_huawei_devices(huawei_driver):
    os_version = read_from_huawei_devices(huawei_driver)
    assert os_version == "V600R009C20SPC600"


def test_read_from_huawei_devices_connection_closed_exception(
        huawei_driver_connection_closed_exception
):
    read_from_huawei_devices(huawei_driver_connection_closed_exception)


def test_read_from_huawei_devices_netmiko_authentication_exception(
        huawei_driver_netmiko_authentication_exception
):
    read_from_huawei_devices(huawei_driver_netmiko_authentication_exception)


def test_read_from_huawei_devices_connection_exception(
        huawei_driver_connection_exception
):
    read_from_huawei_devices(huawei_driver_connection_exception)


def test_read_from_huawei_devices_connect_timeout_error(
    huawei_driver_connect_timeout_error
):
    read_from_huawei_devices(huawei_driver_connect_timeout_error)


def test_read_from_huawei_devices_connection_auth_exception(
    huawei_driver_ConnectAuthError
):
    read_from_huawei_devices(huawei_driver_ConnectAuthError)


def test_read_from_huawei_devices_except(huawei_driver_except):
    read_from_huawei_devices(huawei_driver_except)


def test_read_from_other_devices(other_driver):
    os_version = read_from_other_devices(other_driver)
    assert os_version == "8.4(2)"


def test_read_from_other_devices_connection_closed_exception(
    other_driver_connection_closed_exception
):
    read_from_other_devices(other_driver_connection_closed_exception)


def test_read_from_other_devices_netmiko_authentication_exception(
    other_driver_netmiko_authentication_exception
):
    read_from_other_devices(other_driver_netmiko_authentication_exception)


def test_read_from_other_devices_connection_exception(
        other_driver_connection_exception
):
    read_from_other_devices(other_driver_connection_exception)


def test_read_from_other_devices_connect_timeout_error(
        other_driver_connect_timeout_error
):
    read_from_other_devices(other_driver_connect_timeout_error)


def test_read_from_other_devices_connection_auth_exception(
        other_driver_ConnectAuthError
):
    read_from_other_devices(other_driver_ConnectAuthError)


def test_read_from_other_devices_except(other_driver_except):
    read_from_other_devices(other_driver_except)


def test_get_devices_returns_active_devices(netbox_sample):
    devices = list(read_from_netbox('url', 'token'))
    for device in devices:
        assert device['status']['label'] == 'Active'


def test_get_devices_returns_noc_devices(netbox_sample):
    devices = list(read_from_netbox('url', 'token'))
    for device in devices:
        assert device['tenant']['slug'] == 'noc'


def test_get_devices_returns_ip_platform_devices(netbox_sample):
    devices = list(read_from_netbox('url', 'token'))
    assert devices[0]['primary_ip']['address'] == '10.1.1.3/32'
    assert devices[0]['platform']['display'] == 'PaloAlto PAN-OS'


def test_update_netbox(netbox_sample, other_driver):
    device = list(read_from_netbox('url', 'token'))[0]
    assert update_netbox(device, other_driver) == {'sw_version': '8.4(2)'}


def test_generate_device_drivers(netbox_sample):
    devices = netbox_sample.dcim.devices.filter(tenant='noc', status='active')
    result = generate_device_drivers(devices, 'user', 'pass')
    assert len(result) == 4
