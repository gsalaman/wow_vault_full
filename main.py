# key data
key_circle = neopixel.create(DigitalPin.P2, 16, NeoPixelMode.RGB)
key_state = "wait_for_press"
key_count = 0
key_next_update_ms = 0

# Shape data
shape_leds = neopixel.create(DigitalPin.P0, 48, NeoPixelMode.RGB)
circle_leds = shape_leds.range(1, 5)
square_leds = shape_leds.range(9,6)
triangle_leds = shape_leds.range(18,3)
heart_leds = shape_leds.range(25,4)

shape_list = ["circle", "square", "triangle", "heart"]
remaining_shapes = shape_list
current_shape = shape_list[0]
last_shape_time = 0
shape_state_count = 0
current_shape_state = "idle"

# Generic defines
rgb_green = 0x00ff00
rgb_red = 0xff0000
rgb_blue = 0x0000ff
rgb_yellow = 0xffff00
rgb_black = 0x00

def key_process_wait_for_press():
    global key_state, key_circle
    if (pins.digital_read_pin(DigitalPin.P11) == 0):
        key_state = "spin"
        key_circle.show_color(rgb_black)
        key_circle.set_pixel_color(0, rgb_green)
        key_circle.show()

def key_process_spin():
    global key_next_update_ms, key_circle, key_count, key_state
    # is it time to do an update?
    if (input.running_time() > key_next_update_ms):
        #advance the LED
        key_circle.rotate(-1)
        key_circle.show()
    
    # we're gonna count how many times we've done a "spin"
    # if we do 3 rotations (48), we're done...move on to flashing
    key_count = key_count + 1
    if (key_count > 48):
        key_count = 0
        key_state = "flash"
    # otherwise, prepare for the next rotation
    else:
        # calculate the next update input_running_time
        key_next_update_ms = key_next_update_ms + 50

def key_process_flash():
    global key_count, key_next_update_ms, key_circle, key_state
    # is it time to do an update?
    if (input.running_time() > key_next_update_ms):
        # 3 ons, 3 offs makes 6 iterations through this state
        if (key_count < 6):
            # odds are on, evens are offs
            if (key_count % 2 == 0):
                key_circle.show_color(rgb_green)
            else:
                key_circle.show_color(rgb_black)
            key_count = key_count + 1

            # 200 ms between flashes
            key_next_update_ms = key_next_update_ms + 200
        else:
            key_circle.show_color(rgb_black)
            key_state = "wait_for_press"

def drive_key_state():
    if (key_state == "wait_for_press"):
        key_process_wait_for_press()
    elif (key_state == "spin"):
        key_process_spin()
    elif (key_state == "flash"):
        key_process_flash()

def shape_game_reset():
    global remaining_shapes, shape_list, current_shape, shape_leds, current_shape_state

    # two cleanup items:  make sure the vault is closed, and make sure our strip is off
    # may not stricly be necessary, but good defensive practice.
    pins.digital_write_pin(DigitalPin.P8, 0)
    shape_leds.show_color(rgb_black)

    # set up our "shapes" data
    remaining_shapes = shape_list
    current_shape_index = randint(0,remaining_shapes.length)
    current_shape = remaining_shapes[current_shape_index]

    # show the first shape.
    turn_shape_on(current_shape)
    current_shape_state = "input"

def get_pin_for_shape(shape):
    if (shape == "circle"):
        return(DigitalPin.P3)
    elif (shape == "square"):
        return(DigitalPin.P4)
    elif (shape == "triangle"):
        return(DigitalPin.P5)
    else:  # shape == "heart"
        return(DigitalPin.P6)

# turns on a single shape
def turn_shape_on(shape):
    if (shape == "circle"):
        circle_leds.show_color(rgb_yellow)
    elif (shape == "square"):
        square_leds.show_color(rgb_green)
    elif (shape == "triangle"):
        triangle_leds.show_color(rgb_blue)
    elif (shape == "heart"):
        heart_leds.show_color(rgb_red)
       
# turns off a single shape
def turn_shape_off(shape):
    if (shape == "circle"):
        circle_leds.show_color(rgb_black)
    elif (shape == "square"):
        square_leds.show_color(rgb_black)
    elif (shape == "triangle"):
        triangle_leds.show_color(rgb_black)
    elif (shape == "heart"):
        heart_leds.show_color(rgb_black)

def turn_all_shapes_on():
    turn_shape_on("square")
    turn_shape_on("circle")
    turn_shape_on("triangle")
    turn_shape_on("heart")

def turn_on_all_found_shapes():
    pass

# clears all shapes
def clear_shapes():
    shape_leds.show_color(rgb_black)

def shape_idle_state():
    # currently we do nothing here
    # eventually, we can use this for cases where we want the shape game to 
    # do nothing...like secret codes, or if we want to go sequential between
    # the key and shape games.
    pass

def shape_input_state():
    global current_shape, current_shape_state, shape_state_count

    # is the current shape button currently pressed?
    relevant_pin = get_pin_for_shape(current_shape)
    if (pins.digital_read_pin(relevant_pin) == 1):
        # turn_on_all_found_shapes()
        current_shape_state = "flash"
        shape_state_count = 0

def shape_flash_state():
    global current_shape, remaining_shapes, shape_state_count, current_shape_state, last_shape_time

    time_now = input.running_time()
    if (time_now > last_shape_time + 500):
        # do we need to turn the symbol on or off?
        # if we're in the bottom half of the second, we'll turn it on.
        # top half, we'll  turn it off
        if (time_now % 1000 < 500):
            turn_shape_on(current_shape)
        else:
            turn_shape_off(current_shape)
        last_shape_time = time_now
        
        # if we've flashed it enough, it's time to move on 
        shape_state_count = shape_state_count + 1
        if (shape_state_count > 6):
            # do we have more shapes to do?
            remaining_shapes.remove_element(current_shape)
            if (remaining_shapes.length > 0):
                # pick the next shape
                current_shape_index = randint(0,remaining_shapes.length)
                current_shape = remaining_shapes[current_shape_index]
                clear_shapes()
                turn_shape_on(current_shape)
                current_shape_state = "input"

            else: 
                # Thats all of them!  Open the vault and move on to the success state.
                pins.digital_write_pin(DigitalPin.P8, 1)
                last_shape_time = 0
                shape_state_count = 0
                current_shape_state = "success"

def shape_success_state():
    global shape_state_count, last_shape_time
    # cycle shapes from left to right
    # we're gonna use the shape state count to keep track of where we are in our cycle
    # first four light up all shapes in order, next four turn them off in order.
    # Then repeat N times...so N*8 counts and we're done.
    shape_repeats = 3
    time_now = input.running_time()
    if (time_now > last_shape_time + 500):
        if (shape_state_count >= shape_repeats * 8):
            # we're done...go back to the beginning.
            shape_game_reset()
        else:
            
            # there's probably a more elegant way of doing this...
            if (shape_state_count % 8 == 0):
                # light up the circle
                turn_shape_on("circle")

            elif (shape_state_count % 8 == 1):
                # light up the square 
                turn_shape_on("square")

            elif (shape_state_count % 8 == 2):
                # light up the triangle
                turn_shape_on("triangle")

            elif (shape_state_count % 8 == 3):
                #light up the heart
                turn_shape_on("heart")

            elif (shape_state_count % 8 == 4):
                # turn off the circle
                turn_shape_off("circle")

            elif (shape_state_count % 8 == 5):
                # turn off the square
                turn_shape_off("square")

            elif (shape_state_count % 8 == 6):
                # turn off the triangle
                turn_shape_off("triangle")

            else:
                # turn off the heart_leds
                turn_shape_off("heart")

            last_shape_time = time_now
            shape_state_count = shape_state_count + 1



def drive_shape_state():
    global current_shape_state

    if (current_shape_state == "idle"):
        shape_idle_state()
    elif (current_shape_state == "input"):
        shape_input_state()
    elif (current_shape_state == "flash"):
        shape_flash_state()
    elif (current_shape_state == "success"):
        shape_success_state()

def on_forever():
    drive_key_state()
    drive_shape_state()

shape_game_reset()    
basic.forever(on_forever)
