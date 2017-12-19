from . import ACProtocol


class Hitachi(ACProtocol):
    # Hitachi remote timing constants
    HDR_MARK = 3436
    HDR_SPACE = 1640
    BIT_MARK = 420
    ONE_SPACE = 1250
    ZERO_SPACE = 500

    # Hitachi codes
    HITACHI_MODE_AUTO = 0x02  # Operating mode
    HITACHI_MODE_HEAT = 0x03
    HITACHI_MODE_COOL = 0x04
    HITACHI_MODE_DRY = 0x05
    HITACHI_MODE_FAN = 0x0C

    HITACHI_POWER_OFF = 0x00  # Power OFF
    HITACHI_POWER_ON = 0x80

    HITACHI_FAN_AUTO = 0x01  # Fan speed
    HITACHI_FAN1 = 0x02
    HITACHI_FAN2 = 0x03
    HITACHI_FAN3 = 0x04
    HITACHI_FAN4 = 0x05

    HITACHI_VDIR_AUTO = 0x00
    HITACHI_VDIR_SWING = 0x01

    HITACHI_HDIR_AUTO = 0x00
    HITACHI_HDIR_SWING = 0x01

    op_modes = {
        ACProtocol.MODE_AUTO: HITACHI_MODE_AUTO,
        ACProtocol.MODE_HEAT: HITACHI_MODE_HEAT,
        ACProtocol.MODE_COOL: HITACHI_MODE_COOL,
        ACProtocol.MODE_DRY: HITACHI_MODE_DRY,
        ACProtocol.MODE_FAN: HITACHI_MODE_FAN,
    }

    fan_speeds = {
        ACProtocol.FAN_AUTO: HITACHI_FAN_AUTO,
        ACProtocol.FAN_1: HITACHI_FAN1,
        ACProtocol.FAN_2: HITACHI_FAN2,
        ACProtocol.FAN_3: HITACHI_FAN3,
        ACProtocol.FAN_4: HITACHI_FAN4,
    }

    swing_v_map = {
        ACProtocol.VDIR_AUTO: HITACHI_VDIR_AUTO,
        ACProtocol.VDIR_SWING: HITACHI_VDIR_SWING,
    }

    swing_h_map = {
        ACProtocol.VDIR_AUTO: HITACHI_HDIR_AUTO,
        ACProtocol.VDIR_SWING: HITACHI_HDIR_SWING,
    }

    def send(self, power_mode_cmd, operating_mode_cmd, fan_speed_cmd, temperature_cmd, swing_v_cmd, swing_h_cmd,
             turbo_cmd=False):
        op_mode = self.op_modes.get(operating_mode_cmd, self.HITACHI_MODE_HEAT)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.HITACHI_FAN_AUTO)
        swing_v = self.swing_v_map.get(swing_v_cmd, self.HITACHI_VDIR_AUTO)
        swing_h = self.swing_v_map.get(swing_h_cmd, self.HITACHI_HDIR_AUTO)

        temperature = 23
        if 15 < temperature_cmd < 33:
            temperature = temperature_cmd
        if op_mode == self.HITACHI_MODE_FAN:
            temperature = 64
            if fan_speed == self.HITACHI_FAN_AUTO:
                fan_speed = self.HITACHI_FAN2

        if op_mode == self.HITACHI_MODE_DRY:
            fan_speed = self.HITACHI_FAN2

        power_mode = self.HITACHI_POWER_ON if power_mode_cmd == self.POWER_ON else self.HITACHI_POWER_OFF

        self.send_hitachi(power_mode, op_mode, fan_speed, temperature, swing_v, swing_h)

    def send_hitachi(self, power_mode, op_mode, fan_speed, temperature, swing_v, swing_h):
        send_buffer = bytearray([0x01, 0x10, 0x30, 0x40, 0xBF, 0x01, 0xFE, 0x11, 0x12, 0x08, 0x00, 0x00, 0x00, 0x00,
                                 0x06, 0x06, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x01, 0x00, 0x00, 0x00])
        if temperature == 16:
            send_buffer[9] = 0x09
        send_buffer[10] = op_mode
        send_buffer[11] = temperature << 1
        send_buffer[13] = fan_speed
        send_buffer[14] = send_buffer[14] | swing_v
        send_buffer[15] = send_buffer[15] | swing_h
        send_buffer[17] = power_mode

        checksum = 1086
        for i in range(0, 27):
            checksum = checksum - send_buffer[i]

        send_buffer[27] = checksum & 0xff

        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for i in range(0, len(send_buffer)):
            self.send_byte(send_buffer[i])

        self.mark()
        self.space(0)
