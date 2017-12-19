from . import ACProtocol


class Hisense(ACProtocol):
    # Hisense timing constants
    HDR_MARK = 9060
    HDR_SPACE = 4550
    BIT_MARK = 520
    ONE_SPACE = 1700
    ZERO_SPACE = 630
    MSG_SPACE = 8140

    # Power state
    HISENSE_POWER_OFF = 0x04  # **
    HISENSE_POWER_ON = 0x00  # **

    # Operating modes
    # Hisense codes
    HISENSE_MODE_AUTO = 0x04  # Not available 0x00
    HISENSE_MODE_HEAT = 0x00
    HISENSE_MODE_COOL = 0x02
    HISENSE_MODE_DRY = 0x03
    HISENSE_MODE_FAN = 0x04
    HISENSE_MODE_MAINT = 0x04  # Power OFF

    # Fan speeds. Note that some heatpumps have less than 5 fan speeds

    HISENSE_FAN_AUTO = 0x00  # Fan speed
    HISENSE_FAN1 = 0x03  # * low
    HISENSE_FAN2 = 0x02  # * med
    HISENSE_FAN3 = 0x01  # * high

    op_modes = {
        ACProtocol.MODE_AUTO: HISENSE_MODE_AUTO,
        ACProtocol.MODE_HEAT: HISENSE_MODE_HEAT,
        ACProtocol.MODE_COOL: HISENSE_MODE_COOL,
        ACProtocol.MODE_DRY: HISENSE_MODE_DRY,
        ACProtocol.MODE_FAN: HISENSE_MODE_FAN,
    }

    fan_speeds = {
        ACProtocol.FAN_AUTO: HISENSE_FAN_AUTO,
        ACProtocol.FAN_1: HISENSE_FAN1,
        ACProtocol.FAN_2: HISENSE_FAN2,
        ACProtocol.FAN_3: HISENSE_FAN3,
    }

    def send(self, power_mode_cmd, operating_mode_cmd, fan_speed_cmd, temperature_cmd, swing_v_cmd, swing_h_cmd,
             turbo_cmd=False):
        op_mode = self.op_modes.get(operating_mode_cmd, self.HISENSE_MODE_HEAT)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.HISENSE_FAN_AUTO)
        temperature = 23
        if 17 < temperature_cmd < 33:
            temperature = temperature_cmd
        if op_mode == self.HISENSE_MODE_FAN and fan_speed == self.HISENSE_FAN_AUTO:
            fan_speed = self.HISENSE_FAN1
            temperature = 25

        if op_mode == self.HISENSE_MODE_AUTO:
            fan_speed = self.HISENSE_FAN_AUTO

        power_mode = self.HISENSE_POWER_ON if power_mode_cmd == self.POWER_ON else self.HISENSE_POWER_OFF

        self.send_hisense(power_mode, op_mode, fan_speed, temperature)

    def send_hisense(self, power_mode, op_mode, fan_speed, temperature):
        send_buffer = bytearray([0x87, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x00, 0x00, 0x00])
        send_buffer[2] = fan_speed | power_mode
        send_buffer[3] = (((temperature - 18) << 4) | op_mode)
        send_buffer[13] = send_buffer[2]
        for i in range(3, 13):
            send_buffer[13] = send_buffer[13] ^ send_buffer[i]

        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for i in range(0, 7):
            self.send_byte(send_buffer[i])

        self.mark()
        self.space(self.MSG_SPACE)

        for i in range(7, 14):
            self.send_byte(send_buffer[i])

        self.mark()
        self.space(0)
