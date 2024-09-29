import os
import sys
import tkinter as tk
from tkinter import scrolledtext

import deepl
import yaml


def read_config():
    config_file = 'PyDeeplConfig.yml'

    default_config = '''deepl_api: "enter deepl api key"
# 输入你的DeepL API密钥
'''
    if not os.path.exists(config_file):
        with open(config_file, 'w', encoding='utf-8') as file:
            file.write(default_config)

    with open(config_file, 'r', encoding='utf-8') as file:
        yml_config = yaml.safe_load(file)

    return yml_config


def translate(text: str) -> str:
    config = read_config()

    auth_key = config['deepl_api']  # Deepl Free API
    target_language = 'ZH'

    translator = deepl.Translator(auth_key)

    result = str(translator.translate_text(text, target_lang=target_language))
    return result


def translate_text():
    input_text = input_box.get('1.0', tk.END).strip()
    if input_text:
        try:
            translated_text = translate(input_text)
            output_box.config(state=tk.NORMAL)
            output_box.delete('1.0', tk.END)
            output_box.insert(tk.END, translated_text)
            output_box.config(state=tk.DISABLED)
        except Exception as e:
            output_box.config(state=tk.NORMAL)
            output_box.delete('1.0', tk.END)
            output_box.insert(tk.END, f'翻译失败：{e}')
            output_box.config(state=tk.DISABLED)


def clear_text():
    input_box.delete('1.0', tk.END)
    output_box.config(state=tk.NORMAL)
    output_box.delete('1.0', tk.END)
    output_box.config(state=tk.DISABLED)


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


if __name__ == '__main__':
    root = tk.Tk()
    icon_path = get_resource_path('pydeepl.ico')
    root.iconbitmap(icon_path)
    root.title('PyDeepL')
    root.geometry('500x400')

    input_label = tk.Label(root, text='请输入要翻译的文本：')
    input_label.pack(pady=5)

    input_box = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD)
    input_box.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

    translate_button = tk.Button(root, text='翻译', command=translate_text)
    translate_button.pack(pady=5)

    output_label = tk.Label(root, text='翻译结果：')
    output_label.pack(pady=5)

    output_box = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD, state=tk.DISABLED)
    output_box.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

    clear_button = tk.Button(root, text='清空', command=clear_text)
    clear_button.pack(pady=5)

    root.mainloop()
# pyinstaller --noconsole --onefile --icon='pydeepl.ico' --add-data 'pydeepl.ico;.' PyDeepLTk.py
