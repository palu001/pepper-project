class ActionFileCreator:
    def create_action(self, image, text, tts, buttons, filename="activity"):

        with open(filename, "w", encoding="utf-8") as f:
            # Sezione IMAGE
            f.write(f"IMAGE\n<*, *, *, *>:  {image}\n----\n")

            # Sezione TEXT
            f.write("TEXT\n")
            for key, value in text.items():
                key_str = ", ".join(key)
                f.write(f"<{key_str}>: {value}\n")
            f.write("----\n")

            # Sezione TTS
            f.write("TTS\n")
            for key, value in tts.items():
                key_str = ", ".join(key)
                f.write(f"<{key_str}>: {value}\n")
            f.write("----\n")

            # Sezione BUTTONS
            f.write("BUTTONS\n")
            for btn_key, translations in buttons.items():
                it_text = translations.get("it", "")
                en_text = translations.get("en", "")
                f.write(f"{btn_key}\n")
                f.write(f"<*,*,it,*>: {it_text}\n")
                f.write(f"<*,*,*,*>:  {en_text}\n")
            f.write("----\n")


creator = ActionFileCreator()

image = "/home/robot/playground/pepper-project/tablet/img/science.jpeg"

text = {
    ("*", "*", "it", "*"): "Cosa ti piacerebbe leggere?",
    ("*", "*", "*", "*"): "What would you like to read?"
}

tts = {
    ("*", "*", "it", "*"): "Cosa ti piacerebbe leggere?",
    ("*", "*", "*", "*"): "What would you like to read?"
}

buttons = {
    "politics": {"it": "Politica", "en": "Politics"},
    "sport": {"it": "Sport", "en": "Sport"},
    "health": {"it": "Salute", "en": "Health"},
    "science": {"it": "Scienza e Tecnologia", "en": "Science and Technologies"},
    "entertainment": {"it": "Intrattenimento", "en": "Entertainment"},
    "back": {"it": "Indietro", "en": "Back"}
}

creator.create_action(image, text, tts, buttons, filename="dynamic_action")
