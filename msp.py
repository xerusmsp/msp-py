"""
A Python implementation to interact with the MSP API
"""

import hashlib
import binascii
import random
import base64
import msp_tls_client
from typing import List, Union
from datetime import date, datetime
from pyamf import remoting, ASObject, TypedObject, AMF3, amf3
from secrets import token_hex

def get_marking_id() -> int:
    """
    Generate a random marking ID
    """
    marking_id = random.randint(2**0, 2**32)
    return marking_id

def ticket_header(ticket: str) -> ASObject:
    """
    Generate a ticket header for the given ticket
    """

    marking_id = get_marking_id()
    marking_id_bytes = str(marking_id).encode('utf-8')
    marking_id_hash = hashlib.md5(marking_id_bytes).hexdigest()
    marking_id_hex = binascii.hexlify(marking_id_bytes).decode()
    return ASObject({"Ticket": ticket + marking_id_hash + marking_id_hex, "anyAttribute": None})


def calculate_checksum(arguments: Union[int, str, bool, bytes, List[Union[int, str, bool, bytes]],
                                       dict, date, datetime, ASObject, TypedObject]) -> str:
    """
    Calculate the checksum for the given arguments
    """

    checked_objects = {}
    no_ticket_value = "XSV7%!5!AX2L8@vn"
    salt = "2zKzokBI4^26#oiP"

    def from_object(obj):
        if obj is None:
            return ""

        if isinstance(obj, (int, str, bool)):
            return str(obj)

        if isinstance(obj, amf3.ByteArray):
            return from_byte_array(obj)

        if isinstance(obj, (date, datetime)):
            return str(obj.year) + str(obj.month - 1) + str(obj.day)

        if isinstance(obj, (list, dict)) and "Ticket" not in obj:
            return from_array(obj)

        return ""

    def from_byte_array(bytes):
        if len(bytes) <= 20:
            return bytes.getvalue().hex()

        num = len(bytes) // 20
        array = bytearray(20)
        for i in range(20):
            bytes.seek(num * i)
            array[i] = bytes.read(1)[0]

        return array.hex()

    def from_array(arr):
        result = ""
        for item in arr:
            if isinstance(item, (ASObject, TypedObject)):
                result += from_object(item)
            else:
                result += from_object_inner(item)
        return result

    def get_ticket_value(arr):
        for obj in arr:
            if isinstance(obj, ASObject) and "Ticket" in obj:
                ticket_str = obj["Ticket"]
                if ',' in ticket_str:
                    ticket_parts = ticket_str.split(',')
                    return ticket_parts[0] + ticket_parts[5][-5:]
        return no_ticket_value

    def from_object_inner(obj):
        result = ""
        if isinstance(obj, dict):
            for key in sorted(obj.keys()):
                result += from_object(obj[key])
                checked_objects[key] = True
        else:
            result += from_object(obj)
        return result

    result_str = from_object_inner(arguments) + salt + get_ticket_value(arguments)
    return hashlib.sha1(result_str.encode()).hexdigest()


def invoke_method(server: str, method: str, params: list, session_id: str) -> tuple[int, any]:
    """
    Invoke a method on the MSP API
    """

    if server.lower() == "uk":
        server = "gb"

    req = remoting.Request(target=method, body=params)
    event = remoting.Envelope(AMF3)

    event.headers = remoting.HeaderCollection({
        ("sessionID", False, session_id),
        ("needClassName", False, False),
        ("id", False, calculate_checksum(params)
    )})

    event['/1'] = req
    encoded_req = remoting.encode(event).getvalue()

    full_endpoint = f"https://ws-{server}.mspapis.com/Gateway.aspx?method={method}"

    session = msp_tls_client.Session(
        client_identifier="xerus_ja3_spoof",
        force_http1=True,
    )

    headers = {
        "Referer": "app:/cache/t1.bin/[[DYNAMIC]]/2",
        "Accept": ("text/xml, application/xml, application/xhtml+xml, "
                   "text/html;q=0.9, text/plain;q=0.8, text/css, image/png, "
                   "image/jpeg, image/gif;q=0.8, application/x-shockwave-flash, "
                   "video/mp4;q=0.9, flv-application/octet-stream;q=0.8, "
                   "video/x-flv;q=0.7, audio/mp4, application/futuresplash, "
                   "/;q=0.5, application/x-mpegURL"),
        "x-flash-version": "32,0,0,100",
        "Content-Type": "application/x-amf",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows; U; en) AppleWebKit/533.19.4 "
                      "(KHTML, like Gecko) AdobeAIR/32.0",
        "Connection": "Keep-Alive",
    }

    response = session.post(full_endpoint, data=encoded_req, headers=headers)

    resp_data = response.content if response.status_code == 200 else None

    if response.status_code != 200:
        return (response.status_code, resp_data)
    return (response.status_code, remoting.decode(resp_data)["/1"].body)


def get_session_id() -> str:
    """
    Generate a random session id
    """
    return base64.b64encode(token_hex(23).encode()).decode()
