import broadlink
# import argparse
# import time
import binascii
# import sys
from . import ACProtocol
import logging

_LOGGER = logging.getLogger(__name__)


class Gree(ACProtocol):
    HDR_MARK = 9000
    HDR_SPACE = 4000
    BIT_MARK = 620
    ONE_SPACE = 1600
    ZERO_SPACE = 540
    MSG_SPACE = 19000

    GREE_POWER_OFF = 0x00
    GREE_POWER_ON = 0x08

    # Operating modes
    GREE_MODE_AUTO = 0x00
    GREE_MODE_HEAT = 0x04
    GREE_MODE_COOL = 0x01
    GREE_MODE_DRY = 0x02
    GREE_MODE_FAN = 0x03

    # Fan speeds
    GREE_FAN_AUTO = 0x00
    GREE_FAN1 = 0x10
    GREE_FAN2 = 0x20
    GREE_FAN3 = 0x30

    # Only  available on YAN Vertical air directions
    GREE_VDIR_AUTO = 0x00
    GREE_VDIR_MANUAL = 0x00
    GREE_VDIR_SWING = 0x01
    GREE_VDIR_SWING_UP = 0xB
    GREE_VDIR_SWING_MIDDLE = 0x9
    GREE_VDIR_SWING_DOWN = 0x7
    GREE_VDIR_UP = 0x02
    GREE_VDIR_MUP = 0x03
    GREE_VDIR_MIDDLE = 0x04
    GREE_VDIR_MDOWN = 0x05
    GREE_VDIR_DOWN = 0x06

    GREE_HDIR_AUTO = 0
    GREE_HDIR_LEFT = 0x20
    GREE_HDIR_MLEFT = 0x30
    GREE_HDIR_MIDDLE = 0x40
    GREE_HDIR_MRIGHT = 0x50
    GREE_HDIR_RIGHT = 0x60
    GREE_HDIR_WIDE = 0xC0
    GREE_HDIR_SWING = 0x10
    GREE_HDIR_SWING_SPREAD = 0xD0
    MODEL = False

    op_modes = {
        ACProtocol.MODE_AUTO: GREE_MODE_AUTO,
        ACProtocol.MODE_HEAT: GREE_MODE_HEAT,
        ACProtocol.MODE_COOL: GREE_MODE_COOL,
        ACProtocol.MODE_DRY: GREE_MODE_DRY,
        ACProtocol.MODE_FAN: GREE_MODE_FAN,
    }

    fan_speeds = {
        ACProtocol.FAN_AUTO: GREE_FAN_AUTO,
        ACProtocol.FAN_1: GREE_FAN1,
        ACProtocol.FAN_2: GREE_FAN2,
        ACProtocol.FAN_3: GREE_FAN3,
    }

    swing_v_map = {
        ACProtocol.VDIR_AUTO: GREE_VDIR_AUTO,
        ACProtocol.VDIR_MANUAL: GREE_VDIR_MANUAL,
        ACProtocol.VDIR_UP: GREE_VDIR_UP,
        ACProtocol.VDIR_MUP: GREE_VDIR_MUP,
        ACProtocol.VDIR_MIDDLE: GREE_VDIR_MIDDLE,
        ACProtocol.VDIR_MDOWN: GREE_VDIR_MDOWN,
        ACProtocol.VDIR_DOWN: GREE_VDIR_DOWN,
        ACProtocol.VDIR_SWING: GREE_VDIR_SWING,
        ACProtocol.VDIR_SWING_UP: GREE_VDIR_SWING_UP,
        ACProtocol.VDIR_SWING_MIDDLE: GREE_VDIR_SWING_MIDDLE,
        ACProtocol.VDIR_SWING_DOWN: GREE_VDIR_SWING_DOWN,
    }

    swing_h_map = {
        ACProtocol.HDIR_AUTO: GREE_HDIR_AUTO,
        ACProtocol.HDIR_MANUAL: GREE_HDIR_AUTO,
        ACProtocol.HDIR_MIDDLE: GREE_HDIR_MIDDLE,
        ACProtocol.HDIR_LEFT: GREE_HDIR_LEFT,
        ACProtocol.HDIR_MLEFT: GREE_HDIR_MLEFT,
        ACProtocol.HDIR_MRIGHT: GREE_HDIR_MRIGHT,
        ACProtocol.HDIR_RIGHT: GREE_HDIR_RIGHT,
        ACProtocol.HDIR_WIDE: GREE_HDIR_WIDE,
        ACProtocol.HDIR_SWING: GREE_HDIR_SWING,
        ACProtocol.HDIR_SWING_SPREAD: GREE_HDIR_SWING_SPREAD,
    }

    def __init__(self):
        ACProtocol.__init__(self)

    @classmethod
    def list_modes(cls):
        return list(cls.op_modes)

    @classmethod
    def list_fan_speeds(cls):
        return list(cls.fan_speeds)

    @classmethod
    def list_swing_modes(cls):
        return list(cls.swing_v_map)

    def send(self, power_mode_cmd, operating_mode_cmd, fan_speed_cmd, temperature_cmd, swing_v_cmd, swing_h_cmd,
             turbo_mode=False):
        power_mode = self.GREE_POWER_ON if power_mode_cmd == self.POWER_ON else self.GREE_POWER_OFF
        operating_mode = self.op_modes.get(operating_mode_cmd, self.GREE_MODE_HEAT)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.GREE_FAN_AUTO)
        swing = self.is_swing(swing_v_cmd, swing_h_cmd)
        swing_v = self.swing_v_map.get(swing_v_cmd, self.GREE_VDIR_AUTO)
        swing_h = self.swing_h_map.get(swing_h_cmd, self.GREE_HDIR_AUTO)
        temperature = 23
        if 15 < temperature_cmd < 31:
            temperature = temperature_cmd - 16
        self.durations = []
        self.send_gree(power_mode, operating_mode, fan_speed, temperature, swing, swing_v, swing_h,
                       turbo_mode)

    @staticmethod
    def make_data(power_mode, operating_mode, fan_speed, temperature, swing, swing_v, swing_h, turbo_mode=False):
        data = bytearray(8)
        swing_flag = 0x40 if swing else 0

        data[0] = fan_speed | operating_mode | power_mode | swing_flag
        data[1] = temperature
        data[2] = 0x70 if turbo_mode else 0x60
        data[3] = 0x50
        data[4] = swing_v | swing_h
        data[5] = 0x40
        data[6] = 0
        data[7] = (((data[0] & 0x0F) +
                    (data[1] & 0x0F) +
                    (data[2] & 0x0F) +
                    (data[3] & 0x0F) +
                    ((data[4] & 0xF0) >> 4) +
                    ((data[5] & 0xF0) >> 4) +
                    ((data[6] & 0xF0) >> 4) +
                    0x0A) & 0x0F) << 4
        return data

    def send_gree(self, power_mode, operating_mode, fan_speed, temperature, swing, swing_v, swing_h, turbo_mode=False):
        data = self.make_data(power_mode, operating_mode, fan_speed, temperature, swing, swing_v, swing_h, turbo_mode)

        self.send_train(data)

        data[3] = 0x70
        data[4] = 0
        data[5] = 0
        data[6] = 0
        data[7] = (((data[0] & 0x0F) +
                    (data[1] & 0x0F) +
                    (data[2] & 0x0F) +
                    (data[3] & 0x0F) +
                    ((data[4] & 0xF0) >> 4) +
                    ((data[5] & 0xF0) >> 4) +
                    ((data[6] & 0xF0) >> 4) +
                    0x0A) & 0x0F) << 4

        self.send_train(data)

    def send_train(self, data):
        for c in data:
            _LOGGER.debug("%02x" % c)
        self.mark(self.HDR_MARK)
        self.space(self.HDR_SPACE)
        for i in range(4):
            self.send_byte(data[i])
        # send what's left of byte 4
        self.bit(0)
        self.bit(1)
        self.bit(0)
        self.mark()
        self.space(self.MSG_SPACE)
        for i in range(4, 8):
            self.send_byte(data[i])
        self.mark()
        self.space(self.MSG_SPACE)
