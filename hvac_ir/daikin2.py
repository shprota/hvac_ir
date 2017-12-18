from . import ACProtocol


class Daikin2(ACProtocol):
    # Daikin timing constants
    HDR_MARK = 3360  # 3300
    HDR_SPACE = 1760  # 1600
    BIT_MARK = 360  # 310
    ONE_SPACE = 1370  # 1220
    ZERO_SPACE = 520  # 400
    MSG_SPACE = 32300  # 30800

    # Daikin codes
    DAIKIN_MODE_AUTO = 0x00  # Operating mode
    DAIKIN_MODE_HEAT = 0x40
    DAIKIN_MODE_COOL = 0x30
    DAIKIN_MODE_DRY = 0x20
    DAIKIN_MODE_FAN = 0x60
    DAIKIN_POWER_OFF = 0x00  # Power OFF
    DAIKIN_POWER_ON = 0x01
    DAIKIN_FAN_AUTO = 0xA0  # Fan speed
    DAIKIN_FAN1 = 0x30
    DAIKIN_FAN2 = 0x40
    DAIKIN_FAN3 = 0x50
    DAIKIN_FAN4 = 0x60
    DAIKIN_FAN5 = 0x70

    op_modes = {
        ACProtocol.MODE_AUTO: DAIKIN_MODE_AUTO,
        ACProtocol.MODE_HEAT: DAIKIN_MODE_HEAT,
        ACProtocol.MODE_COOL: DAIKIN_MODE_COOL,
        ACProtocol.MODE_DRY: DAIKIN_MODE_DRY,
        ACProtocol.MODE_FAN: DAIKIN_MODE_FAN,
    }

    fan_speeds = {
        ACProtocol.FAN_AUTO: DAIKIN_FAN_AUTO,
        ACProtocol.FAN_1: DAIKIN_FAN1,
        ACProtocol.FAN_2: DAIKIN_FAN2,
        ACProtocol.FAN_3: DAIKIN_FAN3,
        ACProtocol.FAN_4: DAIKIN_FAN4,
        ACProtocol.FAN_5: DAIKIN_FAN5,
    }

    def send(self, power_mode_cmd, operating_mode_cmd, fan_speed_cmd, temperature_cmd, swing_v_cmd, swing_h_cmd,
             turbo_cmd=False):
        power_mode = self.DAIKIN_POWER_ON if power_mode_cmd == self.POWER_ON else self.DAIKIN_POWER_OFF
        op_mode = self.op_modes.get(operating_mode_cmd, self.DAIKIN_MODE_AUTO)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.DAIKIN_FAN_AUTO)
        temperature = 0x10  # 18 deg
        if (operating_mode_cmd == self.MODE_HEAT and 9 < temperature_cmd < 29) \
                or (operating_mode_cmd == self.MODE_COOL and 17 < temperature_cmd < 31):
            temperature = temperature_cmd << 1
        if operating_mode_cmd == self.MODE_DRY:
            temperature = 0x24
        if operating_mode_cmd == self.MODE_FAN:
            temperature = 0xc0

        self.send_daikin(power_mode, op_mode, fan_speed, temperature)

    def send_daikin(self, power_mode, op_mode, fan_speed, temperature):
        send_buffer = bytearray([
            0x11, 0xDA, 0x27, 0x00, 0xC5, 0x00, 0x00, 0xD7,  # First header
            #  0     1     2     3     4     5     6     7
            0x11, 0xDA, 0x27, 0x00, 0x42, 0x49, 0x05, 0xA2,
            # Second header, this seems to have the wall clock time (bytes 12 & 13 are changing)
            #  8     9    10    11    12    13    14    15
            0x11, 0xDA, 0x27, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x60, 0x00, 0x00, 0xC0, 0x00, 0x00, 0x00
            # 16    17    18    19    20    21    22    23    24    25   26     27    28    29    30    31    32    33    34
        ])

        send_buffer[21] = power_mode | op_mode
        send_buffer[22] = temperature
        send_buffer[24] = fan_speed

        checksum = 0

        for i in range(16, 34):
            checksum = (checksum + send_buffer[i]) & 0xff

        send_buffer[34] = checksum

        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for i in range(0, 8):
            self.send_byte(send_buffer[i])

        self.mark()
        self.space(self.MSG_SPACE)
        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for i in range(8, 16):
            self.send_byte(send_buffer[i])

        self.mark()
        self.space(self.MSG_SPACE)
        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for i in range(16, 35):
            self.send_byte(send_buffer[i])

        self.mark()
        self.space(0)
