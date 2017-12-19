from . import ACProtocol


class Hyundai(ACProtocol):
    # Hyundai heatpump control (remote control P/N Y512F2)
    # Hyundai timing constants
    HDR_MARK = 8840  # 8700
    HDR_SPACE = 4440  # 4200
    BIT_MARK = 640  # 580
    ONE_SPACE = 1670  # 1530
    ZERO_SPACE = 570  # 460

    # Hyundai codes
    HYUNDAI_MODE_AUTO = 0x00  # Operating mode
    HYUNDAI_MODE_HEAT = 0x04
    HYUNDAI_MODE_COOL = 0x01
    HYUNDAI_MODE_DRY = 0x02
    HYUNDAI_MODE_FAN = 0x03
    HYUNDAI_POWER_OFF = 0x00  # Power OFF
    HYUNDAI_POWER_ON = 0x08  # Power ON
    HYUNDAI_FAN_AUTO = 0x00  # Fan speed
    HYUNDAI_FAN1 = 0x10
    HYUNDAI_FAN2 = 0x20
    HYUNDAI_FAN3 = 0x30

    HYUNDAI_VDIR_SWING = 0x40  # Vertical swing
    HYUNDAI_VDIR_AUTO = 0x00  # Automatic setting

    op_modes = {
        ACProtocol.MODE_AUTO: HYUNDAI_MODE_AUTO,
        ACProtocol.MODE_HEAT: HYUNDAI_MODE_HEAT,
        ACProtocol.MODE_COOL: HYUNDAI_MODE_COOL,
        ACProtocol.MODE_DRY: HYUNDAI_MODE_DRY,
        ACProtocol.MODE_FAN: HYUNDAI_MODE_FAN,
    }

    fan_speeds = {
        ACProtocol.FAN_AUTO: HYUNDAI_FAN_AUTO,
        ACProtocol.FAN_1: HYUNDAI_FAN1,
        ACProtocol.FAN_2: HYUNDAI_FAN2,
        ACProtocol.FAN_3: HYUNDAI_FAN3,
    }

    swing_v_map = {
        ACProtocol.VDIR_AUTO: HYUNDAI_VDIR_AUTO,
        ACProtocol.VDIR_SWING: HYUNDAI_VDIR_SWING,
    }

    def send(self, power_mode_cmd, operating_mode_cmd, fan_speed_cmd, temperature_cmd, swing_v_cmd, swing_h_cmd,
             turbo_cmd=False):
        op_mode = self.op_modes.get(operating_mode_cmd, self.HYUNDAI_MODE_HEAT)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.HYUNDAI_FAN_AUTO)
        swing_v = self.swing_v_map.get(swing_v_cmd, self.HYUNDAI_VDIR_AUTO)

        temperature = 23
        if 15 < temperature_cmd < 31:
            temperature = temperature_cmd
        if op_mode == self.HYUNDAI_MODE_FAN:
            temperature = 24
            if fan_speed == self.HYUNDAI_FAN_AUTO:
                fan_speed = self.HYUNDAI_FAN2

        power_mode = self.HYUNDAI_POWER_ON if power_mode_cmd == self.POWER_ON else self.HYUNDAI_POWER_OFF

        self.send_hyundai(power_mode, op_mode, fan_speed, temperature, swing_v)

    def send_hyundai(self, power_mode, op_mode, fan_speed, temperature, swing_v):
        send_buffer = bytearray([0x00, 0x00, 0x00, 0x50])
        send_buffer[0] = op_mode | fan_speed | power_mode | swing_v
        send_buffer[1] = temperature - 16

        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for i in range(0, len(send_buffer)):
            self.send_byte(send_buffer[i])

        self.mark()
        self.space(self.ZERO_SPACE)
        self.mark()
        self.space(self.ONE_SPACE)
        self.mark()
        self.space(self.ZERO_SPACE)

        self.mark()
        self.space(0)
