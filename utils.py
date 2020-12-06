
import struct


def decompose(data):
    v = []
    f_size = len(data)
    bytes_arr = [ord(chr(b)) for b in struct.pack("i", f_size)]
    bytes_arr += [ord(chr(b)) for b in data]
    for b in bytes_arr:
        for i in range(7, -1, -1):
            v.append((b >> i) & 0x1)
    return v


def set_bit(n, i, x):
    mask = 1 << i
    n &= ~mask
    if x:
        n |= mask
    return n


def compose(v):
    mass_bytes = ""
    length = len(v)
    for idx in range(0, int(len(v) / 8)):
        byte = 0
        for i in range(0, 8):
            if idx * 8 + i < length:
                byte = (byte << 1) + v[idx * 8 + i]
        mass_bytes = mass_bytes + chr(byte)
    mass_bytes = [ord(b) for b in mass_bytes]
    mass_size = b''
    for b in mass_bytes[:4]:
        b = bytes([b])
        mass_size = b''.join([mass_size, b])
    payload_size = struct.unpack("i", mass_size)[0]
    mass_bytes = mass_bytes[4: payload_size + 4]
    output_data = b''
    for b in mass_bytes:
        output_data = b''.join([output_data, bytes([b])])
    return output_data


def extract(proc_image):
    width, height = proc_image.size
    conv = proc_image.convert("RGBA").getdata()
    v = []
    for h in range(height):
        for w in range(width):
            (r, g, b, a) = conv.getpixel((w, h))
            v.append(r & 1)
            v.append(g & 1)
            v.append(b & 1)
    data_out = compose(v)
    return data_out
