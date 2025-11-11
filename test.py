from TTS.utils.synthesizer import Synthesizer
text = "嘿嘿～我是小新，今天要去幼稚园～"
synth = Synthesizer("model.pth", "config.json", None)
wav = synth.tts(text, speaker_name="Uma_Musume_Tokai_Teio")
synth.save_wav(wav, "xiaoxin_style.wav")