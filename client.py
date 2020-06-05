import socket
import sys
import server


class RequestMaker:
    def __init__(self, host, port, domain_name, source_type):
        self.host = host
        self.port = port
        self.address: tuple = (host, port)
        self.buffered_size = 1024
        self.domain = domain_name
        self.src = source_type

    def run_client_app(self):
        udp_client_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        try:
            udp_client_sock.settimeout(6.0)
            udp_client_sock.sendto(
                "".join(server.DNSHandler
                        .form_dns_request(self.domain, self.src)).replace(" ", "").encode(),
                self.address)
            message_from_server = udp_client_sock.recvfrom(self.buffered_size)
            msg = "Message from Server {}".format(message_from_server[0].decode())
            print(msg)
        except socket.timeout:
            print("the authority server does not reply,"
                  " and there is not such source in the cache."
                  " please try again.")
            sys.exit(0)


if __name__ == '__main__':
    requester = RequestMaker("127.0.0.1", 53, "e1.ru", "a")
    requester.run_client_app()
