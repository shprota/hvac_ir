from . import ACProtocol


class Carriermca(ACProtocol):
    #  Carrier (42MCA009515LS) timing constants (remote control P/N R11CG/E)
    HDR_MARK = 4510
    HDR_SPACE = 4470
    BIT_MARK = 600
    ONE_SPACE = 1560
    ZERO_SPACE = 500

    CARRIER_MODE_AUTO = 0x10  # Operating mode
    CARRIER_MODE_COOL = 0x00
    CARRIER_MODE_DRY = 0x20
    CARRIER_MODE_FAN = 0x20
    CARRIER_MODE_HEAT = 0x30
    CARRIER_MODE_OFF = 0x00  # Power OFF
    CARRIER_MODE_ON = 0x20  # Power ON
    CARRIER_FAN_DRY_AUTO = 0x00  # Fan speed, AUTO or DRY modes
    CARRIER_FAN1 = 0x01
    CARRIER_FAN2 = 0x02
    CARRIER_FAN3 = 0x04
    CARRIER_FAN_AUTO = 0x05
    CARRIER_FAN_OFF = 0x06

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
        power_mode = self.CARRIER_MODE_ON
        temperature = 23

        if power_mode_cmd == self.POWER_OFF:
            power_mode = self.CARRIER_MODE_OFF
            op_mode = self.CARRIER_MODE_COOL
            fan_speed = self.CARRIER_FAN_OFF
            temperature = 31
            self.send_carrier(power_mode, op_mode, fan_speed, temperature)
            return

        op_mode = self.op_modes.get(operating_mode_cmd, self.CARRIER_MODE_COOL)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.CARRIER_FAN_AUTO) if op_mode != self.CARRIER_MODE_FAN \
            else self.CARRIER_FAN_AUTO

        if 16 < temperature_cmd < 31 and op_mode != self.CARRIER_MODE_FAN:
            temperature = temperature_cmd

        self.send_carrier(power_mode, op_mode, fan_speed, temperature)

    def send_carrier(self, power_mode, op_mode, fan_speed, temperature):
        send_buffer = bytearray(b'\x4D\xB2\xD8\x00\x00\x00')
        temperatures = [0, 8, 12, 4, 6, 14, 10, 2, 3, 11, 9, 1, 5, 13, 7]
        send_buffer[2] = send_buffer[2] | power_mode | fan_speed
        send_buffer[4] = send_buffer[4] | op_mode | temperatures[temperature - 17]
        send_buffer[3] = ~send_buffer[2] & 0xff
        send_buffer[5] = ~send_buffer[4] & 0xff

        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for b in send_buffer:
            self.send_byte(b)

        self.mark()
        self.space(self.HDR_SPACE)
        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for b in send_buffer:
            self.send_byte(b)

        self.mark()
        self.space(0)
