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


def format_durations(data):
    result = ''
    for i in range(0, len(data)):
        if len(result) > 0:
            result += ' '
        result += ('+' if i % 2 == 0 else '-') + str(data[i])
    return result


if __name__ == '__main__':
    Sender = hvac_ir.get_sender('fuego')
    if Sender is None:
        print("Unknown sender")
        exit(2)
    g = Sender()
    g.send(Sender.POWER_OFF, Sender.MODE_HEAT, Sender.FAN_AUTO, 24, Sender.VDIR_SWING_DOWN,
           Sender.HDIR_SWING, False)
    durations = g.get_durations()
    print(format_durations(durations))

    # Uncommend the following to send code over Broadlink:

    # BROADLINK_IP = '192.168.0.10'
    # BROADLINK_MAC = 'B4:43:0D:C3:0B:2B'
    #
    # bl = convert_bl(durations)
    # print(binascii.b2a_hex(bl))
    # mac = binascii.unhexlify(BROADLINK_MAC.encode().replace(b':', b''))
    # dev = broadlink.rm((BROADLINK_IP, 80), mac)
    # dev.auth()
    # dev.send_data(bl)
