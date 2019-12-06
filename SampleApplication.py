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

        self.nao_speech([random.choice(self.hellos), 'My name is SARa and I am here to help.'])

        # Asking the patient how they are feeling
        self.interaction('How are you feeling today?',
                         'answer_how_you_feeling',
                         ['happy'],
                         [random.choice(self.positive_responses), random.choice(self.negative_responses)],
                         self.general_reaction,
                         [''])

        # Asking the patient how they felt after their last meal
        self.interaction(['How did your last meal make you feel?'],
                         'answer_how_you_feeling_after_meal',
                         ['good_feeling', 'bad_feeling'],
                         ["That\'s great to hear.", "That\'s okay. Maybe I could motivate with something!"],
                         self.after_meal_reaction,
                         [''])

        self.game()
        self.nao_speech(random.choice(self.byes))

    def gameLoop(self):
        self.nao_gesture('game/behavior_1')
        game = np.random.uniform(0, 3)
        if game < 1:
            self.doGesture('game/rock')
            self.nao_speech_simple("Rock!")
            self.played = "rock"
        elif game < 2:
            self.doGesture('game/paper')
            self.nao_speech_simple("Paper!")
            self.played = "paper"
        else:
            self.doGesture('game/scissors')
            self.nao_speech_simple("Scissors!")
            self.played = "scissors"

        self.interaction(
            question=f'So I got {self.played}. Did you win?',
            intent='binary_answer',
            entities=['yes', 'no'],
            responseText=[random.choice(self.win), random.choice(self.lose)],
            reaction_function=self.game_reaction,
            gesture="happy/behavior_1"
        )

    def game(self):
        self.interaction(
            question="Okay, let's forget the questions for a little bit and do something fun. "
                     "Would you like to play a game of rock paper scissors with me?",
            intent='binary_answer',
            entities=['yes', 'no'],
            responseText=["Yay, let's play!", "Aw, maybe another time then"],
            reaction_function=self.general_reaction,
            gesture=[""]
        )
        if self.intentName == 'yes':
            self.gameLoop()

            while (True):
                self.interaction(
                    question="Do you want to play again?",
                    intent='binary_answer',
                    entities=['yes', 'no'],
                    responseText=["Ok, let's play!", "Ok, we can play again later"],
                    reaction_function=self.general_reaction,
                    gesture=[""]
                )

                if self.intentName == 'yes':
                    self.gameLoop()
                else:
                    break

    def introduction(self, dialogue):
        self.nao_speech(dialogue)
        # self.doGesture()

    def interaction(self, question, intent, entities, responseText, reaction_function, gesture, listeningTimeout=5,
                    repeatMax=2):
        # Ask how the patient is feeling
        self.nao_speech(question)
        self.general_repeat_Interaction(intent, entities, responseText, reaction_function, gesture, listeningTimeout,
                                        repeatMax)

    def general_repeat_Interaction(self, intent, entities, responseText, reaction_function, gesture, listeningTimeout=5,
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

            if self.intentName:
                reaction_function(entities, responseText, gesture)
                break
            else:
                # Ask patient to repeat
                if (i != repeatMax - 1):
                    self.nao_speech()
                    self.setAudioContext(intent)
                elif (i == repeatMax - 1):
                    self.nao_speech("Sorry, I couldn't understand what you said, let's move on.")

    # Default speech is 'repeat please'
    def nao_speech(self, speech=['Could you repeat, please?!']):
        sentence = ""
        for phrase in speech:
            sentence = sentence + phrase

        self.speechLock = Semaphore(0)
        self.sayAnimated(sentence)
        self.speechLock.acquire()

    def nao_speech_simple(self, speech=['Could you repeat please']):
        sentence = ""
        for phrase in speech:
            sentence = sentence + phrase

        self.speechLock = Semaphore(0)
        self.say(sentence)
        self.speechLock.acquire()

    def general_reaction(self, entities, responseText, gesture):
        if self.intentName == entities[0]:
            self.nao_speech(responseText[0])
        else:
            self.nao_speech(responseText[1])

    def after_meal_reaction(self, entities, responseText, gesture):
        if self.intentName == entities[0]:
            self.nao_speech(responseText[0])
            self.nao_speech(self.compliments[np.random.randint(0, len(self.compliments))])
        else:
            self.nao_speech(responseText[1])
            self.nao_speech(self.quotes[np.random.randint(0, len(self.quotes))])

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

    def onAudioIntent(self, *args, intentName):
        if len(args) > 0:
            self.intentName = args[0]
            self.interactionLock.release()


# Run the application
sample = SampleApplication()
sample.main()
sample.stop()
