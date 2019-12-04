import AbstractApplication as Base
import random
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
                         self.feeling_reaction,
                         ['happy/behavior_1'])

        # Asking the patient how they felt after their last meal
        self.interaction(['How did you feel after your last meal?'],
                         'answer_how_you_feeling_after_meal',
                         ['good_feeling', 'bad_feeling'],
                         ['So you are feeling', 'I\'m sorry to hear that'],
                         self.after_meal_reaction,
                         ['happy/behavior_1'])

    def interaction(self, question, intent, entities, responseText, gesture, reaction_function, listeningTimeout=5,
                    repeatMax=2):
        # Ask how the patient is feeling
        self.nao_speech(question)
        self.general_repeat_Interaction(intent, entities, responseText, gesture, reaction_function, listeningTimeout,
                                        repeatMax)

    def general_repeat_Interaction(self, intent, entities, responseText, gesture, reaction_function, listeningTimeout=5,
                                   repeatMax=2):
        for i in range(0, repeatMax):
            # init emotion
            self.intentName = None
            self.interactionLock = Semaphore(0)

            # setting intent to listen to
            self.setAudioContext(intent)

            # listen to answer
            self.startListening()
            self.interactionLock.acquire(timeout=listeningTimeout)
            self.stopListening()
            # if emotion is still not set, wait some more
            if not self.intentName:
                self.interactionLock.acquire(timeout=1)

            # emotion is set
            if self.intentInfo:
                reaction_function(entities, responseText, gesture)

            if self.intentName:
                reaction_function(entities, responseText, gesture)
            else:
                # Ask patient to repeat
                if (i != repeatMax - 1):
                    self.nao_speech()
                    self.setAudioContext(intent)

    def game(self):
        self.nao_speech(speech="Let's play a game of rock paper scissors.")

        self.gestureLock = Semaphore(0)
        self.doGesture('game/behavior_1')
        self.gestureLock.acquire()

        game = np.random.uniform(0, 3)
        if game < 1:
            self.say("Rock!")
            self.doGesture('rock/rock')
            self.played = "rock"
        elif game < 2:
            self.say("Paper!")
            self.doGesture('paper/paper')
            self.played = "paper"
        else:
            self.say("Scissors!")
            self.doGesture('scissors/scissors')
            self.played = "scissors"

        self.played = "rock"


    def nao_speech(self, speech=['Could you repeat, please?!']):
        sentance = ""
        for phrase in speech:
            sentance = sentance + phrase

        self.speechLock = Semaphore(0)
        self.sayAnimated(sentance)
        self.speechLock.acquire()


    def feeling_reaction(self, entities, responseText, gesture):
        if self.intentInfo == entities[0]:
            self.say(responseText[0] + self.intentInfo)
            self.doGesture(gesture[0])
        else:
            self.sayAnimated(responseText[1])


    def after_meal_reaction(self, entities, responseText, gesture):
        if self.intentInfo == entities[0]:
            self.say(responseText[0] + self.intentInfo)
            self.sayAnimated(self.compliments[np.random.randint(0, len(self.compliments))])
        else:
            self.say(responseText[1])
            self.sayAnimated(self.quotes[np.random.randint(0, len(self.quotes))])


    def nao_gesture(self, gesture):
        self.gestureLock = Semaphore(0)
        self.doGesture(gesture)
        self.gestureLock.acquire()


    def onRobotEvent(self, event):
        if event == 'LanguageChanged':
            self.langLock.release()
        elif event == 'TextDone':
            self.speechLock.release()
        elif event == 'GestureDone':
            self.gestureLock.release()


    def onAudioIntent(self, *args, intentInfo):
        if len(args) > 0:
            self.intentInfo = args[0]
            self.interactionLock.release()

# Run the application
sample = SampleApplication()
sample.main()
sample.stop()
