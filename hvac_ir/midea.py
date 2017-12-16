from . import ACProtocol


class Midea(ACProtocol):
    # Midea timing constants
    HDR_MARK = 4420
    HDR_SPACE = 4300
    BIT_MARK = 620
    ONE_SPACE = 1560
    ZERO_SPACE = 480
    MSG_SPACE = 5100

    # MIDEA codes

    MIDEA_AIRCON1_MODE_AUTO = 0x10  # Operating mode
    MIDEA_AIRCON1_MODE_HEAT = 0x30
    MIDEA_AIRCON1_MODE_COOL = 0x00
    MIDEA_AIRCON1_MODE_DRY = 0x20
    MIDEA_AIRCON1_MODE_FAN = 0x60
    MIDEA_AIRCON1_MODE_FP = 0x70  # Not a real mode...
    MIDEA_AIRCON1_MODE_OFF = 0xFE  # Power OFF - not real codes, but we need something...
    MIDEA_AIRCON1_MODE_ON = 0xFF  # Power ON
    MIDEA_AIRCON1_FAN_AUTO = 0x02  # Fan speed
    MIDEA_AIRCON1_FAN1 = 0x06
    MIDEA_AIRCON1_FAN2 = 0x05
    MIDEA_AIRCON1_FAN3 = 0x03

    temperatures = [0, 8, 12, 4, 6, 14, 10, 2, 3, 11, 9, 1, 5, 13]

    op_modes = {
        ACProtocol.MODE_AUTO: MIDEA_AIRCON1_MODE_AUTO,
        ACProtocol.MODE_HEAT: MIDEA_AIRCON1_MODE_HEAT,
        ACProtocol.MODE_COOL: MIDEA_AIRCON1_MODE_COOL,
        ACProtocol.MODE_DRY: MIDEA_AIRCON1_MODE_DRY,
        ACProtocol.MODE_FAN: MIDEA_AIRCON1_MODE_FAN,
    }

    fan_speeds = {
        ACProtocol.FAN_AUTO: MIDEA_AIRCON1_FAN_AUTO,
        ACProtocol.FAN_1: MIDEA_AIRCON1_FAN1,
        ACProtocol.FAN_2: MIDEA_AIRCON1_FAN2,
        ACProtocol.FAN_3: MIDEA_AIRCON1_FAN3,
    }

    def __init__(self):
        ACProtocol.__init__(self)

    # noinspection PyUnusedLocal
    def send(self, power_mode_cmd, operating_mode_cmd, fan_speed_cmd, temperature_cmd, swing_v_cmd, swing_h_cmd,
             turbo_cmd=False):
        operating_mode = self.MIDEA_AIRCON1_MODE_OFF if power_mode_cmd == self.POWER_OFF \
            else self.op_modes.get(operating_mode_cmd, self.MIDEA_AIRCON1_MODE_HEAT)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.MIDEA_AIRCON1_FAN_AUTO)
        temperature = 23
        if 16 < temperature_cmd < 31:
            temperature = self.temperatures[(temperature - 17)]
        self.send_midea(operating_mode, fan_speed, temperature)

    def send_midea(self, operating_mode, fan_speed, temperature):
        send_buffer = bytearray(b'\x4d\xde\x07')  # Turn OFF default value
        if operating_mode != self.MIDEA_AIRCON1_MODE_OFF:
            send_buffer[1] = ~fan_speed & 0xFF
            if operating_mode == self.MIDEA_AIRCON1_MODE_FAN:
                send_buffer[2] = self.MIDEA_AIRCON1_MODE_DRY | 0x07
            else:
                send_buffer[2] = operating_mode | self.temperatures[(temperature - 17)]
        return self.send_midea_raw(send_buffer)

    def send_midea_raw(self, send_buffer):

        self.durations.extend([self.HDR_MARK, self.HDR_SPACE, ])
        for i in range(3):
            self.send_byte(send_buffer[i])
            self.send_byte(~send_buffer[i])
        self.mark()
        self.space(self.MSG_SPACE)
        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for i in range(3):
            self.send_byte(send_buffer[i])
            self.send_byte(~send_buffer[i])
        self.mark()
        self.space(0)
