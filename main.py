import utils

state = 'inactive'
config = utils.get_config()
is_button_pressed = None
prev_is_button_pressed = None
unsaved_networks = []

utils.set_led_color_by_state(state)

while True:
    prev_is_button_pressed = is_button_pressed
    is_button_pressed = utils.is_button_pressed()
    
    if is_button_pressed and not prev_is_button_pressed:
        if state == 'active':
            state = 'inactive'
        elif state == 'inactive':
            state = 'active'
    
    utils.set_led_color_by_state(state)
    
    if state == 'active':
        if config['mode'] == 'active':
            pass
        elif config['mode'] == 'passive':
            networks = utils.scan_networks()
            utils.save_networks(networks)
            


    