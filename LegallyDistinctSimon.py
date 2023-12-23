import random
import os
import time
import pygame
import gpiozero
import serial

COLORS = ('255 0 0', '0 255 0', '0 0 255', '255 0 255')


def light_command(ser, command):
    print(time.time(), "LIGHT:", command)
    ser.write(command.encode('latin1'))
    ser.flush()


def beep_and_flash(ser, index):
    assert index > 0 and index <= 4
    light, sound = LIGHTS_AND_SOUND[index-1]

    light_command(ser, f"ON {index} {light}\n")
    channel = sound.play()

    # poll until finished
    while channel.get_busy():
        pygame.time.wait(100)

    # turn off light
    light_command(ser, f"ON {index} 0 0 0\n")
    

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
    
    

    butt = gpiozero.Button("GPIO17", bounce_time=0.01)

    on = False 

    with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser:
        for i in range(1, 10):
            beep_and_flash(ser, random.choice(list(range(1, 5))))
        
        pygame.quit()
        return


        while True: 
            pressed = butt.is_pressed
            if pressed:
                command = b'ON 0 255 000 255\n'
            else:
                command = b'ON 0 000 000 000\n'

            if on != pressed:
                print(command)
                ser.write(command)
                ser.flush()
                print("done")
                on = pressed


if __name__ == "__main__":
    main()
