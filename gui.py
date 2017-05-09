import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os.path as os
from tkinter import messagebox
from collections import defaultdict
from matplotlib.colors import hsv_to_rgb
from matplotlib import pyplot as plt
import graphomotor




class MainGui(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.wm_title(self, "Graphomotor")
        self.data = None
        self.panesCount = 0
        self.panes = []
        self.path = "No file"
        # self.addPane(self)
        # self.panes[0].pack(fill=tk.BOTH, expand=1)
        self.basicMenu()

    def basicMenu(self):
        padx = 10
        pady = 10
        controller = ttk.Frame(self)
        controller.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        leftSide = ttk.Frame(controller)
        leftSide.grid(row=1, column=1)
        pathFrame = ttk.Labelframe(leftSide, text="File directory")
        pathFrame.grid(row=1, column=1, padx=padx, pady=pady)
        buttonChoose = ttk.Button(pathFrame, text="Load file", command=lambda: self.chooseFile())
        buttonChoose.grid(row=1, column=1, padx=padx, pady=pady)
        self.pathLabel = ttk.Label(pathFrame, text=self.path)
        self.pathLabel.grid(row=1, column=2, padx=padx, pady=pady, sticky=tk.W)
        container = ttk.Frame(self)
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.graph = Graph(container)
        optionFrame = ttk.Labelframe(leftSide, text="Options")
        optionFrame.grid(row=2, column=1, padx=padx, pady=pady, sticky=tk.W)
        self.speedVar = tk.BooleanVar()
        showSpeed = MyCheckButton(optionFrame, text="Show speed", variable=self.speedVar, onvalue=True, offvalue=False, command=lambda: self.createImage())
        showSpeed.grid(row=1, column=1, padx=padx, pady=pady, sticky=tk.W)
        self.boxesVar = tk.BooleanVar()
        showBoxes = MyCheckButton(optionFrame, text="Show figure boxes", variable=self.boxesVar, onvalue=True, offvalue=False, command=lambda: self.createImage())
        showBoxes.grid(row=1, column=2, padx=padx, pady=pady, sticky=tk.W)
        showSpeed.select()
        showBoxes.select()
        rightSide = ttk.Frame(controller)
        rightSide.grid(row=1, column=2)
        infoFrame = ttk.Labelframe(rightSide, text="Info")
        infoFrame.pack(padx=padx, pady=pady)

        textWidth = 20

        info1 = ttk.Labelframe(infoFrame, text="MAX nacisk")
        info1.grid(row=1, column=1, padx=padx/2.0, pady=pady/2.0, sticky=tk.W)
        self.infoText1 = tk.Label(info1, text="")
        self.infoText1.pack()

        info2 = ttk.Labelframe(infoFrame, text="MIN nacisk")
        info2.grid(row=2, column=1, padx=padx / 2.0, pady=pady / 2.0, sticky=tk.W)
        self.infoText2 = tk.Label(info2, text="")
        self.infoText2.pack()

        info3 = ttk.Labelframe(infoFrame, text="AVG nacisk")
        info3.grid(row=3, column=1, padx=padx / 2.0, pady=pady / 2.0, sticky=tk.W)
        self.infoText3 = tk.Label(info3, text="")
        self.infoText3.pack()

        info4 = ttk.Labelframe(infoFrame, text="MAX predkosc")
        info4.grid(row=1, column=2, padx=padx / 2.0, pady=pady / 2.0, sticky=tk.W)
        self.infoText4 = tk.Label(info4, text="")
        self.infoText4.pack()


        info5 = ttk.Labelframe(infoFrame, text="AVG predkosc")
        info5.grid(row=2, column=2, padx=padx / 2.0, pady=pady / 2.0, sticky=tk.W)
        self.infoText5 = tk.Label(info5, text="")
        self.infoText5.pack()

        info6 = ttk.Labelframe(infoFrame, text="Oderwania")
        info6.grid(row=3, column=2, padx=padx / 2.0, pady=pady / 2.0, sticky=tk.W)
        self.infoText6 = tk.Label(info6, text="")
        self.infoText6.pack()


        info7 = ttk.Labelframe(infoFrame, text="Droga rysowania")
        info7.grid(row=1, column=3, padx=padx / 2.0, pady=pady / 2.0, sticky=tk.W)
        self.infoText7 = tk.Label(info7, text="")
        self.infoText7.pack()


        info8 = ttk.Labelframe(infoFrame, text="AVG szerokość kątowa")
        info8.grid(row=2, column=3, padx=padx / 2.0, pady=pady / 2.0, sticky=tk.W)
        self.infoText8 = tk.Label(info8, text="")
        self.infoText8.pack()

        info9 = ttk.Labelframe(infoFrame, text="AVG wysokość kątowa")
        info9.grid(row=3, column=3, padx=padx / 2.0, pady=pady / 2.0, sticky=tk.W)
        self.infoText9 = tk.Label(info9, text="")
        self.infoText9.pack()

    def addPane(self, pane):
        print(self.panesCount)
        newPane = ttk.PanedWindow(pane)
        newPane.pack(fill=tk.BOTH, expand=True)

        self.panes.append(newPane)
        self.panesCount += 1
        buttons = ttk.Frame(newPane)
        # buttons.pack(fill=tk.BOTH, expand = True)
        addPaneButton = ttk.Button(buttons, text="Add", command=lambda: self.addPane(newPane), width=20)
        addPaneButton.grid(row=1,column=1)
        newPane.add(buttons)
        # addPaneButton.grid(row=1, column=1)


    # def addGraph(self,pane):
    #     newGraph()


    def chooseFile(self):
        # self.images.config(state="readonly")
        self.path = filedialog.askopenfilename()
        if self.path == () or self.path == "":
            self.path = ""
            self.data = None
            return
        self.pathLabel.config(text=self.path)
        self.data = graphomotor.read(self.path)
        self.data = graphomotor.find_figures(self.data)
        self.createImage()

    def createImage(self):
        if(self.data is None):
            return
        self.data = graphomotor.create_image(self.data, show_speed=self.speedVar.get(), show_figure_box=self.boxesVar.get())
        self.graph.changePlot(hsv_to_rgb(self.data["image"]))

        self.infoText1.config(text="{0:.3f}".format(self.data["max_force"]))
        self.infoText2.config(text="{0:.3f}".format(self.data['min_force']))
        self.infoText3.config(text="{0:.3f}".format(self.data["avg_force"]))
        self.infoText4.config(text="{0:.3f}".format(self.data['max_speed']))
        self.infoText5.config(text="{0:.3f}".format(self.data['avg_speed']))
        self.infoText6.config(text=self.data["line_breaks"])
        self.infoText7.config(text="{0:.3f}".format(self.data["line_len"]))
        self.infoText8.config(text="{0:.3f}".format(self.data["avg_width"]))
        self.infoText9.config(text="{0:.3f}".format(self.data["avg_height"]))
        # print("Maksymalny nacisk: "+str(self.data["max_force"]))
        # print("Minimalny nacisk: "+str(self.data['min_force']))
        # print("Średni nacisk: "+str(self.data["avg_force"]))
        # print("Maksymalna prędkość: "+str(self.data['max_speed']))
        # print("Średnia prędkość: "+str(self.data['avg_speed']))
        # print("Oderwania: " +str(self.data["line_breaks"]))
        # print("Droga rysowania: "+str(self.data["line_len"]))
        # print("Średnia szerokość kątowa: "+str(self.data["avg_width"]))
        # print("Średnia wysokość kątowa: "+str(self.data["avg_height"]))


class Graph(Figure):
    plot = None
    image = None
    canvas = None

    def __init__(self, pane, image=None, figsize=(10,10), dpi=100):
        Figure.__init__(self, figsize=figsize, dpi=dpi)
        self.canvas = FigureCanvasTkAgg(self, pane)
        self.plot = self.add_subplot(1, 1, 1)
        self.changePlot(image)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def changePlot(self, image):
        self.image = image
        if(self.image is not None):
            self.plot.imshow(image)
        self.canvas.show()


def digitChecker(keep):
    table = defaultdict(type(None))
    table.update({ord(c): c for c in keep})
    return table


class MyCheckButton(tk.Checkbutton):
    def __init__(self,*args,**kwargs):
        self.var = kwargs.get('variable',tk.BooleanVar())
        kwargs['variable'] = self.var
        tk.Checkbutton.__init__(self,*args,**kwargs)

    def is_checked(self):
        return self.var.get()

