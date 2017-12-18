from . import ACProtocol


class Ballu(ACProtocol):
    HDR_MARK = 9300  
    HDR_SPACE = 4550  
    BIT_MARK = 500   
    ZERO_SPACE = 500   
    ONE_SPACE = 1650  
    MSG_SPACE = 0     

    # BALLU codes
    BALLU_AIRCON_MODE_HEAT = 0x00
    BALLU_AIRCON_MODE_COOL = 0x02
    BALLU_AIRCON_MODE_DRY = 0x03
    BALLU_AIRCON_MODE_FAN = 0x04

    BALLU_AIRCON_MODE_OFF = 0x04 
    BALLU_AIRCON_MODE_ON = 0x00

    BALLU_AIRCON_FAN_AUTO = 0x00 
    BALLU_AIRCON_FAN1 = 0x01 
    BALLU_AIRCON_FAN2 = 0x02
    BALLU_AIRCON_FAN3 = 0x03 

    op_modes = {
        ACProtocol.MODE_HEAT: BALLU_AIRCON_MODE_HEAT,
        ACProtocol.MODE_COOL: BALLU_AIRCON_MODE_COOL,
        ACProtocol.MODE_DRY: BALLU_AIRCON_MODE_DRY,
        ACProtocol.MODE_FAN: BALLU_AIRCON_MODE_FAN,
    }
    
    fan_speeds = {
        ACProtocol.FAN_AUTO: BALLU_AIRCON_FAN_AUTO,
        ACProtocol.FAN_1: BALLU_AIRCON_FAN1,
        ACProtocol.FAN_2: BALLU_AIRCON_FAN2,
        ACProtocol.FAN_3: BALLU_AIRCON_FAN3,
    }

    def __init__(self):
        ACProtocol.__init__(self)

    @classmethod
    def list_modes(cls):
        return list(cls.op_modes)

    @classmethod
    def list_fan_speeds(cls):
        return list(cls.fan_speeds)

    # noinspection PyUnusedLocal
    def send(self, power_mode_cmd, operating_mode_cmd, fan_speed_cmd, temperature_cmd, swing_v_cmd, swing_h_cmd,
             turbo_cmd=False):
        power_mode = self.BALLU_AIRCON_MODE_OFF if power_mode_cmd == self.POWER_OFF else self.BALLU_AIRCON_MODE_ON
        operating_mode = self.op_modes.get(operating_mode_cmd, self.BALLU_AIRCON_MODE_COOL)
        fan_speed = self.fan_speeds.get(fan_speed_cmd, self.BALLU_AIRCON_FAN_AUTO)
        temperature = 8
        if 15 < temperature_cmd < 31:
            temperature = temperature_cmd - 16
        self.durations = []
        self.send_ballu(power_mode, operating_mode, fan_speed, temperature)

    def send_ballu(self, power_mode,operating_mode, fan_speed, temperature):
        send_buffer = bytearray(b'\x83\x06\x04\x42\x00\x00')
        send_buffer[2] = power_mode if power_mode == self.BALLU_AIRCON_MODE_OFF else fan_speed
        send_buffer[3] = (temperature << 4) | operating_mode

        self.durations.extend([self.HDR_MARK, self.HDR_SPACE, ])
        for i in range(len(send_buffer)):
            self.send_byte(send_buffer[i])
        self.mark()
        self.space(0)
