import asyncio
from transport.transport_interface import ITransport
from transport.listener_interface import IListener
from network.connection.raw_connection import RawConnection

class TCP(ITransport):

    def __init__(self):
        self.listener = self.Listener()

    class Listener(IListener):

        def __init__(self, handler_function=None):
            self.multiaddrs = []
            self.server = None
            self.handler = handler_function

        async def listen(self, multiaddr):
            """
            put listener in listening mode and wait for incoming connections
            :param multiaddr: multiaddr of peer
            :return: return True if successful
            """
            _multiaddr = multiaddr

            # TODO check for exceptions
            if "ipfs" in _multiaddr.get_protocols():
                # ipfs_id = multiaddr.get_ipfs_id()
                _multiaddr.remove_protocol("ipfs")

            self.multiaddrs.append(_multiaddr)
            multiaddr_dict = _multiaddr.to_options()
            coroutine = asyncio.start_server(self.handler, multiaddr_dict['host'],\
                multiaddr_dict['port'])
            self.server = await coroutine
            return True

        def get_addrs(self):
            """
            retrieve list of addresses the listener is listening on
            :return: return list of addrs
            """
            # TODO check if server is listening
            return self.multiaddrs

        def close(self, options=None):
            """
            close the listener such that no more connections
            can be open on this transport instance
            :param options: optional object potential with timeout
            a timeout value in ms that fires and destroy all connections
            :return: return True if successful
            """
            if self.server is None:
                return False
            self.server.close()
            _loop = asyncio.get_event_loop()
            _loop.run_until_complete(self.server.wait_closed())
            _loop.close()
            self.server = None
            return True

    async def dial(self, multiaddr, options=None):
        """
        dial a transport to peer listening on multiaddr
        :param multiaddr: multiaddr of peer
        :param options: optional object
        :return: True if successful
        """
        _multiaddr_dict = multiaddr.to_options()
        host = _multiaddr_dict['host']
        port = _multiaddr_dict['port']

        reader, writer = await asyncio.open_connection(host, port)

        return RawConnection(host, port, reader, writer)

    def create_listener(self, handler_function, options=None):
        """
        create listener on transport
        :param options: optional object with properties the listener must have
        :param handler_function: a function called when a new conntion is received
        that takes a connection as argument which implements interface-connection
        :return: a listener object that implements listener_interface.py
        """
        return self.Listener(handler_function)
