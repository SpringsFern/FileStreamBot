import pytest

from WebServer.utils.common import PATH, get_config
from WebServer.app import init_app


# constants
TEST_CONFIG_PATH = PATH / 'config' / 'api.test.yml'
CONFIG_PATH = PATH / 'config' / 'api.dev.yml'
#
config = get_config(['-c', CONFIG_PATH.as_posix()])
test_config = get_config(['-c', TEST_CONFIG_PATH.as_posix()])


@pytest.fixture
async def client(aiohttp_client):
    '''
    The fixture for the initialize client.
    '''
    app = init_app(['-c', TEST_CONFIG_PATH.as_posix()])

    return await aiohttp_client(app)
