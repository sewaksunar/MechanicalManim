from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

class MyAwesomeScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService())

        with self.voiceover(text="This circle is drawn as I speak.") as tracker:
            self.play(Create(circle))