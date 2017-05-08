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
        pathFrame = ttk.Labelframe(controller, text="File directory")
        pathFrame.grid(row=1, column=1, padx=padx, pady=pady, sticky=tk.W)
        buttonChoose = ttk.Button(pathFrame, text="Load file", command=lambda: self.chooseFile())
        buttonChoose.grid(row=1, column=1, padx=padx, pady=pady)
        self.pathLabel = ttk.Label(pathFrame, text=self.path)
        self.pathLabel.grid(row=1, column=2, padx=padx, pady=pady, sticky=tk.W)
        container = ttk.Frame(self)
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.graph = Graph(container)
        optionFrame = ttk.Labelframe(controller, text="Options")
        optionFrame.grid(row=2, column=1, padx=padx, pady=pady, sticky=tk.W)
        self.speedVar = tk.BooleanVar()
        showSpeed = MyCheckButton(optionFrame, text="Show speed", variable=self.speedVar, onvalue=True, offvalue=False, command=lambda: self.createImage())
        showSpeed.grid(row=1, column=1, padx=padx, pady=pady, sticky=tk.W)
        self.boxesVar = tk.BooleanVar()
        showBoxes = MyCheckButton(optionFrame, text="Show figure boxes", variable=self.boxesVar, onvalue=True, offvalue=False, command=lambda: self.createImage())
        showBoxes.grid(row=1, column=2, padx=padx, pady=pady, sticky=tk.W)
        showSpeed.select()
        showBoxes.select()

        # infoFrame = ttk.Labelframe(controller, text="Info")
        # infoFrame.grid(row=1, column=2, padx=padx, pady=pady)
        #
        # textWidth = 20
        #
        # info1 = ttk.Labelframe(infoFrame, text="Maksymalny nacisk")
        # info1.grid(row=1, column=1, padx=padx/2.0, pady=pady/2.0, sticky=tk.W)
        # self.infoText1 = tk.Text(info1, width=textWidth, height=info1.winfo_height())
        # self.infoText1.pack()


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
            return
        self.pathLabel.config(text=self.path)
        self.createImage()

    def createImage(self):
        if(not os.isfile(self.path)):
            return
        data = graphomotor.read(self.path)
        data = graphomotor.find_figures(data)
        data = graphomotor.create_image(data, show_speed=self.speedVar.get(), show_figure_box=self.boxesVar.get())

        self.graph.changePlot(hsv_to_rgb(data["image"]))

        print("Maksymalny nacisk: "+str(data["max_force"]))
        print("Minimalny nacisk: "+str(data['min_force']))
        print("Średni nacisk: "+str(data["avg_force"]))
        print("Maksymalna prędkość: "+str(data['max_speed']))
        print("Średnia prędkość: "+str(data['avg_speed']))
        print("Oderwania: " +str(data["line_breaks"]))
        print("Droga rysowania: "+str(data["line_len"]))
        print("Średnia szerokość kątowa: "+str(data["avg_width"]))
        print("Średnia wysokość kątowa: "+str(data["avg_height"]))


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

