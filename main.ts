//  key data
let key_circle = neopixel.create(DigitalPin.P2, 16, NeoPixelMode.RGB)
let key_state = "wait_for_press"
let key_count = 0
let key_next_update_ms = 0
//  Shape data
let shape_leds = neopixel.create(DigitalPin.P0, 48, NeoPixelMode.RGB)
let circle_leds = shape_leds.range(1, 5)
let square_leds = shape_leds.range(9, 6)
let triangle_leds = shape_leds.range(18, 3)
let heart_leds = shape_leds.range(25, 4)
let shape_list = ["circle", "square", "triangle", "heart"]
let remaining_shapes = shape_list
let current_shape = shape_list[0]
let last_shape_time = 0
let shape_state_count = 0
let current_shape_state = "idle"
//  Generic defines
let rgb_green = 0x00ff00
let rgb_red = 0xff0000
let rgb_blue = 0x0000ff
let rgb_yellow = 0xffff00
let rgb_black = 0x00
function key_process_wait_for_press() {
    
    if (pins.digitalReadPin(DigitalPin.P11) == 0) {
        key_state = "spin"
        key_circle.showColor(rgb_black)
        key_circle.setPixelColor(0, rgb_green)
        key_circle.show()
    }
    
}

function key_process_spin() {
    
    //  is it time to do an update?
    if (input.runningTime() > key_next_update_ms) {
        // advance the LED
        key_circle.rotate(-1)
        key_circle.show()
    }
    
    //  we're gonna count how many times we've done a "spin"
    //  if we do 3 rotations (48), we're done...move on to flashing
    key_count = key_count + 1
    if (key_count > 48) {
        key_count = 0
        key_state = "flash"
    } else {
        //  otherwise, prepare for the next rotation
        //  calculate the next update input_running_time
        key_next_update_ms = key_next_update_ms + 50
    }
    
}

function key_process_flash() {
    
    //  is it time to do an update?
    if (input.runningTime() > key_next_update_ms) {
        //  3 ons, 3 offs makes 6 iterations through this state
        if (key_count < 6) {
            //  odds are on, evens are offs
            if (key_count % 2 == 0) {
                key_circle.showColor(rgb_green)
            } else {
                key_circle.showColor(rgb_black)
            }
            
            key_count = key_count + 1
            //  200 ms between flashes
            key_next_update_ms = key_next_update_ms + 200
        } else {
            key_circle.showColor(rgb_black)
            key_state = "wait_for_press"
        }
        
    }
    
}

function drive_key_state() {
    if (key_state == "wait_for_press") {
        key_process_wait_for_press()
    } else if (key_state == "spin") {
        key_process_spin()
    } else if (key_state == "flash") {
        key_process_flash()
    }
    
}

function shape_game_reset() {
    
    //  two cleanup items:  make sure the vault is closed, and make sure our strip is off
    //  may not stricly be necessary, but good defensive practice.
    pins.digitalWritePin(DigitalPin.P8, 0)
    shape_leds.showColor(rgb_black)
    //  set up our "shapes" data
    remaining_shapes = shape_list
    let current_shape_index = randint(0, remaining_shapes.length)
    current_shape = remaining_shapes[current_shape_index]
    //  show the first shape.
    turn_shape_on(current_shape)
    let current_shape_state = "input"
}

function get_pin_for_shape(shape: string): number {
    if (shape == "circle") {
        return DigitalPin.P3
    } else if (shape == "square") {
        return DigitalPin.P4
    } else if (shape == "triangle") {
        return DigitalPin.P5
    } else {
        //  shape == "heart"
        return DigitalPin.P6
    }
    
}

//  turns on a single shape
function turn_shape_on(shape: string) {
    if (shape == "circle") {
        circle_leds.showColor(rgb_yellow)
    } else if (shape == "square") {
        square_leds.showColor(rgb_green)
    } else if (shape == "triangle") {
        triangle_leds.showColor(rgb_blue)
    } else if (shape == "heart") {
        heart_leds.showColor(rgb_red)
    }
    
}

//  turns off a single shape
function turn_shape_off(shape: string) {
    if (shape == "circle") {
        circle_leds.showColor(rgb_black)
    } else if (shape == "square") {
        square_leds.showColor(rgb_black)
    } else if (shape == "triangle") {
        triangle_leds.showColor(rgb_black)
    } else if (shape == "heart") {
        heart_leds.showColor(rgb_black)
    }
    
}

function turn_all_shapes_on() {
    turn_shape_on("square")
    turn_shape_on("circle")
    turn_shape_on("triangle")
    turn_shape_on("heart")
}

function turn_on_all_found_shapes() {
    
}

//  clears all shapes
function clear_shapes() {
    shape_leds.showColor(rgb_black)
}

function shape_idle_state() {
    //  currently we do nothing here
    
}

function shape_input_state() {
    
    //  is the current shape button currently pressed?
    let relevant_pin = get_pin_for_shape(current_shape)
    if (pins.digitalReadPin(relevant_pin) == 1) {
        turn_on_all_found_shapes()
        current_shape_state = "flash"
        shape_state_count = 0
    }
    
}

function shape_flash_state() {
    let current_shape_index: number;
    
    let time_now = input.runningTime()
    if (time_now > last_shape_time + 500) {
        //  do we need to turn the symbol on or off?
        //  if we're in the bottom half of the second, we'll turn it on.
        //  top half, we'll  turn it off
        if (time_now % 1000 < 500) {
            turn_shape_on(current_shape)
        } else {
            turn_shape_off(current_shape)
        }
        
        last_shape_time = time_now
        //  if we've flashed it enough, it's time to move on 
        shape_state_count = shape_state_count + 1
        if (shape_state_count > 6) {
            //  do we have more shapes to do?
            remaining_shapes.removeElement(current_shape)
            if (remaining_shapes.length > 0) {
                //  pick the next shape
                current_shape_index = randint(0, remaining_shapes.length)
                current_shape = remaining_shapes[current_shape_index]
                clear_shapes()
                turn_shape_on(current_shape)
                current_shape_state = "input"
            } else {
                //  Thats all of them!  move on to the success state.
                
            }
            
        }
        
    }
    
}

function shape_success_state() {
    
}

function drive_shape_state() {
    
    if (current_shape_state == "idle") {
        shape_idle_state()
    } else if (current_shape_state == "input") {
        shape_input_state()
    } else if (current_shape_state == "flash") {
        shape_flash_state()
    } else if (current_shape_state == "success") {
        shape_success_state()
    }
    
}

shape_game_reset()
basic.forever(function on_forever() {
    drive_key_state()
    drive_shape_state()
})
