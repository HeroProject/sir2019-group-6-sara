import AbstractApplication as Base
import numpy as np
from time import sleep
from threading import Semaphore


class SampleApplication(Base.AbstractApplication):
    def main(self):
        # Set the correct language (and wait for it to be changed)
        self.langLock = Semaphore(0)
        self.setLanguage('en-US')
        self.langLock.acquire()

        # Pass the required Dialogflow parameters (add your Dialogflow parameters)
        self.setDialogflowKey('nao_key.json')  # Add your own json-file name here
        self.setDialogflowAgent('nao-akwxxe')

        # Asking the patient how they are feeling
        self.interaction('how are you feeling today?',
                         'answer_how_you_feeling',
                         ['happy'],
                         ['So you are feeling', 'I\'m sorry to hear that'],
                         ['happy/behavior_1'])

        # Asking the patient how they felt after their last meal
        self.interaction('How did you feel after your last meal?',
                         'answer_how_you_feeling_after_meal',
                         ['good_feeling', 'bad_feeling'],
                         ['So you are feeling', 'I\'m sorry to hear that'],
                         ['happy/behavior_1'])

    def interaction(self, question, intent, entities, responseText, gesture, listeningTimeout=5, repeatMax=2):
        # Ask how the patient is feeling
        self.nao_speech(question)
        self.general_repeat_Interaction(intent, entities, responseText, gesture, listeningTimeout=5, repeatMax=2)

    def general_repeat_Interaction(self, intent, entities, responseText, gesture, listeningTimeout=5, repeatMax=2):
        for i in range(0, repeatMax):
            # init emotion
            self.emotion = None
            self.emotionLock = Semaphore(0)

            # setting intent to listen to
            self.setAudioContext(intent)

            # listen to answer
            self.startListening()
            self.emotionLock.acquire(timeout=listeningTimeout)
            self.stopListening()
            # if emotion is still not set, wait some more
            if not self.emotion:
                self.emotionLock.acquire(timeout=1)

            # emotion is set
            if self.emotion:
                output = True
                if self.emotion == entities[0]:
                    self.say(responseText[0] + self.emotion)
                    # perform custom animation gesture installed on nao (from choreograph)
                    self.doGesture(gesture[0])
                else:
                    self.sayAnimated(responseText[1])
                return False
            else:
                # Ask patient to repeat
                self.nao_speech()
                self.setAudioContext(intent)

    # Default speech is 'repeat please'
    def nao_speech(self, speech='Could you repeat, please?!'):
        self.speechLock = Semaphore(0)
        self.sayAnimated(speech)
        self.speechLock.acquire()

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
