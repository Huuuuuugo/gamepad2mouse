# adapted from: https://pastebin.com/8KDYbpaj
# TODO: change 'GamepadControls.list_gamepads()' behaviour from "create list of gamepads" to "update list of gamepads"
#   this will allow it to be called inside of a loop without creating new gamepad and notify objects on every single cycle
#   which, in turn, will allow the thread logic of the notify object to work propperly on this cenario

from __future__ import absolute_import, division
from xinput import XInputJoystick, get_bit_values, XINPUT_GAMEPAD
import ctypes
import threading
import time

# uses the vibration of the controller to notify if something was activated or deactivated
# this class must be instantiated and it's object must be used as a thread
class Notify():
    def __init__(self, gamepad=0):
        self.gamepad = gamepad
        # stores the state of the last succesful call to Notify()
        # it's used to allow notifications of the other state to run above the current one, without waiting for it to finish
        self.last_state = None
        # flag that stores the current state of the thread (running or not running)
        # used in combinaton of 'lock' to avoid cuncurrent calls to the same state of notification
        self.is_running = False
        # lock used when changing the state of the 'is_running' flag
        # used in combinaton of 'is_running' to avoid cuncurrent calls to the same state of notification
        self.lock = threading.Lock()
        # stores the number of the current trhead call
        # used to avoid that a previous thread call changes the state of the 'is_runnig' flag
        self.last_call = 0
       
    def run(self, state: bool):
        # while using the lock:
        with self.lock:
            # check if the current state is different from the last one
            # if it's different, this is a Notify() call of other state, and therefore should run without waiting for the last thread call to finish
            # if it's not different, check if the 'is_running' flag before proceding
            if self.last_state is state:
                if self.is_running:
                    # print("already running!")
                    return
                self.is_running = True

        # update state
        self.last_state = state
        # assign 'current_call' and update 'last_call'
        self.last_call = current_call = self.last_call + 1
        if state:
            # interrupt current thread call if another call was made (ie if it's not the latest call anymore)
            if current_call is not self.last_call:
                # print("state changed!")
                return
            self.gamepad.set_vibration(1,1)
            time.sleep(0.4)
        else:
            # interrupt current thread call if another call was made (ie if it's not the latest call anymore)
            if current_call is not self.last_call:
                # print("state changed!")
                return
            self.gamepad.set_vibration(0.1,1)
            time.sleep(0.9)
        # interrupt current thread call if another call was made (ie if it's not the latest call anymore)
        if current_call is not self.last_call:
            # print("state changed!")
            return
        self.gamepad.set_vibration(0,0)
        time.sleep(1.5)

        # while using the lock
        with self.lock:
            # check if there was still no other calls after this one before trying to change the 'is_running' flag
            if current_call is self.last_call:
                # change the 'is_runing' flag state, to allow the thread to run for same state again
                self.is_running = False
                # print("end of thread!", current_call)
            # else:
            #     print("changed end of thread!", current_call)    

    def __call__(self, state: bool):
        T_notify = threading.Thread(target=self.run, args=(state,), daemon=True)
        T_notify.start()
 

class GamepadControls(XInputJoystick, Notify):
    """Wrapper for the XInputJoystick class to avoid using events."""
    
    def __init__(self, *args, **kwargs):
        try:
            device_number = args[0].device_number
        except (IndexError, AttributeError):
            raise ValueError('use the result from GamepadControls.list_gamepads() to initialize the class')
        super(GamepadControls, self).__init__(device_number, *args[1:], **kwargs)
        self.notify = Notify(args[0])
 
    @classmethod
    def list_gamepads(self):
        """Return a list of gamepad objects."""
        return [self(gamepad) for gamepad in self.enumerate_devices()]
 
    def __enter__(self):
        """Get the current state."""
        self._state = self.get_state()
        return self
 
    def __exit__(self, *args):
        """Record the last state."""
        self._last_state = self._state
    
    def get_axis(self, dead_zone=1024):
        """Return a dictionary of any axis based inputs."""
        result = {}
        axis_fields = dict(XINPUT_GAMEPAD._fields_)
        axis_fields.pop('buttons')
        for axis, type in list(axis_fields.items()):
            old_val = getattr(self._last_state.gamepad, axis)
            new_val = getattr(self._state.gamepad, axis)
            data_size = ctypes.sizeof(type)
            old_val = int(self.translate(old_val, data_size) * 65535)
            new_val = int(self.translate(new_val, data_size) * 65535)
 
            result[axis] = new_val
            
        return result
        
    def get_button(self):
        """Return a dictionary of any button inputs."""
        changed = self._state.gamepad.buttons ^ self._last_state.gamepad.buttons
        changed = get_bit_values(changed, 16)
        buttons_state = get_bit_values(self._state.gamepad.buttons, 16)
        changed.reverse()
        buttons_state.reverse()
        button_numbers = ['dpad_up', 'dpad_down', 'dpad_left', 'dpad_right', 'start', 'select', 'LS', 'RS', 'LB', 'RB', 11, 12, 'A', 'B', 'X', 'Y']
        changed_buttons = list(list(zip(changed, button_numbers, buttons_state)))
        
        result = {}
        for changed, number, pressed in changed_buttons:
            result[number] = pressed
        return result
 

if __name__ == '__main__':
    import time

    gamepads = GamepadControls.list_gamepads()
    while True:
        for gamepad in gamepads:
            with gamepad as gamepad_input:
                buttons = gamepad_input.get_button()
                axis = gamepad_input.get_axis()
                if buttons['select'] and buttons['A']:
                    gamepad_input.notify(True)
                if buttons['select'] and buttons['B']:
                    gamepad_input.notify(False)
                print(f"{buttons}\n{axis}{' '*(132-len(str(axis))) + '\x1b[A\x1b[A\r'}", end='', flush=True)
            time.sleep(1/60)