from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView

class UI(BoxLayout):

    pass


class ButtonList(BoxLayout):



    def importFile(self):
        App.get_running_app().importFile()

    def clear(self):
        App.get_running_app().clear()

    pass


class DisplayImage(AnchorLayout):
    pass


class labelcode(Label):
    pass

class DisplayCode(ScrollView):

    pass


class SysMessage(Label):

    pass


class Filechooser(BoxLayout):

    def select(self, *args):
        try:
            App.get_running_app().fileName = args[1][0]
            A.filename = args[1][0]
            print('filename = ', A.fileName)
            A.openFolder()
        except:
            pass

class AFDT(App):
    def __init__(self, **kwargs):

        super(AFDT, self).__init__(**kwargs)
        self.code = ''
        self.sysMessage = 'Welcome to AFDT'
        self.fileName = ''
        self.hasOpenFolder = False
       # Window.bind(on_key_down=self._on_keyboard_down)

    #你想顯示啥用這個
    def setSystemMessage(self,text):
        self.UI.sysMessageLabel.text = text

    def build(self):
        self.UI = UI()
        return self.UI

    def importFile(self):
        if self.fileName == '':
            self.openFolder()
            self.setSystemMessage('No file path exist')
        else:
            self.setSystemMessage('import : ' + self.fileName + 'success')
            with open(self.fileName,'r') as f:
                self.code = f.read()
                self.UI.displayCode.text = self.code

    def clear(self):
        self.setSystemMessage('Clear file success')
        self.UI.displayCode.text = ''
        self.fileName = ''
        self.code = ''
    def openFolder(self):
        print(self.hasOpenFolder)
        if self.hasOpenFolder:
            self.UI.fileChooser.size_hint_x = None
            self.UI.fileChooser.width = 0
            self.hasOpenFolder = False
            self.UI.displayCode.size_hint_x = 0.4
        else:
            self.UI.displayCode.size_hint_x = None
            self.UI.displayCode.width = 0
            self.UI.fileChooser.size_hint_x = 0.4
            self.hasOpenFolder = True

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if len(modifiers) > 0 and modifiers[0] == 'ctrl':
            if text == 'o':  # Ctrl+a
                print('open folder')
                self.setSystemMessage('open folder')
                self.openFolder()
            elif text == 's':
                self.setSystemMessage('save img')
                print('save img')
            elif text == 'p':
                self.setSystemMessage('analyze code')
                print('analyze code')


A = AFDT()
A.run()
