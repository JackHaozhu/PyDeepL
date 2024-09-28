import deepl


def translate(text: str) -> str:
    auth_key = 'abc55bf3-2226-4fb6-8208-12ba89ec65df:fx'  # Deepl Free API
    target_language = 'ZH'

    translator = deepl.Translator(auth_key)

    result = str(translator.translate_text(text, target_lang=target_language))
    return result


if __name__ == '__main__':
    while True:
        original_text = input('输入文本(输入quit以退出):\n')
        if original_text == 'quit':
            break
        print(translate(original_text))
        print()
# pyinstaller --onefile --icon='pydeepl.ico' main.py

