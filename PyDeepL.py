import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import deepl
import yaml
import threading
import keyboard
import pystray
from PIL import Image

class PyDeepLApp:
    def __init__(self, root):
        self.root = root
        self.is_minimized = False
        self.tray_icon = None

        self.root.title('PyDeepL')
        self.root.geometry('600x480')
        self.root.iconbitmap(get_resource_path('pydeepl.ico'))
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)

        self.create_widgets()

    def create_widgets(self):
        self.source_lang_var = tk.StringVar()
        self.target_lang_var = tk.StringVar()

        languages = ['中文', '英语', '日语', '法语', '德语', '西班牙语', '意大利语', '荷兰语', '波兰语', '葡萄牙语', '俄语']

        self.source_lang_menu = ttk.Combobox(self.root, textvariable=self.source_lang_var, values=languages)
        self.source_lang_menu.grid(row=0, column=0, padx=5, pady=5)
        self.source_lang_menu.set('英语')

        self.swap_button = tk.Button(self.root, text='↔', command=self.swap_languages)
        self.swap_button.grid(row=0, column=1, padx=5, pady=5)

        self.target_lang_menu = ttk.Combobox(self.root, textvariable=self.target_lang_var, values=languages)
        self.target_lang_menu.grid(row=0, column=2, padx=5, pady=5)
        self.target_lang_menu.set('中文')

        self.input_box = scrolledtext.ScrolledText(self.root, height=20, width=40, wrap=tk.WORD)
        self.input_box.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        self.output_box = scrolledtext.ScrolledText(self.root, height=20, width=40, wrap=tk.WORD, state=tk.DISABLED)
        self.output_box.grid(row=1, column=3, columnspan=3, padx=5, pady=5)

        self.clear_button = tk.Button(self.root, text='清空', command=self.clear_text)
        self.clear_button.grid(row=2, column=0, padx=5, pady=5)

        self.translate_button = tk.Button(self.root, text='翻译', command=self.translate_text)
        self.translate_button.grid(row=2, column=1, padx=5, pady=5)

        self.copy_button = tk.Button(self.root, text='复制', command=self.copy_text)
        self.copy_button.grid(row=2, column=2, padx=5, pady=5)

        self.start_keyboard_thread()


    def swap_languages(self):
        source_lang = self.source_lang_var.get()
        target_lang = self.target_lang_var.get()
        self.source_lang_var.set(target_lang)
        self.target_lang_var.set(source_lang)

    def create_tray_icon(self):
        self.tray_icon = pystray.Icon('PyDeepL',
                                      Image.open(get_resource_path('pydeepl.ico')),
                                      title='PyDeepL',
                                      menu=pystray.Menu(
                                          pystray.MenuItem('打开窗口', self.restore_from_tray),
                                          pystray.MenuItem('退出', self.quit_program)
                                      ))

    def minimize_to_tray(self):
        if not self.is_minimized:
            self.hide_window()
            self.create_tray_icon()
            self.tray_icon.run_detached()
            self.is_minimized = True

    def hide_window(self):
        self.root.withdraw()

    def restore_from_tray(self, icon=None, item=None):
        self.root.deiconify()
        if self.tray_icon:
            self.tray_icon.stop()
        self.is_minimized = False

    def quit_program(self):
        if self.tray_icon:
            self.tray_icon.stop()
        keyboard.unhook_all()
        self.root.quit()

    def on_closing(self):
        self.minimize_to_tray()

    def set_hotkey(self):
        config = read_config()
        keyboard.add_hotkey(config['call_shortcut'], self.restore_from_tray)

    def start_keyboard_thread(self):
        threading.Thread(target=self.set_hotkey, daemon=True).start()

    def translate_text(self):
        input_text = self.input_box.get('1.0', tk.END).strip()
        if input_text:
            try:
                translated_text = translate(input_text)
                self.output_box.config(state=tk.NORMAL)
                self.output_box.delete('1.0', tk.END)
                self.output_box.insert(tk.END, translated_text)
                self.output_box.config(state=tk.DISABLED)
            except Exception as e:
                self.output_box.config(state=tk.NORMAL)
                self.output_box.delete('1.0', tk.END)
                self.output_box.insert(tk.END, f'翻译失败：{e}')
                self.output_box.config(state=tk.DISABLED)

    def clear_text(self):
        self.input_box.delete('1.0', tk.END)
        self.output_box.config(state=tk.NORMAL)
        self.output_box.delete('1.0', tk.END)
        self.output_box.config(state=tk.DISABLED)

    def copy_text(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_box.get('1.0', tk.END))


def read_config():
    config_file = 'PyDeeplConfig.yml'

    default_config = '''deepl_api: "enter deepl api key"
# 输入你的DeepL API密钥

call_shortcut: ctrl+space
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


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


if __name__ == '__main__':
    root = tk.Tk()
    app = PyDeepLApp(root)
    root.mainloop()