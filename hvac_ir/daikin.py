from . import ACProtocol


class Daikin(ACProtocol):
    # Daikin timing constants
    HDR_MARK = 5050
    HDR_SPACE = 2100
    BIT_MARK = 391
    ONE_SPACE = 1725
    ZERO_SPACE = 667
    MSG_SPACE = 30000

    # Daikin codes
    DAIKIN_MODE_AUTO = 0x10  # Operating mode
    DAIKIN_MODE_HEAT = 0x40
    DAIKIN_MODE_COOL = 0x30
    DAIKIN_MODE_DRY = 0x20
    DAIKIN_MODE_FAN = 0x60

    DAIKIN_FAN_AUTO = 0x0A  # Fan speed
    DAIKIN_FAN1 = 0x03
    DAIKIN_FAN2 = 0x04
    DAIKIN_FAN3 = 0x05
    DAIKIN_FAN4 = 0x06
    DAIKIN_FAN5 = 0x07

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
        power_mode = 0x1 if power_mode_cmd == self.POWER_ON else 0x0
        op_mode = self.op_modes.get(operating_mode_cmd, self.DAIKIN_MODE_AUTO)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.DAIKIN_FAN_AUTO)
        temperature = 0x10  # 18 deg
        if (operating_mode_cmd == self.MODE_HEAT and 13 < temperature_cmd < 29) \
                or (operating_mode_cmd == self.MODE_COOL and 17 < temperature_cmd < 33) \
                or 17 < temperature_cmd < 30:
            temperature = (temperature_cmd << 1) - 20
        if operating_mode_cmd == self.MODE_DRY:
            temperature = 0x80
        if operating_mode_cmd == self.MODE_FAN:
            temperature = 0xc0

        self.send_daikin(power_mode, op_mode, fan_speed, temperature)

    def send_daikin(self, power_mode, op_mode, fan_speed, temperature):
        send_buffer = bytearray(b'\x11\xDA\x27\xF0\x0D\x00\x0F\x11\xDA\x27\x00\xD3\x11\x00\x00\x00\x1E\x0A\x08\x26')
        send_buffer[12] = power_mode | op_mode
        send_buffer[16] = temperature
        send_buffer[17] = fan_speed

        checksum = 0
        for i in range(7, 19):
            checksum = checksum + send_buffer[i]

        send_buffer[19] = checksum & 0xff

        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for i in range(0, 7):
            self.send_byte(send_buffer[i])

        self.mark()
        self.space(self.MSG_SPACE)

        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for i in range(7, 20):
            self.send_byte(send_buffer[i])

        self.mark()
        self.space(0)

