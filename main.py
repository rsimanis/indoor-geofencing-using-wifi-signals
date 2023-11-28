import utils

config = utils.get_config()

while True:
    if config['mode'] == 'active':
        pass
    elif config['mode'] == 'passive':
        if (utils.is_button_pressed()):
            utils.set_led_color(255, 0, 0)
        else:
            utils.set_led_color(0, 255, 0)


    