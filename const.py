class RequestConstants:
    def __init__(self):
        self.a_req = "A"
        self.ns_req = "NS"

    @staticmethod
    def get_qtype_hex(qtype: str):
        qtype_code = {"a": "00 01", "ns": "00 02"}
        try:
            return qtype_code[qtype]
        except KeyError:
            raise KeyError("Unknown field in header")
