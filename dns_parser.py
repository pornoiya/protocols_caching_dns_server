import time
import const
import sys


class DNSHandler:
    @staticmethod
    def each_byte(str_byte: str, func, kwargs):
        return [func(str_byte[2 * i:2 * i + 2], **kwargs) for i in range(len(str_byte) // 2)]

    @staticmethod
    def form_qname_part(domain: str):
        labels = domain.split(".")
        qname = ""
        for label in labels:
            qname += hex(len(label))[-2:].replace("x", "0") + " "
            qname += " ".join([hex(ord(char))[-2:].replace("x", "0") for char in label]) + " "
        return qname

    @staticmethod
    def form_dns_request(domain_name, q_type):
        header = "AA AA 01 00 00 01 00 00 00 00 00 00 "
        return header, f"{DNSHandler.form_qname_part(domain_name)}" \
            f"00 {const.RequestConstants.get_qtype_hex(q_type)} 00 01"

    @staticmethod
    def parse_answer(dns_answer: str, cache: dict, offset=0):
        resources = {}

        name, _ = DNSHandler.parse_name(dns_answer)
        question = dns_answer[24 + offset:24 + offset + len(name) * 2 + 4]
        qtype = dns_answer[24 + offset + len(name) * 2 + 4: 24 + offset + len(name) * 2 + 8]
        qclass = dns_answer[24 + offset + len(name) * 2 + 8: 24 + offset + len(name) * 2 + 12]

        answer_name_class_type = dns_answer[24 + offset + len(name) * 2 + 12:24 + offset + len(name) * 2 + 28]
        ttl = dns_answer[24 + offset + len(name) * 2 + 28:24 + offset + len(name) * 2 + 32]
        answr_rdlength = dns_answer[24 + offset + len(name) * 2 + 32: 24 + offset + len(name) * 2 + 36]
        rdlength_ten_base = int(answr_rdlength, 16)
        rddata = dns_answer[24 + offset + len(name) * 2 + 36:24 + offset + len(name) * 2 + 36 + rdlength_ten_base * 2]

        resources.update({"reply_time": time.time()})
        resources.update({"ttl": int(ttl, 16)})
        resources.update({"answer_name": answer_name_class_type[:4]})
        resources.update({"answer_type": answer_name_class_type[4:8]})
        resources.update({"answer_class": answer_name_class_type[8:12]})
        resources.update({"rddata":
                         ".".join([str(b)
                                  for b in DNSHandler.each_byte(rddata, int, {"base": 16})])})

        cache.update({name: resources})

        return DNSHandler.each_byte(rddata, int, {"base": 16}),\
            len(name) + 18 + rdlength_ten_base

    @staticmethod
    def parse_answers(dns_resp: str, session_cache):
        """dns_resp is a string with hex numbers"""

        ID = dns_resp[:4]
        other_flags = dns_resp[4:8]
        questions_count = dns_resp[8:12]
        answers_count = dns_resp[12:16]
        auth_serv_info = dns_resp[16:20]
        additional_info = dns_resp[20:24]
        offset = 0
        ip = "0.0.0.0"
        for i in range(int(answers_count, 16)):
            try:
                ip, offset = DNSHandler.parse_answer(dns_resp, session_cache, offset=offset * i)
            except ValueError:
                print("url does not exist")
                sys.exit(0)
        return ip

    @staticmethod
    def parse_name(dns_answer, start=24):
        name = []
        offset = 0
        while True:
            index = start + offset
            raw = dns_answer[index:index + 4]
            if int(raw, 16) >= 49152:
                link = str(bin(int(raw, 16)))[2:]
                link = int(link[2:], 2) * 2
                rest, offset = DNSHandler.parse_name(dns_answer, link)
                name.append(rest)
                name.append(".")
                break

            length = int(dns_answer[index:index + 2], 16)
            if length == 0:
                break
            i = 2
            while i <= length * 2:
                decoded = chr(int(dns_answer[index + i:index + i + 2], 16))
                name.append(decoded)
                i += 2
            name.append(".")
            offset += length * 2 + 2
        name = "".join(name[:-1])
        return name, offset
