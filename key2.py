import sys, tty, os, termios, signal

def main():
    # save old stdin setting to restore
    stdin_old = termios.tcgetattr(sys.stdin)

    # graceful quit function for sigint and sigterm using signal module
    def restore_quit(sig=None, frame=None):
        #reset settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, stdin_old)
        os.system('stty sane')
        print('keyboard control relinquished')
        quit()

    # signal catchers
    signal.signal(signal.SIGTERM, restore_quit)
    signal.signal(signal.SIGINT, restore_quit)

    # change file descriptor setting to cbreak
    # allows it to read each individual key press without return
    tty.setcbreak(sys.stdin.fileno())

    while True:
        # read/decode 3 bytes of stdin
        raw_key = os.read(sys.stdin.fileno(), 3).decode()
        # change special keys to more easily readable names
        key = special_key_name_converter(raw_key)

        if key == 'esc':
            break
        else:
            print(raw_key)

    # change keyboard settings back
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


if __name__=='__main__':
    main()

