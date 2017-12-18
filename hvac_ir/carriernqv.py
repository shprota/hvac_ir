from . import ACProtocol


class Carriernqv(ACProtocol):
    #  Carrier (42NQV035G / 38NYV035H2) timing constants (remote control P/N WH-L05SE)
    HDR_MARK = 4320
    HDR_SPACE = 4350
    BIT_MARK = 500
    ONE_SPACE = 1650
    ZERO_SPACE = 550
    MSG_SPACE = 7400

    #  Carrier codes
    CARRIER_MODE_AUTO = 0x00  # Operating mode
    CARRIER_MODE_HEAT = 0xC0
    CARRIER_MODE_COOL = 0x80
    CARRIER_MODE_DRY = 0x40
    CARRIER_MODE_FAN = 0x20
    CARRIER_MODE_OFF = 0xE0  # Power OFF
    CARRIER_FAN_AUTO = 0x00  # Fan speed
    CARRIER_FAN1 = 0x02
    CARRIER_FAN2 = 0x06
    CARRIER_FAN3 = 0x01
    CARRIER_FAN4 = 0x05
    CARRIER_FAN5 = 0x03

    op_modes = {
        ACProtocol.MODE_AUTO: CARRIER_MODE_AUTO,
        ACProtocol.MODE_HEAT: CARRIER_MODE_HEAT,
        ACProtocol.MODE_COOL: CARRIER_MODE_COOL,
        ACProtocol.MODE_DRY: CARRIER_MODE_DRY,
        ACProtocol.MODE_FAN: CARRIER_MODE_FAN,
    }

    fan_speeds = {
        ACProtocol.FAN_AUTO: CARRIER_FAN_AUTO,
        ACProtocol.FAN_1: CARRIER_FAN1,
        ACProtocol.FAN_2: CARRIER_FAN2,
        ACProtocol.FAN_3: CARRIER_FAN3,
    }

    def send(self, power_mode_cmd, operating_mode_cmd, fan_speed_cmd, temperature_cmd, swing_v_cmd, swing_h_cmd,
             turbo_cmd=False):
        op_mode = self.CARRIER_MODE_OFF if power_mode_cmd == self.POWER_OFF else self.op_modes.get(operating_mode_cmd)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.CARRIER_FAN_AUTO)
        temperature = temperature_cmd - 17 if 16 < temperature_cmd < 31 else 7
        self.send_carrier(op_mode, fan_speed, temperature)

    def send_carrier(self, op_mode, fan_speed, temperature):
        send_buffer = bytearray(b'\x4f\xb0\xc0\x3f\x80\x00\x00\x00\x00')
        temperatures = bytearray(b'\x00\x08\x04\x0c\x02\x0a\x06\x0e\x01\x09\x05\x0d\x03\x0b')

        send_buffer[5] = temperatures[temperature]
        send_buffer[6] = op_mode | fan_speed
        checksum = self.calc_checksum(send_buffer)
        send_buffer[8] = self.bit_reverse(checksum)

        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for b in send_buffer:
            self.send_byte(b)

        self.mark()
        self.space(self.MSG_SPACE)

        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for b in send_buffer:
            self.send_byte(b)

        self.mark()
        self.space(0)

    #  There's something really strange with the checksum calculation...
    #  With these many of the codes matchs with the code from the real Carrier remote
    #  Still certain temperatures do not work with fan speeds 1, 2 or 5
    def calc_checksum(self, send_buffer):
        checksum = 0
        for i in range(8):
            checksum = checksum + self.bit_reverse(send_buffer[i])
        left = send_buffer[6] & 0xf0
        right = send_buffer[6] & 0x0f
        if left == 0:  # MODE_AUTO - certain temperature / fan speed combinations do not work
            checksum = checksum + 0x02
            if right in [0x02, 0x03, 0x06]:
                checksum = checksum + 0x80
        if left == 0x40:  # MODE_DRY - all settings should work
            checksum = checksum + 0x02
        if left == 0xc0 and right in [0x05, 0x06]:  # MODE_HEAT - certain temperature/fan speed combinations do not work
            checksum = checksum + 0xc0
        if left == 0x20:  # MODE_FAN - all settings should work
            checksum = checksum + 0x02
            if right in [0x02, 0x03, 0x06]:
                checksum = checksum + 0x80
        return checksum & 0xff
