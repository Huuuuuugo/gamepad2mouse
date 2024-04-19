import xinput_wrapper as xinput
import pynput
import time
from pynput_utils import pynput_utils


keyboard = pynput.keyboard.Controller()
key = pynput.keyboard.Key
mouse = pynput.mouse.Controller()
mouse_btns = pynput.mouse.Button
io = pynput_utils()

gamepad_axis = {
    'l_thumb_x':0,
    'l_thumb_y':0,
    'r_thumb_x':0,
    'r_thumb_y':0,
    'right_trigger':0,
}
gamepad_btns = {}
on_off_switch = 1
toggle_wait = 1


while True:
    gamepads = xinput.GamepadControls.list_gamepads()
    if len(gamepads) < 1:
        time.sleep(2)
        continue
    while True:
        with gamepads[0] as gamepad:
            # get gamepad states
            try:
                gamepad_axis.update(gamepad.get_axis())
                gamepad_btns.update(gamepad.get_button())
            except AttributeError:
                break

            if gamepad_btns[6] and toggle_wait:
                if gamepad_btns[8]:
                    on_off_switch = 1 - on_off_switch
                    toggle_wait = 0
                io.key_touch(key.media_volume_up, gamepad_btns[1])
                io.key_touch(key.media_volume_down, gamepad_btns[2])
            elif gamepad_btns[6] == toggle_wait:
                toggle_wait = 1

            if on_off_switch and not gamepad_btns[6]:
                # get mouse movement percentage and move pointer
                if gamepad_axis['l_thumb_x'] < 0:
                    x_speed = -min(((gamepad_axis['l_thumb_x']/32767)**2), 0.5)
                else:
                    x_speed = min(((gamepad_axis['l_thumb_x']/32767)**2), 0.5)

                if gamepad_axis['l_thumb_y'] < 0:
                    y_speed = min(((gamepad_axis['l_thumb_y']/32767)**2), 0.5)
                else:
                    y_speed = -min(((gamepad_axis['l_thumb_y']/32767)**2), 0.5)
                mouse.move(x_speed*30, y_speed*30)


                # scroll
                if gamepad_axis['r_thumb_x'] < 0:
                    scroll_x_speed = -(gamepad_axis['r_thumb_x']/32767)**2
                else:
                    scroll_x_speed = (gamepad_axis['r_thumb_x']/32767)**2

                if gamepad_axis['r_thumb_y'] < 0:
                    scroll_y_speed = -(gamepad_axis['r_thumb_y']/32767)**2
                else:
                    scroll_y_speed = (gamepad_axis['r_thumb_y']/32767)**2
                mouse.scroll(scroll_x_speed/2, scroll_y_speed/2)


                # send mouse button presses
                io.mouse_touch(mouse_btns.left, gamepad_btns[10])
                io.mouse_touch(mouse_btns.right, gamepad_axis['right_trigger'])


                # send keyboard input
                io.key_touch(key.up, gamepad_btns[1])
                io.key_touch(key.down, gamepad_btns[2])
                io.key_touch(key.left, gamepad_btns[3])
                io.key_touch(key.right, gamepad_btns[4])
                io.key_touch('k', gamepad_btns[5])
                

                # print(math.sqrt(gamepad_axis['l_thumb_x']**2 + gamepad_axis['l_thumb_y']**2)/34000)
                # print(x_speed, y_speed)
                # print(gamepad_btns)
            time.sleep(1/60)