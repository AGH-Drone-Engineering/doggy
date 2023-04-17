from doggy import Doggy, DoggyAction
import time


def spin():
    print('Connecting to Doggy...')
    doggy = Doggy()
    print('Changing mode...')
    doggy.send_action(DoggyAction.WALK)
    try:
        print('Spin!')
        print('Press Ctrl+C to stop')
        while True:
            doggy.send_stick(0, 0, 0.3, 0)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('Stop')
        for _ in range(10):
            doggy.send_stick(0, 0, 0, 0)
            time.sleep(0.1)
