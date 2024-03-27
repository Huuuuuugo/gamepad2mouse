import pynput


keyboard = pynput.keyboard.Controller()
mouse = pynput.mouse.Controller()

class pynput_utils(object):
    def __init__(self) -> None:
        self.cache = [{'id': None, 'toggle': None}]

    def mouse_touch(self, button:int, is_pressed:bool, id:int = 0):
        found = False
        toggle = bool(is_pressed)
        unique_id = str(button) + str(id)
        for i, entry in enumerate(self.cache):
            if entry['id'] == unique_id:
                toggle = entry['toggle']
                found = True
                break
        if not found:
            entry = {'id': unique_id, 'toggle': bool(is_pressed)}
            self.cache.append(entry)

        if bool(toggle) != bool(is_pressed):
            if is_pressed:
                mouse.press(button)
            else:
                mouse.release(button)
            self.cache[i]['toggle'] = bool(is_pressed)
    

    def key_touch(self, key:int, is_pressed:bool, id:int = 0):
        found = False
        toggle = bool(is_pressed)
        unique_id = str(key) + str(id)
        for i, entry in enumerate(self.cache):
            if entry['id'] == unique_id:
                toggle = entry['toggle']
                found = True
                break
        if not found:
            entry = {'id': unique_id, 'toggle': bool(is_pressed)}
            self.cache.append(entry)

        if toggle != bool(is_pressed):
            if is_pressed:
                keyboard.press(key)
            else:
                keyboard.release(key)
            self.cache[i]['toggle'] = bool(is_pressed)