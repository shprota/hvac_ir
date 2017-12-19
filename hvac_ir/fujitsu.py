from . import ACProtocol


class Fujitsu(ACProtocol):
    # Fujitsu Nocria (AWYZ14) timing constants (remote control P/N AR-PZ2)
    HDR_MARK = 3210
    HDR_SPACE = 1680
    BIT_MARK = 410
    ONE_SPACE = 1230
    ZERO_SPACE = 440

    # Fujitsu codes
    FUJITSU_MODE_AUTO = 0x00  # Operating mode
    FUJITSU_MODE_HEAT = 0x04
    FUJITSU_MODE_COOL = 0x01
    FUJITSU_MODE_DRY = 0x02
    FUJITSU_MODE_FAN = 0x03
    FUJITSU_MODE_OFF = 0xFF  # Power OFF - not real codes, but we need something...
    FUJITSU_FAN_AUTO = 0x00  # Fan speed
    FUJITSU_FAN1 = 0x04
    FUJITSU_FAN2 = 0x03
    FUJITSU_FAN3 = 0x02
    FUJITSU_FAN4 = 0x01
    FUJITSU_VDIR_MANUAL = 0x00  # Air direction modes
    FUJITSU_VDIR_SWING = 0x10
    FUJITSU_HDIR_MANUAL = 0x00
    FUJITSU_HDIR_SWING = 0x20
    FUJITSU_ECO_OFF = 0x20
    FUJITSU_ECO_ON = 0x00

    op_modes = {
        ACProtocol.MODE_AUTO: FUJITSU_MODE_AUTO,
        ACProtocol.MODE_HEAT: FUJITSU_MODE_HEAT,
        ACProtocol.MODE_COOL: FUJITSU_MODE_COOL,
        ACProtocol.MODE_DRY: FUJITSU_MODE_DRY,
        ACProtocol.MODE_FAN: FUJITSU_MODE_FAN,
    }

    fan_speeds = {
        ACProtocol.FAN_AUTO: FUJITSU_FAN_AUTO,
        ACProtocol.FAN_1: FUJITSU_FAN1,
        ACProtocol.FAN_2: FUJITSU_FAN2,
        ACProtocol.FAN_3: FUJITSU_FAN3,
        ACProtocol.FAN_4: FUJITSU_FAN4,
    }

    swing_v_map = {
        ACProtocol.VDIR_AUTO: FUJITSU_VDIR_MANUAL,
        ACProtocol.VDIR_SWING: FUJITSU_VDIR_SWING,
    }

    swing_h_map = {
        ACProtocol.VDIR_AUTO: FUJITSU_HDIR_MANUAL,
        ACProtocol.VDIR_SWING: FUJITSU_HDIR_SWING,
    }

    def send(self, power_mode_cmd, operating_mode_cmd, fan_speed_cmd, temperature_cmd, swing_v_cmd, swing_h_cmd,
             turbo_cmd=False):
        op_mode = self.op_modes.get(operating_mode_cmd, self.FUJITSU_MODE_HEAT)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.FUJITSU_FAN_AUTO)
        swing_v = self.swing_v_map.get(swing_v_cmd, self.FUJITSU_VDIR_MANUAL)
        swing_h = self.swing_v_map.get(swing_h_cmd, self.FUJITSU_HDIR_MANUAL)
        if power_mode_cmd == self.POWER_OFF:
            op_mode = self.FUJITSU_MODE_OFF
        temperature = 23
        if 15 < temperature_cmd < 31:
            temperature = temperature_cmd
        self.send_fujitsu(op_mode, fan_speed, temperature, swing_v, swing_h)

    def send_fujitsu(self, op_mode, fan_speed, temperature, swing_v, swing_h):
        send_buffer = bytearray([0x14, 0x63, 0x00, 0x10, 0x10, 0xFE, 0x09, 0x30, 0x80, 0x04, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00])
        off_command = bytearray([0x14, 0x63, 0x00, 0x10, 0x10, 0x02, 0xFD])
        checksum = 0
        send_buffer[9] = op_mode
        send_buffer[8] = (temperature - 16) << 4 | 0x01
        send_buffer[10] = fan_speed + swing_v + swing_h
        for i in range(0, 15):
            checksum = (checksum + send_buffer[i]) & 0xff
        send_buffer[15] = checksum
        if op_mode == self.FUJITSU_MODE_OFF:
            return self.send_command(off_command)
        return self.send_command(send_buffer)

    def send_command(self, send_buffer):
        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for i in range(0, len(send_buffer)):
            self.send_byte(send_buffer[i])

        self.mark()
        self.space(0)

