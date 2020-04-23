# ==============================================================================================================
#
# Creator: Adrian Lee
# Date: April 10, 2020
#
# This application runs on the console and sends voice commands to Youtube. Using a microphone detached from the
# computer seems to help mitigate latency.
#
# Requirements: Python 3, Google Speech Recognition library for Python, PyAudio, Selenium (and its Chrome webdriver)
#
# ==============================================================================================================

import speech_recognition as sr                                     # enable Google Speech Recognition
import time
from selenium import webdriver                                      # enable interface with Chrome webdriver --so this script can interact with Chrome
from selenium.webdriver.common.by import By                         # enable location of button elements in document
from selenium.webdriver.support import expected_conditions as EC    # enable defaults for wait commands
from selenium.webdriver.support.ui import WebDriverWait             # enable wait commands for webdriver
import os, sys
from lib import youtube_adskipper

class Workout_DJ:

    def __init__(self):

        # Constructor insantiates Chrome web driver which opens Youtube in a new window and initializes member variables
        self.driver = webdriver.Chrome('C:/Users/Valued Customer/Desktop/Python Projects/youtube-voice/chromedriver_win32/chromedriver')
        self.driver.get('https://www.youtube.com/')
        self.current_song = ""
        self.is_playing = 0
        self.autoplay_enabled = 0
        time.sleep(1)
    
    def play_song(self, command):

        # Console outputs
        song = ""
        for i in range(1,len(command)):
            song += command[i]+' '
        print('Playing '+song+'...')

        # Search for song
        search_box = self.driver.find_element_by_name("search_query")
        search_box.send_keys(song)
        search_box.submit()
        wait = WebDriverWait(self.driver, 3)
        visible = EC.visibility_of_element_located
        wait.until(visible((By.ID, "video-title")))

        # Click the first result
        song_link = self.driver.find_element_by_id("video-title")
        self.current_song = song_link.get_attribute('href')
        song_link.click()
        wait = WebDriverWait(self.driver,10)
        visible1 = EC.visibility_of_element_located
        wait.until(visible1((By.CLASS_NAME, "ytp-time-duration")))
        
        # If an ad with a skip button has appeared, press it
        exec(open("youtube_adskipper.py").read())
        self.is_playing = 1

        # Enable autoplay by default
        self.enable_autoplay()

    def pause_song(self):

        button = self.driver.find_element_by_class_name("ytp-play-button")
        if self.is_playing == 1:
            self.is_playing = 0
            print("Paused.")
            button.click()
    
    def resume_song(self):
        
        button = self.driver.find_element_by_class_name("ytp-play-button")
        if self.is_playing == 0:
            self.is_playing = 1
            print('Resumed playing.')
            button.click()

    def start_from(self, command):

        if (command[1] == 'again'):
            song = self.current_song+'&t=0'
            self.driver.get(song)
            return

        if (command[3] == 'seconds'):
            song = self.current_song+'&t='+command[2]
            self.driver.get(song)
            return
        
        if (command[3] == 'minutes'):
            song = self.current_song+'&t='+str(int(command[2])*60)
            self.driver.get(song)
            return

    def replay_song(self):

        button = self.driver.find_element_by_class_name('ytp-play-button')
        if (button.get_attribute('title').lower() == 'replay'):
            button.click()
        else:
            self.start_from(["play","again"])

    def enable_autoplay(self):

        wait = WebDriverWait(self.driver,10)
        visible = EC.visibility_of_element_located
        wait.until(visible((By.ID,"toggle")))

        if self.autoplay_enabled == 0:
            button = self.driver.find_element_by_id("toggle")
            button.click()
            self.autoplay_enabled = 1

    def disable_autoplay(self):

        wait = WebDriverWait(self.driver,10)
        visible = EC.visibility_of_element_located
        wait.until(visible((By.ID,"toggle")))

        if self.autoplay_enabled == 1:
            button = self.driver.find_element_by_id("toggle")
            button.click()
            self.autoplay_enabled = 0

    
if __name__ == "__main__":

    r = sr.Recognizer()
    mic = sr.Microphone()
    youtube = Workout_DJ()

    # Clear console and output prompts (For Windows, command is "cls", for Linux, command is "clear")
    os.system('cls')
    print("\n**-----Commands-----**\nplay <song name>\nenable autoplay\ndisable autoplay\n\n")
    print("**-----When a song is playing, try-----**\nPause\nResume\nPlay Again/Replay\nPlay from <time specified in minutes or seconds>\n\n")
    print("To quit, just say Bye :)\n")
    
    while True:

        with mic as source:

            print("Listening for commands...")

            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)

            try:
                text = r.recognize_google(audio)
                text = text.lower()
                print("You said: {} ".format(text))
                command = text.split(' ')

                # Parsing input
                if (command[0] == 'play'):
                    if (command[1] == 'from'):
                        youtube.start_from(command)
                    elif (command[1] == 'again'):
                        youtube.replay_song()
                    else:
                        youtube.play_song(command)
                elif (command[0] == 'pause'):
                    youtube.pause_song()
                elif (command[0] == 'resume'):
                    youtube.resume_song()
                elif (command[0] == 'replay'):
                    youtube.replay_song()
                elif (instructions == 'disable autoplay'):
                    youtube.disable_autoplay()
                elif (instructions == 'enable autoplay'):
                    youtube.enable_autoplay()
                elif (command[0] == 'bye'):
                    print("Goodbye!")
                    youtube.driver.close()
                    sys.exit()
                else:
                    print('Invalid command.')

            except:
                pass