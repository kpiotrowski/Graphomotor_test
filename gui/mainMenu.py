from kivy.app            import App

from kivy.uix.boxlayout  import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout

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


from libs.garden.filebrowser import FileBrowser
from os.path import sep, expanduser, isdir, dirname, exists
import platform
from kivy.uix.screenmanager import ScreenManager, Screen, TransitionBase, SlideTransition
from kivy.graphics.context_instructions import Color
from kivy.uix.checkbox import CheckBox
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView

class MyFileBrowser(FileBrowser):
    def __init__(self,**kwargs):
        super(MyFileBrowser,self).__init__(**kwargs)
        if not platform.system() == 'Linux':
            user_path = dirname(expanduser('.'))
        else:
            user_path = expanduser('.')
        if isdir(user_path):
            self.path = user_path
            self.select_string = "Load"
            self.favorites =[(user_path, 'Project')]
        self.currentWidget = None
        self.load = True
        self.bind(
                    on_success=self.loadFile,
                    on_canceled=self._fbrowser_canceled)

    def loadFile(self,instance):
        if exists(instance.filename):
            extension = instance.filename.split('.')[-1]
            if extension == "mtb":
                self.currentWidget.data = graphomotor.read(instance.filename)
                self.currentWidget.data = graphomotor.find_figures(self.currentWidget.data)
                self.currentWidget.showImage()
                self.currentWidget.showGrid()
                self.goBack()
            # elif extension == "gmt":
            #     with open(instance.filename) as dict:
            #         self.currentWidget.data = ast.literal_eval(dict.read())
            #     self.currentWidget.showImage()
            #     self.currentWidget.showGrid()
            #     self.goBack()

    def saveFile(self,instance):
        directory = ""
        folders = instance.filename.split(sep)
        if len(folders) > 2:
            for fd in folders[:-1]:
                directory += fd + sep
            if isdir(directory):
                graphomotor.save_metrics(self.currentWidget.data,instance.filename)
                self.goBack()

    def goBack(self):
        mainScreenManager.current = "main"

    def _fbrowser_canceled(self,instance):
        return self.goBack()


class InfoPopUp(Popup):
    def __init__(self, posX, posY, currentWidget, **kwargs):
        super(InfoPopUp, self).__init__(**kwargs)
        self.pos_hint = {'x': posX / Window.width, 'y': (posY - self.height) / Window.height}
        self.add_widget(Label(text="test"))


class MyCheckBoxLayout(RelativeLayout):
    def __init__(self, currentWidget,name, var, center_x,group = None, **kwargs):
        super(MyCheckBoxLayout, self).__init__(**kwargs)
        self.currentWidget = currentWidget
        showSpeed = CheckBox(pos_hint= {'center_x': 0.1, 'center_y': 0.5})
        showSpeed.active = self.currentWidget.imageParam[var]
        if group is not None:
            showSpeed.group = group
            showSpeed.bind(active=lambda c,v:self.toggleButton(c, v, var))
            showSpeed.allow_no_selection = False
        else:
            showSpeed.bind(active=lambda c,v:self.checkBoxChange(c,v,var))
        self.add_widget(showSpeed)
        checkboxLabel = Label(text=name,pos_hint= {'center_x': center_x, 'center_y': 0.5})
        self.add_widget(checkboxLabel)


    def checkBoxChange(self, checkbox, value, var):
        self.currentWidget.imageParam[var] = value
        self.currentWidget.showImage()


    def toggleButton(self, checkbox, value, var):
        if value == False:
            return
        self.currentWidget.imageParam["showwidth"] = False
        self.currentWidget.imageParam["showheight"] = False
        self.currentWidget.imageParam["showPress"] = False
        self.checkBoxChange(checkbox,value,var)




class MyPopUp(Popup):
    def __init__ (self,posX, posY, currentWidget,**kwargs):
        super(MyPopUp,self).__init__(**kwargs)
        self.currentWidget = currentWidget
        newLayout = BoxLayout(orientation='vertical')
        self.width = 180
        self.height = 290
        changeView = Button(text="Change view")
        changeView.bind(on_press=lambda btn:self.changeView())
        newLayout.add_widget(changeView)
        if len(mainScreenManager.mainScreen.grid.spliters) > 1:
            removeSplitt = Button(text="Remove view", on_press=lambda btn:self.removeSplitter())
            newLayout.add_widget(removeSplitt)
        else:
            addSplitt = Button(text="Add view",on_press=lambda btn: self.addSplitter())
            newLayout.add_widget(addSplitt)
        self.add_widget(newLayout)
        showFile = Button(text="Load test", on_press=lambda btn:self.loadFiles())
        newLayout.add_widget(showFile)
        if self.currentWidget.data is not None:
            saveFile = Button(text="Save test", on_press=lambda btn:self.saveFiles())
            newLayout.add_widget(saveFile)
            self.height = self.height + 40
        self.pos_hint = {'x': posX / Window.width, 'y': (posY - self.height) / Window.height}
        resetButton = Button(text="Reset", on_press=lambda btn: self.resetImage())
        newLayout.add_widget(resetButton)
        newLayout.add_widget(MyCheckBoxLayout(self.currentWidget,"Show speed","showspeed",0.5))
        newLayout.add_widget(MyCheckBoxLayout(self.currentWidget,"Show boxes", "showboxes", 0.5))
        newLayout.add_widget(MyCheckBoxLayout(self.currentWidget,"Show pressure","showPress",0.6,group="image"))
        newLayout.add_widget(MyCheckBoxLayout(self.currentWidget,"Show width","showwidth",0.5,group="image"))
        newLayout.add_widget(MyCheckBoxLayout(self.currentWidget,"Show height","showheight",0.5,group="image"))

    def resetImage(self):
        self.currentWidget.showImage()
        self.dismiss()

    def changeView(self):
        self.currentWidget.viewImage = not self.currentWidget.viewImage
        self.currentWidget.changeView()
        self.dismiss()

    def addSplitter(self):
        mainScreenManager.mainScreen.grid.addSplitter(True)
        mainScreenManager.mainScreen.grid.resizeSplitters(Window.size[0])
        self.dismiss()

    def removeSplitter(self):
        for split in mainScreenManager.mainScreen.grid.spliters:
            if split == self.currentWidget:
                mainScreenManager.mainScreen.grid.removeSplitter(self.currentWidget)
                self.dismiss()
                break
        mainScreenManager.mainScreen.grid.spliters[0].strip_size = 0
        mainScreenManager.mainScreen.grid.resizeSplitters(Window.size[0])

    def swapScreen(self):
        mainScreenManager.fileScreen.filesBrow.currentWidget = self.currentWidget
        mainScreenManager.current = "files"

    def saveFiles(self):
        if self.currentWidget.data is not None:
            mainScreenManager.fileScreen.filesBrow.select_string = "Save"
            if mainScreenManager.fileScreen.filesBrow.load:
                mainScreenManager.fileScreen.filesBrow.unbind(on_success=mainScreenManager.fileScreen.filesBrow.loadFile)
                mainScreenManager.fileScreen.filesBrow.bind(on_success=mainScreenManager.fileScreen.filesBrow.saveFile)
            mainScreenManager.fileScreen.filesBrow.load = False
            self.swapScreen()
        self.dismiss()

    def loadFiles(self):
        mainScreenManager.fileScreen.filesBrow.select_string = "Load"
        if mainScreenManager.fileScreen.filesBrow.load:
            mainScreenManager.fileScreen.filesBrow.unbind(on_success=mainScreenManager.fileScreen.filesBrow.saveFile)
            mainScreenManager.fileScreen.filesBrow.bind(on_success=mainScreenManager.fileScreen.filesBrow.loadFile)
        mainScreenManager.fileScreen.filesBrow.load = True
        self.swapScreen()
        self.dismiss()


class GridLabel(Label):
    def __init__(self,background=None, **kwargs):
        super(GridLabel, self).__init__(**kwargs)
        if background is None:
            self.background = [0.0,0.0,0.0,1.0]
        else:
            self.background = background

    def on_size(self, *args):
        self.canvas.before.clear()
        r, g, b, a = self.background
        with self.canvas.before:
            Color(r, g, b, a)
            Rectangle(pos=self.pos, size=self.size)


class MySplitter(Splitter):
    def __init__ (self,viewImage=True,min=0,showStrip = True,**kwargs):
        super(MySplitter,self).__init__(**kwargs)
        # self.max_size = Window.width - min
        self.min_size = min
        self.keep_within_parent = True
        self.rescale_with_parent = True
        if not showStrip:
            self.strip_size = 0
        self.data = None
        self.setCanvas()
        self.setGrid()
        self.pressedLeft = None
        self.rangeX = 1
        self.scale = 30
        self.showSpeed = True
        self.imageParam = {
            "showspeed": False,
            "showboxes": False,
            "showwidth": False,
            "showheight": False,
            "showPress": True
        }
        self.viewImage = True
        self.changeView(empty=True)
        self.bind(size=lambda x,y: self.posGrid())
        # self.showGrid()

    def posGrid(self):
        self.grid.pos = (self.width *0.1,0.0)

    def changeView(self,empty=False):
        if empty is not True:
            self.clear_widgets()
        if self.viewImage:
            self.add_widget(self.fig.canvas)
        else:
            self.add_widget(self.scrollInfo)

    def setCanvas(self):
        print(self.width)
        self.fig, self.ax = plt.subplots()
        self.fig.frameon = False
        self.ax.axis('off')
        # self.add_widget(self.fig.canvas)

    def setGrid(self):
        self.scrollInfo = ScrollView(do_scroll_x=True, do_scroll_y=True)
        self.grid = BoxLayout(orientation="vertical",size_hint=(1.0,None))
        self.grid.padding = [20,10,20,5]
        # self.grid = GridLayout(cols=2,rows=10,size_hint=(1.0,None))
        self.scrollInfo.add_widget(self.grid)


    def showGrid(self):
        self.grid.add_widget(Widget())
        self.grid.clear_widgets()
        self.grid.height = 5000
        # self.addText(["test1","test2"])
        self.addText([self.data["file_name"]])
        self.addText(["Gender:",self.data["gender"]])
        self.addInfo(self.data)
        for fig in self.data["figures"]:
            self.addText([fig["type"]])
            self.addInfo(fig)

    def addInfo(self,data):
        self.addText(["Maximum force:", "{0:.3f}".format(data["max_force"])])
        self.addText(["Minimum force:", "{0:.3f}".format(data["min_force"])])
        self.addText(["Average force:", "{0:.3f}".format(data["avg_force"])])
        self.addText(["Maximum speed:", "{0:.3f}".format(data["max_speed"])])
        self.addText(["Average speed:", "{0:.3f}".format(data["avg_speed"])])
        self.addText(["Line breaks:", "{0:.3f}".format(data["line_breaks"])])
        self.addText(["Average width:", "{0:.3f}".format(data["avg_width"])])
        self.addText(["Average height:", "{0:.3f}".format(data["avg_height"])])
        self.addText(["Average height:", "{0:.0f}".format(data["time"])])

    def addText(self,labels):
        box = BoxLayout(spacing=5)
        gray = 0.2
        if len(labels) > 1:
            box.padding = [0,0,0,5]
        else:
            box.padding = [0,15,0,3]
            gray = 0.7
        # box = GridLayout(cols=len+(labels))
        for lab in labels:
            # lb = GridLabel(text=lab,background=[gray,gray,gray,1.0],pos_hint={'x':.1,'y':.1},size_hint=(0.8,0.8))
            lb = GridLabel(text=lab,background=[gray,gray,gray,1.0])
            # box.add_widget(lb)
            box.add_widget(lb)
            gray +=0.2
        self.grid.add_widget(box)

    def showImage(self):
        if self.data is None:
            return
        max_force = 0
        max_speed = 0
        grid = mainScreenManager.mainScreen.grid
        for split in grid.spliters:
            if split.data is None:
                max_force = None
                max_speed = None
                break
            if 'max_force' in split.data:
                max_force = max(max_force,split.data['max_force'])
            if 'max_speed' in split.data:
                max_speed = max(max_speed,split.data['max_speed'])
        if max_force == 0:
            max_force = None
        if max_speed == 0:
            max_speed = None
        self.data = graphomotor.create_image(self.data,scale=self.scale, show_speed=self.imageParam["showspeed"],
                                             show_figure_box=self.imageParam["showboxes"],show_width=self.imageParam["showwidth"],show_height=self.imageParam["showheight"]
                                             ,max_speed=max_speed,max_force=max_force)
        image = hsv_to_rgb(self.data["image"])
        self.ax.cla()
        self.ax.axis('off')
        self.ax.imshow(image)
        cur_xlim = self.ax.get_xlim()
        self.rangeX = cur_xlim[1]-cur_xlim[0]
        self.fig.canvas.draw()


    def on_touch_up(self, touch):
        if self.viewImage:
            self.pressedLeft = None
            self.fig.canvas.draw()

    def on_touch_move(self, touch):
        if self.pressedLeft is not None:
            x0, y0,x1,y1, posX, posY = self.pressedLeft
            moveScale = 0.7
            moveScale *= (x1-x0)/self.rangeX
            dx = touch.x - posX
            dy = touch.y - posY
            dx *= -moveScale
            dy *= moveScale
            self.ax.set_xlim([x0+dx,x1+dx])
            self.ax.set_ylim([y0 + dy, y1 + dy])
            self.fig.canvas.draw()

    def on_touch_down(self, touch):
        posX = touch.pos[0]
        posY = touch.pos[1]
        if self.collide_point(posX, posY):
            self.focus = False
            if 'right' in touch.button:
                menu = MyPopUp(posX, posY, self, title="Plot", size_hint=(None, None))
                menu.open()
            if self.viewImage:
                if "scrollup" in touch.button:
                    if self.data is not None:
                        self.zoom(posX, posY, self.ax, self.fig, "scrollup")
                elif "scrolldown" in touch.button:
                    if self.data is not None:
                        self.zoom(posX, posY, self.ax, self.fig, "scrolldown")
                elif 'left' in touch.button:
                    if self.data is not None:
                        cur_xlim = self.ax.get_xlim()
                        cur_ylim = self.ax.get_ylim()
                        self.pressedLeft = cur_xlim[0], cur_ylim[0], cur_xlim[1], cur_ylim[1], posX, posY
            super(MySplitter,self).on_touch_down(touch)

    def checkFig(self,posX,posY):
        if self.data is None:
            return False
        cur_limx = self.ax.get_xlim()
        cur_limy = self.ax.get_ylim()
        # print([self.data['image'].shape[0],cur_limx[1]-cur_limx[0]])
        # print([self.data['image'].shape[1], cur_limy[1] - cur_limy[0]])
        x = posX + cur_limx[0]
        y = posY + cur_limy[1]
        y *= self.scale
        x *= self.scale
        print("x,y:")
        print([x,y])
        print("\n")
        for fig in self.data["figures"]:
            figX0 = fig['pos_x'][0]
            figX1 = fig['pos_x'][1]
            figY0 = fig['pos_y'][0]
            figY1 = fig['pos_y'][1]
            # print([x,fig['pos_x'][1]])
            print(fig['type'])
            print([fig['pos_x'][0], fig['pos_x'][1]])
            print([fig['pos_y'][0],fig['pos_y'][1]])
            print("\n")
            if figX0 <= x <= figX1 and figY0 <= y <= figY1:
                print("\n")
                print(fig['type'])
                print("\n")
                return True
        return False

    def zoom(self,posX,posY,ax,fig,event, baseScale = 1.5):
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
        xmouse = posX  # get event x location
        ymouse = posY  # get event y location
        cur_xcentre = (cur_xlim[1] + cur_xlim[0]) * .5
        cur_ycentre = (cur_ylim[1] + cur_ylim[0]) * .5
        xdata = cur_xcentre + 0.25 * (xmouse - cur_xcentre)
        ydata = cur_ycentre + 0.25 * (ymouse - cur_ycentre)
        if event == 'scrollup':
            # deal with zoom in
            scale_factor = 1/baseScale
        elif event == 'scrolldown':
            # deal with zoom out
            scale_factor = baseScale
        else:
            # deal with something that should never happen
            scale_factor = 1
        # set new limits
        ax.set_xlim([xdata - cur_xrange*scale_factor,
                     xdata + cur_xrange*scale_factor])
        ax.set_ylim([ydata - cur_yrange*scale_factor,
                     ydata + cur_yrange*scale_factor])
        fig.canvas.draw() # force re-draw


class MainGrid(BoxLayout):
    def __init__ (self,**kwargs):
        super(MainGrid,self).__init__(**kwargs)
        self.min_view_size = 100
        self.spliters = []
        self.viewImage = False
        self.addSplitter(False)


    def addSplitter(self,showStrip):
        split = MySplitter(viewImage=self.viewImage, min=self.min_view_size, showStrip=showStrip)
        self.spliters.append(split)
        self.add_widget(split)
        for sp in self.spliters:
            sp.size_hint = (0.5,1.0)


    def removeSplitter(self,split):
        self.spliters.remove(split)
        self.remove_widget(split)
        self.spliters[0].size_hint = (1.0,1.0)


    def resizeSplitters(self,width):
        for split in self.spliters:
            if len(self.spliters) > 1:
                split.max_size = width - self.min_view_size
                split.min_size = self.min_view_size
            else:
                split.max_size = width
                split.min_size = 0


class MainScreen(Screen):
    def __init__(self,**kwargs):
        super(MainScreen,self).__init__(**kwargs)
        self.grid = MainGrid()
        self.add_widget(self.grid)


class FileScreen(Screen):
    def __init__(self,**kwargs):
        super(FileScreen,self).__init__(**kwargs)
        self.filesBrow = MyFileBrowser()
        self.add_widget(self.filesBrow)



class MyScreenManager(ScreenManager):
    def __init__(self,**kwargs):
        super(MyScreenManager,self).__init__(**kwargs)
        self.mainScreen = MainScreen(name="main")
        self.fileScreen = FileScreen(name="files")
        self.add_widget(self.mainScreen)
        self.add_widget(self.fileScreen)
        self.current = "main"
        self.minimum_width = 800
        self.minimum_height = 600

        self.ctrl = False
        self._keyboard = Window.request_keyboard(None, self)
        self._keyboard.bind(on_key_down=self.on_key_down)
        self._keyboard.bind(on_key_up=self.on_key_up)


    def keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard.unbind(on_key_up=self.on_key_up)
        self._keyboard = None


    def on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == "lctrl" or keycode[1] == "rctrl":
            self.ctrl = True


    def on_key_up(self, keyboard, keycode):
        if keycode[1] == "lctrl" or keycode[1] == "rctrl":
            self.ctrl = False


mainScreenManager = MyScreenManager()


class MyAppGUI(App):

    def build(self):
        def windowResize(window, width, height):
            mainScreenManager.mainScreen.grid.resizeSplitters(width)

        self.init()
        Window.bind(on_resize=windowResize)
        # return MainGrid(cols=2,rows=1)
        return mainScreenManager
        # return MainGrid()

    def init(self):
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        Builder.load_file('gui/frontGUI.kv')



