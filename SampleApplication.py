import AbstractApplication as Base
import numpy as np
from time import sleep
from threading import Semaphore


class SampleApplication(Base.AbstractApplication):
    def general_repeat_Interaction(self):
        # Ask patient to repeat
        self.sayAnimated('Could you repeat, please?!')
        self.speechLock.acquire()

    def feeling_in_general(self):
        # Ask how the patient is feeling
        self.speechLock = Semaphore(0)
        self.sayAnimated('How are you feeling today?')
        self.speechLock.acquire()

        loop = 0
        output = False
        while loop < 2:
            self.emotion = None
            self.emotionLock = Semaphore(0)
            self.setAudioContext('answer_how_you_feeling')
            self.startListening()
            self.emotionLock.acquire(timeout=5)
            self.stopListening()
            if not self.emotion:  # wait one more second after stopListening (if needed)
                self.emotionLock.acquire(timeout=1)

            if self.emotion:
                loop = 2
                output = True
                if self.emotion == 'happy':
                    self.say('So you are feelin ' + self.emotion)
                    self.doGesture('happy/behavior_1') #custom animation installed on nao
                else:
                    self.sayAnimated('Too bad dude.')
            else:
                self.sayAnimated('Sorry, I didn\'t catch what you said.')
                loop += 1
                general_repeat_Interaction()
        self.speechLock.acquire()

    def feeling_about_meal_interaction(self):
        # Ask how the patient is feeling
        self.speechLock = Semaphore(0)
        self.sayAnimated('How did you feel after your last meal?')
        self.speechLock.acquire()

        self.mealEmotion = None
        self.emotionLock = Semaphore(0)
        self.setAudioContext('answer_how_you_feeling_after_meal')
        self.startListening()
        self.emotionLock.acquire(timeout=5)
        self.stopListening()
        if not self.mealEmotion:  # wait one more second after stopListening (if needed)
            self.emotionLock.acquire(timeout=1)

        if self.mealEmotion:
            if self.mealEmotion == 'good_feeling':
                self.say('So you are feelin ' + self.mealEmotion)
                self.doGesture('happy/behavior_1') #custom animation installed on nao
                self.sayAnimated(compliments[np.random.randint(0, len(compliments))])
            else:
                self.sayAnimated(quotes[np.random.randint(0, len(quotes))])
        else:
            self.sayAnimated('Sorry, I didn\'t catch what you said.')
        self.speechLock.acquire()


    def main(self):
        # Set the correct language (and wait for it to be changed)
        self.langLock = Semaphore(0)
        self.setLanguage('en-US')
        self.langLock.acquire()

        # Pass the required Dialogflow parameters (add your Dialogflow parameters)
        self.setDialogflowKey('nao_key.json') # Add your own json-file name here
        self.setDialogflowAgent('nao-akwxxe')

        # # Make the robot ask the for the name, and wait until it is done speaking
        # self.speechLock = Semaphore(0)
        # self.sayAnimated('Hello, what is your name?')
        # self.speechLock.acquire()
        #
        # # Listen for an answer for at most 5 seconds
        # self.name = None
        # self.nameLock = Semaphore(0)
        # self.setAudioContext('answer_name')
        # self.startListening()
        # self.nameLock.acquire(timeout=5)
        # self.stopListening()
        # if not self.name:  # wait one more second after stopListening (if needed)
        #     self.nameLock.acquire(timeout=1)
        #
        # # Respond and wait for that to finish
        # if self.name:
        #     self.sayAnimated('Nice to meet you ' + self.name + '!')
        # else:
        #     self.sayAnimated('Sorry, I didn\'t catch your name.')
        # self.speechLock.acquire()
        #
        # # Ask for the time
        # self.speechLock = Semaphore(0)
        # self.sayAnimated('Could you tell me the time ' + self.name + '?')
        # self.speechLock.acquire()
        #
        # self.time = None
        # self.timelock = Semaphore(0)
        # self.setAudioContext('answer_time')
        # self.startListening()
        # self.timelock.acquire(timeout=3)
        # self.stopListening()
        # if not self.time:  # wait one more second after stopListening (if needed)
        #     self.timelock.acquire(timeout=1)
        #
        # if self.time:
        #     self.sayAnimated('So the time is  ' + self.time + '!')
        # else:
        #     self.sayAnimated('Sorry, I didn\'t catch what you said.')
        # self.speechLock.acquire()

        feeling_in_general()

        feelings_about_meal_interaction()

    def onRobotEvent(self, event):
        if event == 'LanguageChanged':
            self.langLock.release()
        elif event == 'TextDone':
            self.speechLock.release()
        elif event == 'GestureDone':
            self.gestureLock.release()

    def onAudioIntent(self, *args, intentName):
        if intentName == 'answer_name' and len(args) > 0:
            self.name = args[0]
            self.nameLock.release()
        if intentName == 'answer_time' and len(args) > 0:
            self.time = args[0]
            self.timelock.release()
        if intentName == 'answer_how_you_feeling' and len(args) > 0:
            self.emotion = args[0]
            self.emotionLock.release()

# Run the application
sample = SampleApplication()
sample.main()
sample.stop()
