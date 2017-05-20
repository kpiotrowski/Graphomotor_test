from kivy.app            import App

from kivy.uix.boxlayout  import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout

import kivy.input.motionevent

from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.textinput  import TextInput
from kivy.uix.label      import Label
from kivy.uix.dropdown   import DropDown
from kivy.uix.splitter import Splitter
from kivy.uix.splitter import SplitterStrip
from kivy.graphics.transformation import Matrix

import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from kivy.base import EventLoop


import numpy as np
from matplotlib.mlab import griddata
from libs.garden.matplotlib.backend_kivy import FigureCanvasKivy,\
                            FigureManagerKivy, show, new_figure_manager,\
                            NavigationToolbar2Kivy
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.config import Config
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

from  kivy.graphics.vertex_instructions import Rectangle
import graphomotor
from matplotlib.colors import hsv_to_rgb
from matplotlib import pyplot as plt
from kivy.properties import OptionProperty, NumericProperty, ObjectProperty,\
    ListProperty

class MyPopUp(Popup):
    def __init__ (self,posX, posY, currentWidget,**kwargs):
        super(MyPopUp,self).__init__(**kwargs)
        showFile = Button(text="Load image",on_press=lambda btn:self.showImage())
        self.add_widget(showFile)
        self.width = 150
        self.currentWidget = currentWidget
        self.pos_hint = {'x': posX / Window.width, 'y': (posY - self.height) / Window.height}

    def showImage(self):
        # if (self.currentWidget.data is None):
        #     return

        self.currentWidget.data = graphomotor.read("dane/40080000000 (M)/03_40080000000_11MRLP.mtb")
        self.currentWidget.data = graphomotor.find_figures(self.currentWidget.data)
        self.currentWidget.data = graphomotor.create_image(self.currentWidget.data, show_speed=True,
                                             show_figure_box=True)
        image = hsv_to_rgb(self.currentWidget.data["image"])
        self.currentWidget.showImage(image)
        self.dismiss()


class MyScatterLayout(ScatterLayout):
    def __init__(self,**kwargs):
        super(MyScatterLayout,self).__init__(**kwargs)
        self.fig, self.ax = plt.subplots()
        self.fig.frameon = False
        self.ax.axis('off')
        self.add_widget(self.fig.canvas)
        self.keep_within_parent = True
        self.rescale_with_parent = True


class MainGrid(BoxLayout):
    def __init__ (self,**kwargs):
        super(MainGrid,self).__init__(**kwargs)
        self.minimum_width = 800
        self.minimum_height = 600


class MySplitter(Splitter):
    def __init__ (self,**kwargs):
        super(MySplitter,self).__init__(**kwargs)
        self.data = None
        self.fig, self.ax = plt.subplots()
        self.fig.frameon = False
        self.ax.axis('off')
        self.add_widget(self.fig.canvas)


    def showImage(self,image):
        self.ax.imshow(image)


    def on_touch_up(self, touch):
        if self.collide_point(touch.pos[0], touch.pos[1]):
            if 'right' in touch.button:
                menu = MyPopUp(touch.pos[0], touch.pos[1], self, title="Plot", size_hint=(None, None))
                menu.open()
            # elif "scrollup" in touch.button:
            #     self.scat.scale *= 1.1
            # elif "scrolldown" in touch.button:
            #     self.scat.scale /= 1.1
            # elif self.scat.collide_point(touch.pos[0], touch.pos[1]):
            #     return self.scat.on_touch_up(touch)


class MyAppGUI(App):

    def build(self):
        self.init()
        # return MainGrid(cols=2,rows=1)
        return MainGrid()

    def init(self):
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        Builder.load_file('gui/frontGUI.kv')



