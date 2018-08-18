# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 22:55:54 2017

@author: eugeneschao
"""

#!/usr/bin/env python

import os, time, threading
import picamera as camera
import RPi.GPIO as GPIO
import configparser # to load config.ini

class Trigger_Camera(threading.Thread):
    # Initialization
    def __init__(self):
        threading.Thread.__init__(self)
        self.savepath = '/home/pi/video/' + time.strftime('%Y%m%d') + '/'
        if not os.path.exists(self.savepath):
                print('\ttrigger_camera is making output directory: %s\n' % self.savepath)
                os.makedirs(self.savepath)
    		#1. set up default setting
        self.config = {}
        self.config['system'] = {}
        self.config['system']['videolength'] = 30
        self.config['system']['videoname'] = 'test'
        self.config['camera'] = {}
        self.config['camera']['fps'] = 30
        self.config['camera']['resolution'] = (1296, 730)
        self.config['trigger'] = {}
        self.config['trigger']['triggerpin'] = 27
        #2. read setting from config.ini
        self.ParseConfigFile()
        #3. set up trigger camera
        camera.resolution = self.config['camera']['resolution']
        camera.framerate = self.config['camera']['fps']
        trigger = self.config['trigger']['triggerpin']
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)	 # set up BCM GPIO numbering
        GPIO.setup(trigger, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.remove_event_detect(trigger)
        #4. wait for trigger pulse from acquisition device, then record video
        GPIO.add_event_detect(trigger, GPIO.RISING, callback=self.triggerPinCallback, bouncetime=200)
    # Parse config.ini for camera settings
    def ParseConfigFile(self):
        print('\ttrigger_camera.ParseConfigFile() is reading config file from config.ini')
        Config = configparser.ConfigParser()
        Config.read('/home/pi/trigger_camera/config.ini')
        Config.sections()
        self.config['system']['videolength'] = int(Config.get('system','videolength'))
        self.config['system']['videoname'] = Config.get('system','videoname')
        self.config['camera']['fps'] = int(Config.get('camera','fps'))
        resolution = Config.get('camera','resolution').split(',')
        self.config['camera']['resolution'] = (int(resolution[0]), int(resolution[1]))		
        self.config['trigger']['triggerpin'] = int(Config.get('trigger','triggerpin'))
        print('\tdone reading config file')
    # If trigger is detected, record video
    def triggerPinCallback(self, pin):
        pinIsUp = GPIO.input(pin)
        if pinIsUp:
            self.recordTime(os.path.join(self.savepath,self.config['system']['videoname']),self.config['system']['videolength'])
    # Record video for set amount of time (s)
    def recordTime(self,name,time):
        print('\ttriggercamera is recording video')        
        # Record video to the file name specified
        camera.start_recording(name, format='h264')
        camera.wait_recording(time)
        camera.stop_recording()
  
  
