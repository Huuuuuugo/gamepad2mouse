import xinput_wrapper as xinput
import pynput
import time
import math


keyboard = pynput.keyboard.Controller()
mouse = pynput.mouse.Controller()
mouse_btns = pynput.mouse.Button

def mouse_touch(button:int, is_pressed:bool):
    if is_pressed:
        mouse.press(button)
    else:
        mouse.release(button)

# x: -32768 32767
gamepads = xinput.GamepadControls.list_gamepads()
gamepad_axis = {
    'l_thumb_x':0,
    'l_thumb_y':0,
    'r_thumb_x':0,
    'r_thumb_y':0,
    'right_trigger':0,
}
gamepad_btns = {}
a = 0
l_click_wait = 0
r_click_wait = 0

while True:
    with gamepads[0] as gamepad:
        # get gamepad states
        gamepad_axis.update(gamepad.get_axis())
        gamepad_btns.update(gamepad.get_button())


        # get mouse movement percentage and move pointer
        if gamepad_axis['l_thumb_x'] < 0:
            x_speed = -min(((gamepad_axis['l_thumb_x']/32767)**2), 0.5)
        else:
            x_speed = min(((gamepad_axis['l_thumb_x']/32767)**2), 0.5)

        if gamepad_axis['l_thumb_y'] < 0:
            y_speed = min(((gamepad_axis['l_thumb_y']/32767)**2), 0.5)
        else:
            y_speed = -min(((gamepad_axis['l_thumb_y']/32767)**2), 0.5)
        mouse.move(x_speed*40, y_speed*40)


        # send mouse button presses
        if gamepad_btns[10] != l_click_wait:
            mouse_touch(mouse_btns.left, gamepad_btns[10])
            l_click_wait = 1 - l_click_wait

        if bool(gamepad_axis['right_trigger']) != bool(r_click_wait):
            mouse_touch(mouse_btns.right, bool(gamepad_axis['right_trigger']))
            r_click_wait = 1 - r_click_wait


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


        print(math.sqrt(gamepad_axis['l_thumb_x']**2 + gamepad_axis['l_thumb_y']**2)/34000)
        # print(x_speed, y_speed)
        # print(gamepad_btns)
        time.sleep(1/60)