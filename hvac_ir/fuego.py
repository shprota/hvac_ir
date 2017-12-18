from . import ACProtocol


class Fuego(ACProtocol):
    # Fuego timing constants
    HDR_MARK = 3600
    HDR_SPACE = 1630
    BIT_MARK = 420
    ONE_SPACE = 1380
    ZERO_SPACE = 420

    # Fuego codes
    FUEGO_MODE_AUTO = 0x08  # Operating mode
    FUEGO_MODE_HEAT = 0x01
    FUEGO_MODE_COOL = 0x03
    FUEGO_MODE_DRY = 0x02
    FUEGO_MODE_FAN = 0x07
    FUEGO_MODE_ON = 0x04  # Power ON
    FUEGO_MODE_OFF = 0x00
    FUEGO_FAN_AUTO = 0x00  # Fan speed
    FUEGO_FAN1 = 0x02
    FUEGO_FAN2 = 0x03
    FUEGO_FAN3 = 0x05

    FUEGO_VS_AUTO = 0x00  # Vertical swing
    FUEGO_VS_UP = 0x08
    FUEGO_VS_MUP = 0x10
    FUEGO_VS_MIDDLE = 0x18
    FUEGO_VS_MDOWN = 0x20
    FUEGO_VS_DOWN = 0x28
    FUEGO_VS_SWING = 0x38

    op_modes = {
        ACProtocol.MODE_AUTO: FUEGO_MODE_AUTO,
        ACProtocol.MODE_HEAT: FUEGO_MODE_HEAT,
        ACProtocol.MODE_COOL: FUEGO_MODE_COOL,
        ACProtocol.MODE_DRY: FUEGO_MODE_DRY,
        ACProtocol.MODE_FAN: FUEGO_MODE_FAN,
    }

    fan_speeds = {
        ACProtocol.FAN_AUTO: FUEGO_FAN_AUTO,
        ACProtocol.FAN_1: FUEGO_FAN1,
        ACProtocol.FAN_2: FUEGO_FAN2,
        ACProtocol.FAN_3: FUEGO_FAN3,
    }
    
    swing_v_map = {
        ACProtocol.VDIR_AUTO: FUEGO_VS_AUTO,
        ACProtocol.VDIR_UP: FUEGO_VS_UP,
        ACProtocol.VDIR_MUP: FUEGO_VS_MUP,
        ACProtocol.VDIR_MIDDLE: FUEGO_VS_MIDDLE,
        ACProtocol.VDIR_MDOWN: FUEGO_VS_MDOWN,
        ACProtocol.VDIR_DOWN: FUEGO_VS_DOWN,
        ACProtocol.VDIR_SWING: FUEGO_VS_SWING,
    }

    def send(self, power_mode_cmd, operating_mode_cmd, fan_speed_cmd, temperature_cmd, swing_v_cmd, swing_h_cmd,
             turbo_cmd=False):
        power_mode = self.FUEGO_MODE_ON
        temperature = 23
        swing_v = self.FUEGO_VS_SWING

        if power_mode_cmd == self.POWER_OFF:
            power_mode = self.FUEGO_MODE_OFF
            swing_v = self.FUEGO_VS_MUP

        op_mode = self.op_modes.get(operating_mode_cmd, self.FUEGO_MODE_HEAT)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.FUEGO_FAN_AUTO)
        swing_v = self.swing_v_map.get(swing_v_cmd, swing_v)
        if 17 < temperature_cmd < 32:
            temperature = temperature_cmd
        self.send_fuego(power_mode, op_mode, fan_speed, temperature, swing_v)

    def send_fuego(self, power_mode, op_mode, fan_speed, temperature, swing_v):
        send_buffer = bytearray([0x23, 0xCB, 0x26, 0x01, 0x80, 0x20, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
                                 # 0     1     2     3     4     5     6     7     8     9    10    11    12    13
        send_buffer[5] = send_buffer[5] | power_mode
        send_buffer[6] = send_buffer[6] | op_mode
        send_buffer[7] = send_buffer[7] | (31 - temperature)
        send_buffer[8] = send_buffer[8] | fan_speed | swing_v
        checksum = 0
        for i in range(0, len(send_buffer) - 1):
            checksum = (checksum + send_buffer[i]) & 0xff
        send_buffer[13] = checksum

        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)

        for i in range(0, len(send_buffer)):
            self.send_byte(send_buffer[i])

        self.mark()
        self.space(0)




