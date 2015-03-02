import pytest
import subprocess
import tempfile
import time
import py

from pyepm import api, config

COW_SECRET = "0xc85ef7d79691fe79573b1a7064c19c1a9819ebdbd1faaab1a8ec92344438aaf4"

def eth_args(client, tmpdir):
    if client == 'cpp-ethereum':
        return [
                'eth',
                '-j',
                '-s', COW_SECRET,
                '-m', 'off',
                '-d', tmpdir]
    elif client == 'go-ethereum':
        return [
                'ethereum',
                '-mine=false',
                '-rpc=true',
                '-rpcport=8080',
                '-loglevel=5',
                '-bootnodes=""',
                '-nat=none',
                '-dial=false',
                '-datadir=' + tmpdir]
    else:
        raise ValueError("unknown client: %s" % client)

@pytest.fixture(scope="module", params=['cpp-ethereum', 'go-ethereum'])
def eth(request):
    tmpdir = py.path.local(tempfile.mkdtemp())

    args = eth_args(request.param, str(tmpdir))
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(2)  # Waiting for node startup

    assert process.poll() is None, "process terminated"

    def fin():
        process.terminate()
        tmpdir.remove(rec=1)
    request.addfinalizer(fin)
    return process

def assert_address(address):
    assert address.startswith("0x")
    assert len(address) == 42
    assert int(address, 16) > 0

class TestBasicRPC(object):

    def setup_class(cls):
        cls.instance = api.Api(config.get_default_config())

    def test_status(self, eth):
        assert not self.instance.is_mining()
        assert self.instance.is_listening()
        assert self.instance.defaultBlock() == -1
        assert self.instance.peer_count() == 0

    def test_coinbase(self, eth):
        coinbase = self.instance.coinbase()
        assert_address(coinbase)

    def test_accounts(self, eth):
        accounts = self.instance.accounts()
        assert len(accounts) > 0
        for account in accounts:
            assert_address(account)

    def test_block_genesis(self, eth):
        genesis = self.instance.block(0)

        for key in ['miner', 'difficulty', 'nonce', 'gasLimit', 'hash', 'number', 'parentHash', 'sha3Uncles', 'stateRoot', 'transactionsRoot', 'timestamp']:
            assert key in genesis

        assert genesis['gasLimit'] == 1000000
        assert genesis['number'] == 0

        assert int(genesis['extraData'], 16) == 0
        assert int(genesis['miner'], 16) == 0
        assert int(genesis['parentHash'], 16) == 0

    @pytest.mark.timeout(15)
    def test_create_contract(self, eth):
        # contracts/simple.se
        CODE = "0x336000556001600155604f8060146000396063567c01000000000000000000000000000000000000000000000000000000006000350463119fbbd48114156036576001600154016001555b63ea66cf6d811415604d5760015460405260206040f35b505b6000f3"
        address = self.instance.create(code=CODE)

        assert_address(address)
        self.instance.wait_for_contract(address)

