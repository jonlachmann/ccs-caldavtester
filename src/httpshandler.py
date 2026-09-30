##
# Copyright (c) 2010-2016 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

import http.client
import socket
import ssl as sslmodule


def _sslContext(cert=None):
    # ponytail: no server cert verification, same as the py2 version; add a
    # serverinfo option for a CA bundle if testing against production servers matters
    context = sslmodule.SSLContext(sslmodule.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = sslmodule.CERT_NONE
    if cert:
        context.load_cert_chain(cert)
    return context


class UnixSocketHTTPConnection(http.client.HTTPConnection):
    """
    An L{http.client.HTTPConnection} class that uses a unix socket rather than TCP.
    """

    def __init__(self, path, host, port):
        http.client.HTTPConnection.__init__(self, host, port)
        self.path = path

    def connect(self):
        """
        Connect using the supplied unix socket file path
        """
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.path)


def SmartHTTPConnection(host, port, ssl, afunix, cert=None):
    """
    Create and connect the appropriate L{http.client.HTTPConnection} for the supplied arguments.

    @param host: TCP host name
    @type host: L{str}
    @param port: TCP port number
    @type port: L{int}
    @param ssl: indicates if SSL is to be used
    @type ssl: L{bool}
    @param afunix: unix socket to use or L{None}
    @type afunix: L{str}
    @param cert: SSL client cert path to use or L{None}
    @type cert: L{str}
    """

    if afunix:
        connect = UnixSocketHTTPConnection(afunix, host, port)
    elif ssl:
        connect = http.client.HTTPSConnection(host, port, context=_sslContext(cert))
    else:
        connect = http.client.HTTPConnection(host, port)
    connect.connect()
    return connect
