import socket
import binascii
from dns_parser import DNSHandler
import sys
import threading
import os
from cache import CacheHandler


class Server:
    """Сервер. Принимает на вход хост и порт."""
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.resolver_addr = "8.8.4.4"
        self.resolver_port = 53
        self.a_req = "A"
        self.ns_req = "NS"
        self.session_cash = {}

    def run_server(self):
        """Основной метод"""
        udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server_sock.bind((self.host, self.port))
        while True:
            message, client_ip = udp_server_sock.recvfrom(1024)

            # достаем из запроса клиента доменное имя
            domain = DNSHandler.parse_name(message)[0]

            # проверяем, есть ли имя в кеше
            if domain in session_cache:
                resp = session_cache[domain]["rddata"]
            else:
                # если нет, отправляем запрос авторитетному серверу dns.google.com
                r = self.send_udp_message_to_auth_server(message.decode())

                # из ответа вычленяем айпи адрес
                resp = ".".join([str(b) for b in DNSHandler.parse_answers(r, session_cache)])
            udp_server_sock.sendto(resp.encode(), client_ip)

            # следим за обновлением кеша и полем ттл
            # с промежутком 12 секунд
            threading.Timer(12, cacher.check_resources(session_cache))
            print(f"client {client_ip} is served")

    def send_udp_message_to_auth_server(self, message):
        """send_udp_message_to_auth_server sends a message to UDP server
        message should be a hexadecimal encoded string
        """
        message = message.replace(" ", "").replace("\n", "")
        authority_server = (self.resolver_addr, self.resolver_port)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.settimeout(6.0)
            sock.sendto(binascii.unhexlify(message), authority_server)
            data, _ = sock.recvfrom(4096)
        except socket.timeout:
            print("the authority server does not reply, "
                  "and there is not such source in the cache. "
                  "please try again.")
            sys.exit(0)
        finally:
            cacher.cache_on_disk(session_cache)
            sock.close()
        return binascii.hexlify(data).decode("utf-8")


if __name__ == '__main__':
    # инициализируем кеш
    cacher = CacheHandler(os.path.join(os.getcwd(), "cache.json"))
    if os.path.isfile(cacher.path):
        session_cache = cacher.deserialize()
    else:
        session_cache = {}

    # инициализируем сервер
    dns_serv = Server("127.0.0.1", 53)
    dns_serv.run_server()

