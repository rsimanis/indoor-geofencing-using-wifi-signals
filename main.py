import utils

config = utils.get_config()
is_button_pressed = None
prev_is_button_pressed = None
is_button_active = False

utils.set_led_color_by_active(is_button_active)

while True:
    prev_is_button_pressed = is_button_pressed
    is_button_pressed = utils.is_button_pressed()
    if is_button_pressed and not prev_is_button_pressed:
        is_button_active = not is_button_active
        utils.set_led_color_by_active(is_button_active)
    if config['mode'] == 'active':
        pass
    elif config['mode'] == 'passive':
        pass


    