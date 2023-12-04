import utils

state = 'inactive'
config = utils.get_config()
is_button_pressed = None
prev_is_button_pressed = None
unsaved_networks = []

if config['mode'] == 'active':
    saved_inside_networks_by_id = utils.get_saved_inside_networks_by_id()
    saved_outside_networks_by_id = utils.get_saved_outside_networks_by_id()
    utils.set_led_color_for_active_mode(state)
elif config['mode'] == 'passive':
    utils.set_led_color_for_passive_mode(state)
    
while True:
    prev_is_button_pressed = is_button_pressed
    is_button_pressed = utils.is_button_pressed()
    
    if not prev_is_button_pressed and is_button_pressed:
        if state == 'active':
            state = 'inactive'
        elif state == 'inactive':
            state = 'active'
        
        if config['mode'] == 'active':
            if state == 'inactive':
                utils.set_led_color_for_active_mode(state)
        elif config['mode'] == 'passive':
            utils.set_led_color_for_passive_mode(state)
    
    if config['mode'] == 'active':
        if state == 'active':
            current_networks = utils.scan_networks()
            is_inside = utils.do_networks_match_using_naive_algorithm(current_networks, saved_inside_networks_by_id)
            is_outside = utils.do_networks_match_using_naive_algorithm(current_networks, saved_outside_networks_by_id)
            utils.set_led_color_for_active_mode(state, is_inside, is_outside)
    elif config['mode'] == 'passive':
        if state == 'active':
            networks = utils.scan_networks()
            utils.save_networks(networks)
