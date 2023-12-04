import utils

state = 'inactive'
config = utils.get_config()
is_button_pressed = None
prev_is_button_pressed = None
unsaved_networks = []

if config['mode'] == 'active':
    saved_inside_networks_by_id = utils.get_saved_inside_networks_by_id(True)
    saved_outside_networks_by_id = utils.get_saved_outside_networks_by_id(True)
    utils.set_led_color_for_active_mode(state)
elif config['mode'] == 'passive':
    utils.set_led_color_for_passive_mode(state)
    
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
        
        if config['mode'] == 'active':
            utils.set_led_color_for_active_mode(state)
        elif config['mode'] == 'passive':
            utils.set_led_color_for_passive_mode(state)
    
    if config['mode'] == 'active':
        if state == 'active':
            current_networks = utils.scan_networks()
            inside_matching_data = utils.get_network_matching_data_using_naive_algorithm(current_networks, saved_inside_networks_by_id, True)
            outside_matching_data = utils.get_network_matching_data_using_naive_algorithm(current_networks, saved_outside_networks_by_id, False)
            is_inside = is_outside = False
            if inside_matching_data['total_matches'] > outside_matching_data['total_matches']:
                is_inside = True
            elif inside_matching_data['total_matches'] < outside_matching_data['total_matches']:
                is_outside = True
            utils.set_led_color_for_active_mode(state, is_inside, is_outside)
    elif config['mode'] == 'passive':
        if state == 'active':
            networks = utils.scan_networks()
            utils.save_networks(networks)
