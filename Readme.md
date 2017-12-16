# hvac-ir

This is a python port of the great [Arduino heapumpir library](https://github.com/ToniA/arduino-heatpumpir) by ToniA

Currently supported devices:

* Midea (Electra, etc.)
* Gree (Tadiran, Hyunday, etc.) YAG1FB remote (others may also work)

## Example usage:

```python
import hvac_ir

Sender = hvac_ir.get_sender('gree')
if Sender is None:
    print("Unknown sender")
    exit(2)
my_ac = Sender()
my_ac.send(Sender.POWER_OFF, Sender.MODE_HEAT, Sender.FAN_AUTO, 24, Sender.VDIR_SWING_DOWN,
       Sender.HDIR_SWING, False)
durations = my_ac.durations
```
