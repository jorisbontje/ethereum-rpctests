[![Stories in Ready](https://badge.waffle.io/jorisbontje/ethereum-rpctests.png?label=ready&title=Ready)](https://waffle.io/jorisbontje/ethereum-rpctests)
# Ethereum RPC Tests

JSONRPC API tests for `cpp-ethereum` and `go-ethereum`.

## Installation

```
pip install -r requirements.txt
```

The tests will assume the binaries to be on the PATH. Default ports are used, so this will conflict if there are any clients running. A temporary directory will be used (and cleaned up) for data storage.

## Usage

To run all tests:
```
$ py.test
```

To run all tests for a specific client, use the `-k match` option

```
$ py.test -k go-ethereum
```

For extra verbosity:
```
$ py.test -s -vvv
```
