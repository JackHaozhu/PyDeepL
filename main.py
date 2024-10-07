import subprocess

import gui

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QIcon
import os
import sys
import deepl
import yaml
from pynput import keyboard
import pystray
from PIL import Image
import datetime

import win32gui, win32con, win32api


def read_config():
    config_file = 'PyDeeplConfig.yml'

    default_config = '''deepl_api: "enter deepl api key"
# 输入你的DeepL API密钥

call_shortcut: <ctrl>+<space>
'''
    if not os.path.exists(config_file):
        with open(config_file, 'w', encoding='utf-8') as file:
            file.write(default_config)

    with open(config_file, 'r', encoding='utf-8') as file:
        yml_config = yaml.safe_load(file)

    return yml_config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = gui.Ui_MainWindow()
        self.ui.setupUi(self)

        # 初始化
        self.setWindowTitle('PyDeepL')
        self.setWindowIcon(QIcon(':/Icon/pydeepl.ico'))
        self.on_combobox_changed()
        self.clear_text()

        # 托盘图标
        self.tray_icon = pystray.Icon('PyDeepL', Image.open(self.get_resource_path('./icon_resources/pydeepl.ico')),
                                      title='PyDeepL',
                                      menu=pystray.Menu(
                                          pystray.MenuItem('打开窗口', self.show_window),
                                          pystray.MenuItem('退出', self.exit_app)
                                      ))
        self.tray_icon.run_detached()

        # 绑定信号与槽
        self.ui.SourceComboBox.currentIndexChanged.connect(self.on_combobox_changed)
        self.ui.TargetComboBox.currentIndexChanged.connect(self.on_combobox_changed)
        self.ui.SwapButton.clicked.connect(self.swap_languages)
        self.ui.ClearButton.clicked.connect(self.clear_text)
        self.ui.TranslateButton.clicked.connect(self.translate_text)
        self.ui.CopyButton.clicked.connect(self.copy_text)
        self.ui.UploadFileButton.clicked.connect(self.select_and_translate_file)

        # 监听快捷键
        config = read_config()
        self.listener = keyboard.GlobalHotKeys({
            config['call_shortcut']: self.toggle_window
        })
        self.listener.start()

    def on_combobox_changed(self):
        source_index = self.ui.SourceComboBox.currentIndex()
        target_index = self.ui.TargetComboBox.currentIndex()

        for i in range(self.ui.TargetComboBox.count()):
            self.ui.SourceComboBox.model().item(i + 1).setEnabled(True)
            self.ui.TargetComboBox.model().item(i).setEnabled(True)

        if source_index == 0:
            self.ui.SourceComboBox.model().item(target_index + 1).setEnabled(False)
        else:
            self.ui.TargetComboBox.model().item(source_index - 1).setEnabled(False)
            self.ui.SourceComboBox.model().item(target_index + 1).setEnabled(False)

    def swap_languages(self):
        source_index = self.ui.SourceComboBox.currentIndex()
        target_index = self.ui.TargetComboBox.currentIndex()
        if source_index != 0:
            self.ui.SourceComboBox.setCurrentIndex(target_index + 1)
            self.ui.TargetComboBox.setCurrentIndex(source_index - 1)

    def clear_text(self):
        self.ui.InputTextEdit.clear()
        self.ui.OutputTextBrowser.clear()
        self.ui.InputTextEdit.setFocus()

    def translate_text(self):
        input_text = self.ui.InputTextEdit.toPlainText()
        if input_text:
            try:
                translated_text = self.translate(input_text)
                self.ui.OutputTextBrowser.clear()
                self.ui.OutputTextBrowser.setText(translated_text)
            except Exception as e:
                self.ui.OutputTextBrowser.clear()
                self.ui.OutputTextBrowser.setText(f'翻译失败：{e}')

    def copy_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.ui.OutputTextBrowser.toPlainText())

    def select_and_translate_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, '选择文件', '',
                                                   '可翻译文件 (*.txt *.doc *.docx *.pptx *.xlsx *.pdf *.htm *.html *.xlf *.xliff *.srt);;所有文件 (*)',
                                                   options=options)
        if file_path:
            directory, filename = os.path.split(file_path)
            name, ext = os.path.splitext(filename)
            timestamp = datetime.datetime.now().strftime('%y%m%d%H%M%S')
            new_file_name = f'{name}_translated_{timestamp}{ext}'
            save_path = os.path.join(directory, new_file_name)
            try:
                config = read_config()
                auth_key = config['deepl_api']
                target_lang = self.ui.TargetComboBox.currentIndex()

                target_map = ['ZH', 'EN-US', 'JA', 'FR', 'DE', 'IT', 'ES', 'PT-PT', 'RU']

                translator = deepl.Translator(auth_key)
                translator.translate_document_from_filepath(file_path, save_path, target_lang=target_map[target_lang])

                subprocess.run(f'explorer /select,"{save_path}"')
            except Exception as e:
                self.ui.OutputTextBrowser.setText(f'错误：{e}')

    def translate(self, text: str) -> str:
        config = read_config()
        auth_key = config['deepl_api']
        source_lang = self.ui.SourceComboBox.currentIndex()
        target_lang = self.ui.TargetComboBox.currentIndex()

        source_map = [None, 'ZH', 'EN', 'JA', 'FR', 'DE', 'IT', 'ES', 'PT', 'RU']
        target_map = ['ZH', 'EN-US', 'JA', 'FR', 'DE', 'IT', 'ES', 'PT-PT', 'RU']

        translator = deepl.Translator(auth_key)
        result = translator.translate_text(text,
                                           source_lang=source_map[source_lang],
                                           target_lang=target_map[target_lang])
        return result.text

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def get_resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath('.'), relative_path)

    def show_window(self, icon, item):
        self.show()

    def exit_app(self, icon, item):
        self.tray_icon.stop()
        QApplication.quit()

    def toggle_window(self):
        if not self.isVisible():
            self.show()
            self.raise_()
            self.activateWindow()
            self.ui.InputTextEdit.setFocus()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
# pyinstaller --onefile --windowed --add-data "gui.py;." --add-data "pydeepl_rc.py;." --add-data "icon_resources;icon_resources" main.py  --icon='icon_resources/pydeepl.ico' --name=PyDeepL
