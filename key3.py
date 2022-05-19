import sys, tty, os, termios, signal

from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

MOVE_KEYS = [['a', 'd'], ['s', 'w']]
PINS = [22, 17]
MOVE_SIZE = 10
HOST='192.168.1.28'

move_size = MOVE_SIZE * 2/180

def main():
    # save old stdin setting to restore
    stdin_old = termios.tcgetattr(sys.stdin)

    # graceful quit function for sigint and sigterm using signal module
    def restore_quit(sig=None, frame=None):
        #reset settings, clean-up, close factory
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, stdin_old)
        os.system('stty sane')
        print('keyboard control relinquished')
        factory.close()
        print('servos and GPIO factory closed')
        quit()

    # signal catchers
    signal.signal(signal.SIGTERM, restore_quit)
    signal.signal(signal.SIGINT, restore_quit)

    # change file descriptor setting to cbreak
    # allows it to read each individual key press without return
    tty.setcbreak(sys.stdin.fileno())
    # open factory and open servos
    factory = PiGPIOFactory(host=HOST)
    servos = []
    for pin in PINS:
        servo = Servo(
            pin,
            pin_factory=factory,
            #min_pulse_width=.001,
            #max_pulse_width=.002,
            initial_value=0
        )

        servos.append(servo)
    try:
        while True:
            # read/decode 3 bytes of stdin
            pushed_key = os.read(sys.stdin.fileno(), 3).decode()
            # change special keys to more easily readable names
            pushed_key = special_key_name_converter(pushed_key)

            if pushed_key == 'esc':
                break
            else:
                for i, move_keys in enumerate(MOVE_KEYS):
                    servo = servos[i]
                    for j, mk in enumerate(move_keys):
                        if pushed_key == mk:
                            move = (-1)**j * move_size
                            servo.value = servo_saver(servo, move)

        # change keyboard settings back
    except Exception as exc:
        print("ERROR: ", exc)

    finally:
        restore_quit()



def special_key_name_converter(b):

    k = ord(b[-1])
    special_keys = {
        127: 'backspace',
        10: 'return',
        32: 'space',
        9: 'tab',
        27: 'esc',
        65: 'up',
        66: 'down',
        67: 'right',
        68: 'left'
    }
    return special_keys.get(k, chr(k))

def servo_saver(servo, move, i=""):
    value = servo.value
    new_value = servo.value + move
    if 1 > new_value > -1:
        return new_value
    elif 1 < new_value:
        print("Servo {0} is {1}".format(i, 1))
        return 1.
    else:
        print("Servo {0} is {1}".format(i, -1))
        return -1.



if __name__=='__main__':
    main()

