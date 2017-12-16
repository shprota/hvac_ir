from importlib import import_module


class ACProtocol:
    HDR_MARK = 4420
    HDR_SPACE = 4300
    BIT_MARK = 620
    ONE_SPACE = 1560
    ZERO_SPACE = 480
    MSG_SPACE = 5100

    # Commands
    POWER_OFF = 'off'
    POWER_ON = 'on'

    # Operating modes
    MODE_AUTO = 'auto'
    MODE_HEAT = 'heat'
    MODE_COOL = 'cool'
    MODE_DRY = 'dry'
    MODE_FAN = 'fan_only'

    # Fan speeds. Note that some heatpumps have less than 5 fan speeds
    FAN_AUTO = 'auto'
    FAN_1 = 'low'
    FAN_2 = 'medium'
    FAN_3 = 'high'

    # Vertical air directions. Note that these cannot be set on all heat pumps
    VDIR_AUTO = 'auto'
    VDIR_MANUAL = 'manual'
    VDIR_UP = 'up'
    VDIR_MUP = 'middle_up'
    VDIR_MIDDLE = 'middle'
    VDIR_MDOWN = 'middle_down'
    VDIR_DOWN = 'down'
    VDIR_SWING = 'swing'
    VDIR_SWING_UP = 'swing_up'
    VDIR_SWING_MIDDLE = 'swing_middle'
    VDIR_SWING_DOWN = 'swing_down'

    # Horizontal air directions. Note that these cannot be set on all heat pumps
    HDIR_AUTO = 'auto'
    HDIR_MANUAL = 'manual'
    HDIR_MIDDLE = 'middle'
    HDIR_LEFT = 'left'
    HDIR_MLEFT = 'middle_left'
    HDIR_MRIGHT = 'middle_right'
    HDIR_RIGHT = 'right'
    HDIR_WIDE = 'wide'
    HDIR_SWING = 'swing'
    HDIR_SWING_SPREAD = 'swing_spread'

    def __init__(self):
        self.durations = []

    @classmethod
    def is_swing(cls, vdir, hdir=HDIR_AUTO):
        return vdir in [cls.VDIR_SWING, cls.VDIR_SWING_DOWN, cls.VDIR_SWING_MIDDLE, cls.VDIR_SWING_UP] or \
               hdir in [cls.HDIR_SWING, cls.HDIR_SWING_SPREAD]

    def send_byte(self, val):
        for i in range(8):
            self.bit(val)
            val = val >> 1

    def mark(self, duration=-1):
        if duration == -1:
            duration = self.BIT_MARK
        self.durations.append(duration)

    def space(self, duration=-1):
        if duration == -1:
            duration = self.ZERO_SPACE
        self.durations.append(duration)

    def bit(self, val):
        self.durations.append(self.BIT_MARK)
        if val & 0x01:
            self.durations.append(self.ONE_SPACE)
        else:
            self.durations.append(self.ZERO_SPACE)

    @staticmethod
    def bit_reverse(val):
        x = val
        #          01010101  |         10101010
        x = ((x >> 1) & 0x55) | ((x << 1) & 0xaa)
        #          00110011  |         11001100
        x = ((x >> 2) & 0x33) | ((x << 2) & 0xcc)
        #          00001111  |         11110000
        x = ((x >> 4) & 0x0f) | ((x << 4) & 0xf0)
        return x

    def send(self, power_mode_cmd, operating_mode_cmd, fan_speed_cmd, temperature_cmd, swing_v_cmd, swing_h_cmd,
             turbo_mode=False):
        pass


def get_sender(ac_type):
    try:
        return getattr(import_module('hvac_ir.' + ac_type.lower()), ac_type.title())
    except ImportError:
        return None
