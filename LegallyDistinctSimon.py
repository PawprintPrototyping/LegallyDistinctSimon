import random
import os
import time
import pygame
import gpiozero
import serial

COLORS = ('255 0 0', '0 255 0', '0 0 255', '255 0 255')

BUTTONS = [ gpiozero.Button("GPIO17", bounce_time=0.01),
            gpiozero.Button("GPIO27", bounce_time=0.01),
            gpiozero.Button("GPIO22", bounce_time=0.01),
            gpiozero.Button("GPIO23", bounce_time=0.01) ]

def light_command(ser, command):
    print(time.time(), "LIGHT:", command)
    ser.write(command.encode('latin1'))
    ser.flush()


def beep_and_flash(ser, index, interruptable=False):
    assert index > 0 and index <= 4
    light, sound = LIGHTS_AND_SOUND[index-1]

    light_command(ser, f"ON {index} {light}\n")
    channel = sound.play()
            
    # poll until finished playing sound
    while channel.get_busy():
        pygame.time.wait(10)

    # turn off light
    light_command(ser, f"ON {index} 0 0 0\n")


def beep_and_flash_input(ser, index):
    assert index > 0 and index <= 4
    light, sound = LIGHTS_AND_SOUND[index-1]
    
    light_command(ser, f"ON {index} {light}\n")
    channel = sound.play()
   
    # very fun quirk, need to call wait_for_press before wait_for_release behaves correctly.
    BUTTONS[index-1].wait_for_press()
    BUTTONS[index-1].wait_for_release()
    print(time.time(), f"Button {index} released")

    while channel.get_busy():
        butt = poll_buttons()
        if butt != 0:
            channel.stop()
            break

    # turn off light
    light_command(ser, f"ON {index} 0 0 0\n")

def beep_and_flash_bad(ser):
    # Function for when you lose
    print("GAME OVER")

def poll_buttons():
    """
    Polls and returns 1-index button if a button is pressed.
    Returns 0 if no button is pressed.
    """
    for idx, butt in enumerate(BUTTONS):
        if butt.is_pressed:
            return idx + 1
    return 0

    

def get_soundboard():
    """Play an audio file as a buffered sound sample

    :param str file_path: audio file (default data/secosmic_low.wav)
    """
    # choose a desired audio format
    pygame.mixer.init(8000)  # raises exception on fail

    # load the sounds
    sounds = []
    sounds_directory = '/root/LegallyDistinctSimon/sounds'
    for f in os.listdir(sounds_directory):
        sounds.append(pygame.mixer.Sound(os.path.join(sounds_directory, f)))

    return sounds

def next_value():
    return random.choice(list(range(1, 5)))

def main():
    global LIGHTS_AND_SOUND
    LIGHTS_AND_SOUND = list(zip(COLORS, get_soundboard()))
    TIMEOUT_VALUE = 10

    game_memory = []
    
    with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser:

        # Clear all the beans
        light_command(ser, "ON 0 0 0 0\n")


        running = True
        while running:
            game_memory.append(next_value())

            # Say the game memory for player to memorize
            print("SAY")
            for bean in game_memory:
                beep_and_flash(ser, bean)
                pygame.time.wait(100)

            input_start_time = time.time()
            current_idx = 0
            print("ASK")
            continue_game = False
            while time.time() <= input_start_time + TIMEOUT_VALUE:
                # Ask player to repeat it back
                butt = poll_buttons()
                if butt:
                    # correct answer!
                    print(f"current_idx = {current_idx}, butt = {butt}, game_memory = {game_memory}")
                    #import pdb; pdb.set_trace()
                    if game_memory[current_idx] == butt:
                        beep_and_flash_input(ser, butt)
                        current_idx += 1
                        # good job! next sequence
                        if current_idx >= len(game_memory):
                            continue_game = True
                            pygame.time.wait(500)
                            break

                        input_start_time = time.time()
                    # you lose!
                    else:
                        beep_and_flash_bad(ser)
                        game_memory = []
                        return

            if not continue_game: 
                # you lose! (timeout)
                beep_and_flash_bad(ser)
                game_memory = []
                return




if __name__ == "__main__":
    main()
