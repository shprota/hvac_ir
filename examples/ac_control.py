import hvac_ir
import binascii
import broadlink

TICK = 32.6
IR_TOKEN = 0x26


def convert_bl(durations):
    result = bytearray()
    result.append(IR_TOKEN)
    result.append(0)  # repeat
    result.append(len(durations) % 256)
    result.append(int(len(durations) / 256))
    for dur in durations:
        num = int(round(dur / TICK))
        if num > 255:
            result.append(0)
            result.append(int(num / 256))
        result.append(num % 256)
    result.append(0x0d)
    result.append(0x05)
    result.append(0x00)
    result.append(0x00)
    result.append(0x00)
    result.append(0x00)
    return result


if __name__ == '__main__':
    Sender = hvac_ir.get_sender('daikin2')
    if Sender is None:
        print("Unknown sender")
        exit(2)
    g = Sender()
    g.send(Sender.POWER_OFF, Sender.MODE_HEAT, Sender.FAN_AUTO, 24, Sender.VDIR_SWING_DOWN,
           Sender.HDIR_SWING, False)
    s = g.durations
    bl = convert_bl(s)
    print(binascii.b2a_hex(bl))
    # mac = binascii.unhexlify("B4430DC30B2B".encode().replace(b':', b''))
    # dev = broadlink.rm(("192.168.0.10", 80), mac)
    # dev.auth()
    # dev.send_data(bl)
