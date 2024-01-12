import os
import random
import time
import typing
from enum import Enum

import gpiozero
import pygame
import serial
import subprocess
import json
import datetime

DEBUG=False
NUM_BEANS = 4

#           RED          GREEN      BLUE     YELLOW
COLORS = ('255 0 0', '0 255 0', '0 0 255', '255 255 0')

BUTTONS = [ gpiozero.Button("GPIO23", bounce_time=0.01),
            gpiozero.Button("GPIO22", bounce_time=0.01),
            gpiozero.Button("GPIO17", bounce_time=0.01),
            gpiozero.Button("GPIO27", bounce_time=0.01) ]

# Cheat mode strings with passwords as lists
CHEAT_MODES = {
    "print_a_line": [1,1,1,1],
    "dog_mode": [4,3,2,1],
    "cat_mode": [1,2,3,4],
    "blue_mode": [3,3,3,3,3,3],
    "speedrun_mode": [2,3,1,4],
}


class BeanColors(Enum):
    red = COLORS[0]
    green = COLORS[1]
    blue = COLORS[2]
    yellow = COLORS[3]
    off = "0 0 0"


def light_command(ser, command):
    if DEBUG:
        print(time.time(), "LIGHT:", command)
    ser.write(command.encode("latin1"))
    ser.flush()


def get_soundboard():
    """Play an audio file as a buffered sound sample

    :param str file_path: audio file (default data/secosmic_low.wav)
    """
    # choose a desired audio format
    pygame.mixer.init(8000)  # raises exception on fail

    # load the sounds
    sounds = []
    root_dir = os.path.dirname(__file__)
    sounds_directory = os.path.join(root_dir, "sounds")
    for f in os.listdir(sounds_directory):
        sounds.append(pygame.mixer.Sound(os.path.join(sounds_directory, f)))

    return sounds


def get_dog_soundboard():
    """Play an audio file as a buffered sound sample, but with dogs

    :param str file_path: audio file (default data/secosmic_low.wav)
    """
    # choose a desired audio format
    pygame.mixer.init(8000)  # raises exception on fail

    # load the sounds
    sounds = []
    root_dir = os.path.dirname(__file__)
    sounds_directory = os.path.join(root_dir, "espeak_sounds/normal")
    sounds = [
        pygame.mixer.Sound(os.path.join(sounds_directory, "espeak_woof_p0_a200.wav")),
        pygame.mixer.Sound(os.path.join(sounds_directory, "espeak_woof_p50_a200.wav")),
        pygame.mixer.Sound(os.path.join(sounds_directory, "espeak_woof_p75_a200.wav")),
        pygame.mixer.Sound(os.path.join(sounds_directory, "espeak_woof_p100_a200.wav")),
    ]

    return sounds


def get_cat_soundboard():
    """Play an audio file as a buffered sound sample, but with dogs

    :param str file_path: audio file (default data/secosmic_low.wav)
    """
    # choose a desired audio format
    pygame.mixer.init(8000)  # raises exception on fail

    # load the sounds
    sounds = []
    root_dir = os.path.dirname(__file__)
    sounds_directory = os.path.join(root_dir, "espeak_sounds/normal")
    sounds = [
        pygame.mixer.Sound(os.path.join(sounds_directory, "espeak_meow_p0_a200.wav")),
        pygame.mixer.Sound(os.path.join(sounds_directory, "espeak_meow_p50_a200.wav")),
        pygame.mixer.Sound(os.path.join(sounds_directory, "espeak_meow_p75_a200.wav")),
        pygame.mixer.Sound(os.path.join(sounds_directory, "espeak_meow_p100_a200.wav")),
    ]

    return sounds


class AttractMode:
    def __init__(
        self,
        ser: typing.Optional[serial.Serial],
        seed: float = time.time(),
        dummy: bool = False,
    ):
        random.seed(seed)
        self._ser: typing.Optional[serial.Serial] = ser
        self._bean_statuses: typing.List[bool, ...] = [False, False, False, False]
        self._all_animations: typing.List[typing.Callable, ...] = [
            self.twinkle,
            self.all_on_all_off,
        ]
        self._dummy: bool = dummy

    def _poll_wait(self, delay_ms: int) -> bool:
        for _ in range(round((delay_ms * 0.9))):  # approximate the delay here
            pygame.time.wait(1)
            if not self._dummy and poll_buttons():
                return True
        return False

    @classmethod
    def _gen_bean_command(cls, bean: int, color: BeanColors) -> str:
        if 1 > bean > NUM_BEANS + 1:
            raise ValueError(f"Incorrect bean index {bean}")
        return f"ON {bean + 1} {color.value}\n"

    @classmethod
    def _random_color(cls) -> BeanColors:
        return random.choice(BeanColors)

    @classmethod
    def _correct_bean_color(cls, bean) -> BeanColors:
        return BeanColors(COLORS[bean])

    @classmethod
    def _random_bean(cls) -> int:
        return random.randrange(0, NUM_BEANS)

    def _random_off_bean(self) -> int:
        return random.choice(
            [bean for bean in range(NUM_BEANS) if self._bean_statuses[bean] is False]
        )

    def _random_on_bean(self) -> int:
        return random.choice(
            [bean for bean in range(NUM_BEANS) if self._bean_statuses[bean] is True]
        )

    @property
    def _all_beans_off(self) -> bool:
        return self._bean_statuses == [False, False, False, False]

    @property
    def _all_beans_on(self) -> bool:
        return self._bean_statuses == [True, True, True, True]

    def _set_bean(self, bean: int, color: BeanColors):
        if not self._dummy:
            light_command(
                ser=self._ser, command=self._gen_bean_command(bean=bean, color=color)
            )
        else:
            print(f"Attract Mode: {self._gen_bean_command(bean=bean, color=color)}")
        self._bean_statuses[bean] = False if color == BeanColors.off else True

    def _flash_random_bean(self, on_time_ms: int = 500) -> bool:
        bean = self._random_bean()
        self._set_bean(bean=bean, color=self._correct_bean_color(bean=bean))
        if self._poll_wait(delay_ms=on_time_ms):
            return True
        self._set_bean(bean=bean, color=BeanColors.off)
        return False

    def twinkle(self, num_flashes: int = random.randrange(10, 20)) -> bool:
        print("Playing twinkle animation")
        for _ in range(num_flashes):
            if self._flash_random_bean():
                return True
        self._clear_all_beans()
        return False

    def all_on_all_off(self, num_cycles=random.randrange(2, 5)):
        print("Playing all on all off animation")
        for _ in range(num_cycles):
            self._clear_all_beans()
            while not self._all_beans_on:
                bean = self._random_off_bean()
                self._set_bean(bean=bean, color=self._correct_bean_color(bean))
                if self._poll_wait(500):
                    return True
            while not self._all_beans_off:
                self._set_bean(bean=self._random_on_bean(), color=BeanColors.off)
                if self._poll_wait(500):
                    return True
        return False

    def game_over(self):
        self._set_bean(bean=-1, color=BeanColors.red)
        root_dir = os.path.dirname(__file__)
        game_over_sound_path = os.path.join(root_dir, "buzzer_3.wav")
        sound = pygame.mixer.Sound(game_over_sound_path)
        channel = sound.play()
        # poll until finished playing sound
        while channel.get_busy():
            pygame.time.wait(10)
        self._clear_all_beans()

    def _clear_all_beans(self):
        if not self._dummy:
            light_command(ser=self._ser, command="ON 0 0 0 0\n")
        self._bean_statuses = [False, False, False, False]

    def play(self) -> None:
        while True:
            random.shuffle(self._all_animations)
            for animation in self._all_animations:
                if animation():
                    self._clear_all_beans()
                    return


def get_cheat_mode_str(input_list):
    # It's not efficient, but goddammit it's 2024
    # and if we have enough cheat modes for it to
    # matter, I'm very proud of us. - Kataze
    if input_list not in CHEAT_MODES.values():
        cheat_mode_str = None
    else:
        cheat_mode_str = list(CHEAT_MODES.keys())[list(CHEAT_MODES.values()).index(input_list)]
    return cheat_mode_str


def light_all_beans(ser):
    for i, color in enumerate(COLORS):
        bean_idx = i + 1
        light_command(ser, f"ON {bean_idx} {color}\n")


def blank_all_beans(ser):
    light_command(ser, "ON 0 0 0 0\n")


def beep_and_flash(ser, index, interruptable=False):
    global SPEEDRUN_TIMER

    assert index > 0 and index <= 4
    light, sound = LIGHTS_AND_SOUND[index - 1]

    light_command(ser, f"ON {index} {light}\n")
    channel = sound.play()

    if SPEEDRUN_TIMER:
        pygame.time.wait(SPEEDRUN_TIMER)
        channel.stop()
        if SPEEDRUN_TIMER > 50:
            SPEEDRUN_TIMER = SPEEDRUN_TIMER - 10
    else:
        # poll until finished playing sound
        while channel.get_busy():
            pygame.time.wait(10)

    # turn off light
    light_command(ser, f"ON {index} 0 0 0\n")


def beep_and_flash_input(ser, index):
    assert index > 0 and index <= 4
    light, sound = LIGHTS_AND_SOUND[index - 1]

    light_command(ser, f"ON {index} {light}\n")
    channel = sound.play()

    # very fun quirk, need to call wait_for_press before wait_for_release behaves correctly.
    BUTTONS[index - 1].wait_for_press()
    BUTTONS[index - 1].wait_for_release()
    print(f"Button {index} pushed")

    if SPEEDRUN_TIMER:
        for _ in range(round((SPEEDRUN_TIMER * 0.9))): # Borrowing kay's technique for non-blocking wait
            pygame.time.wait(1)
            butt = poll_buttons()
            if butt != 0:
                break
        channel.stop()
    else:
        while channel.get_busy():
            butt = poll_buttons()
            if butt != 0:
                channel.stop()
                break

    # turn off light
    light_command(ser, f"ON {index} 0 0 0\n")


def beep_and_flash_bad(ser, game_memory, cheat_mode_str):
    # Function for when you lose
    sadge = AttractMode(ser=ser)
    sadge.game_over()
    score = len(game_memory) - 1
    create_or_increment_odometer(cheat_mode_str, score)
    if cheat_mode_str:
        print(f"{cheat_mode_str} GAME OVER!")
    else:
        print("GAME OVER!")
    print(f"YOUR SCORE: {score}")
    print("JOIN PAWPRINT PROTOTYPING AT PAWPRINTPROTOTYPING.ORG\n\n")

def create_or_increment_odometer(cheat_mode_str, score):
    root_dir = os.path.dirname(__file__)
    odometer_path = os.path.join(root_dir, "odometer.json")
    
    # make it if it's not there, put a pretty timestamp
    if not os.path.isfile(odometer_path):
        with open(odometer_path, "w") as odometer_file:
            odometer = {"odometer_started": datetime.datetime.now().isoformat()}
            json.dump(odometer, odometer_file)

    with open(odometer_path, "r+") as odometer_file:
        odometer = json.load(odometer_file)
        odometer["total_games"] = odometer.get("total_games", 0) + 1
        if cheat_mode_str:
            odometer[cheat_mode_str] = odometer.get(cheat_mode_str, 0) + 1
        high_score = odometer.get("high_score", 0)
        if score > high_score:
            print("HIGH SCORE!!!!!!!!!!!!!!!111!!")
            odometer["high_score"] = score
        # blow away the original file 
        odometer_file.truncate(0)
        odometer_file.seek(0)
        json.dump(odometer, odometer_file)


def poll_buttons() -> int:
    """
    Polls and returns 1-index button if a button is pressed.
    Returns 0 if no button is pressed.
    """
    for idx, butt in enumerate(BUTTONS):
        if butt.is_pressed:
            return idx + 1
    return 0


def next_value():
    return random.choice(list(range(1, NUM_BEANS + 1)))


def block_until_butt_release(butt):
    BUTTONS[butt - 1].wait_for_press()
    BUTTONS[butt - 1].wait_for_release()

def reset_to_normal_mode():
    # If you change something for a special cheat mode, make sure to reset it here!
    global LIGHTS_AND_SOUND
    global BLUE_PLAYER_PROC
    global SPEEDRUN_TIMER
    global SONIC_PROC
    LIGHTS_AND_SOUND = list(zip(COLORS, get_soundboard()))
    # kill any video players
    if BLUE_PLAYER_PROC:
        # Begone thot
        BLUE_PLAYER_PROC.kill()
        BLUE_PLAYER_PROC = None
    SPEEDRUN_TIMER = None
    if SONIC_PROC:
        # Be gentler and SIGTERM, since there's a family tree here
        SONIC_PROC.terminate()
        SONIC_PROC = None

def main():
    global LIGHTS_AND_SOUND
    global BLUE_PLAYER_PROC
    global SPEEDRUN_TIMER
    global SONIC_PROC
    LIGHTS_AND_SOUND = list(zip(COLORS, get_soundboard()))
    BLUE_PLAYER_PROC = None
    SPEEDRUN_TIMER = None
    SONIC_PROC = None
    TIMEOUT_VALUE = 10
    CHEAT_TIMEOUT_VALUE = 3

    game_memory = []

    with serial.Serial("/dev/ttyUSB0", 115200, timeout=1) as ser:
        while True:
            # Clear all the beans
            light_command(ser, "ON 0 0 0 0\n")

            # Reset anything that might have been affected by a special mode
            reset_to_normal_mode()

            attract = AttractMode(ser=ser)
            attract.play()  # Will continue as soon as someone hits a button
            print("Attract mode is over! Starting in 3 seconds...")
            
            # == WELCOME TO THE CHEAT ZONE!!!!11!! ==
            #light up all beans for cheat code entry
            light_all_beans(ser)
            cheat_memory = []
            cheat_input_start_time = time.time()
            first_button_press = True
            while time.time() <= cheat_input_start_time + CHEAT_TIMEOUT_VALUE:
                butt = poll_buttons()
                if butt:
                    if first_button_press:
                        # Throw out the first button press that exits attract mode
                        first_button_press = False
                        block_until_butt_release(butt)
                    else:
                        cheat_memory.append(butt) # Add it to the list
                        block_until_butt_release(butt)
                        print(f"BUTTON {butt} PRESSED!")

            print(f"CHEAT MEMORY: {cheat_memory}")
            blank_all_beans(ser)

            cheat_mode_str = get_cheat_mode_str(cheat_memory)
            
            # If you got a cheat mode at all, let's congratulate you!
            if cheat_mode_str:
                root_dir = os.path.dirname(__file__)
                zelda_secret_sound_path = os.path.join(root_dir, "zelda_secret.wav")
                sound = pygame.mixer.Sound(zelda_secret_sound_path)
                channel = sound.play()
                
                # Celebratory green flash!
                for _ in range(3):
                    light_command(ser, f"ON 0 0 255 0\n")
                    pygame.time.wait(200)
                    blank_all_beans(ser)
                    pygame.time.wait(200)

                # Let the sound finish, because you're worth it
                while channel.get_busy():
                    pygame.time.wait(10)


            if cheat_mode_str == "print_a_line":
                print("CHEAT MODE UNLOCKED: PRINT A LINE! YOU'RE SUCH A HACKER!!")

            if cheat_mode_str == "dog_mode":
                print("CHEAT MODE UNLOCKED: DOG MODE!! DOGS ROOL CATS DROOL!")
                LIGHTS_AND_SOUND = list(zip(COLORS, get_dog_soundboard()))

            if cheat_mode_str == "cat_mode":
                print("CHEAT MODE UNLOCKED: CAT MODE!! CATS ROOL DOGS DROOL!")
                LIGHTS_AND_SOUND = list(zip(COLORS, get_cat_soundboard()))

            if cheat_mode_str == "blue_mode":
                print("CHEAT MODE UNLOCKED: BLUE MODE!! DA BA DEE DA BA DI!")
                root_dir = os.path.dirname(__file__)
                videos_directory = os.path.join(root_dir, "videos")
                full_blue_path = os.path.join(videos_directory, "blue.webm")
                BLUE_COLORS = ('0 0 255', '0 0 255', '0 0 255', '0 0 255')
                LIGHTS_AND_SOUND = list(zip(BLUE_COLORS, get_soundboard()))
                BLUE_PLAYER_PROC = subprocess.Popen(["mplayer", "-geometry", "300x300+300+300", full_blue_path])

            if cheat_mode_str == "speedrun_mode":
                print("CHEAT MODE UNLOCKED: SPEED RUN MODE!! GOTTA GO FAST!")
                SPEEDRUN_TIMER = 500
                root_dir = os.path.dirname(__file__)
                scripts_directory = os.path.join(root_dir, "scripts")
                full_sanic_path = os.path.join(scripts_directory, "sanic.sh")
                SONIC_PROC = subprocess.Popen(full_sanic_path)

            # == NOW LEAVING THE CHEAT ZONE!!!! KEEP IT R34L!! ==

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
                        if DEBUG:
                            print(
                                f"current_idx = {current_idx}, butt = {butt}, game_memory = {game_memory}"
                            )
                        # import pdb; pdb.set_trace()
                        if game_memory[current_idx] == butt:  # haha butt
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
                            beep_and_flash_bad(ser, game_memory, cheat_mode_str)
                            game_memory = []
                            running = False
                            break

                if running and not continue_game:
                    # you lose! (timeout)
                    beep_and_flash_bad(ser, game_memory, cheat_mode_str)
                    game_memory = []
                    running = False
                    break


if __name__ == "__main__":
    main()
