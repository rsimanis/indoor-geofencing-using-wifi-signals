import utils

state = 'inactive'
config = utils.get_config()
mode = config['mode']
is_button_pressed = None
prev_is_button_pressed = None
unsaved_networks = []

if mode == 'active' or mode == 'test':
    saved_networks = utils.get_saved_networks()
utils.set_led_color_by_mode_and_state(mode, state)
    
while True:
    prev_is_button_pressed = is_button_pressed
    is_button_pressed = utils.is_button_pressed()
    
    if not prev_is_button_pressed and is_button_pressed:
        if state == 'active':
            state = 'inactive'
            print('State was changed to INACTIVE')
        elif state == 'inactive':
            state = 'active'
            print('State was changed to ACTIVE')
        utils.set_led_color_by_mode_and_state(mode, state)
    
    if mode == 'active':
        if state == 'active':
            current_networks = utils.scan_networks()
            [is_inside, is_outside] = utils.match_using_active_algorithm(current_networks, saved_networks)
            utils.set_led_color_for_active_mode(state, is_inside, is_outside)
    elif mode == 'passive':
        if state == 'active':
            networks = utils.scan_networks()
            utils.save_networks(networks)
    elif mode == 'test':
        if state == 'active':
            current_networks = utils.scan_networks()
            [is_inside, is_outside] = utils.match_using_active_algorithm(current_networks, saved_networks)
            utils.save_test_data(is_inside, is_outside)

