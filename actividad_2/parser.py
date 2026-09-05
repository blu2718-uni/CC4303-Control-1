from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

def parse_DNS_message(message):
    D = DNSRecord.parse(message)

    parsed_message = {
        "Qname":[x.get_qname for x in D.questions],
        "ANCOUNT": D.header.a,
        "NSCOUNT": D.header.auth,
        "ARCOUNT": D.header.ar,
        "Answer": D.get_a if D.header.a > 0 else D.header.a,
        "Authority": D.auth if D.header.auth > 0 else D.header.auth,
        "Additional": D.ar if D.header.ar > 0 else D.header.ar,
    }

    return D