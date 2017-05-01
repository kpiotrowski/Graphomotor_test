from __future__ import print_function
import graphomotor
from matplotlib import pyplot as plt
from matplotlib.colors import hsv_to_rgb



if __name__ == "__main__":
    data = graphomotor.read("dane/33100000000 (M)/02_33100000000_10MRLP.mtb")
    data = graphomotor.find_figures(data)
    data = graphomotor.create_image(data, show_speed=True, show_figure_box=True)

    plt.imshow(hsv_to_rgb(data["image"]))

    print("Maksymalny nacisk: "+str(data["max_force"]))
    print("Minimalny nacisk: "+str(data['min_force']))
    print("Średni nacisk: "+str(data["avg_force"]))
    print("Maksymalna prędkość: "+str(data['max_speed']))
    print("Średnia prędkość: "+str(data['avg_speed']))
    print("Oderwania: " +str(data["line_brakes"]))
    print("Droga rysowania: "+str(data["line_len"]))
    print("Średnia szerokość kątowa: "+str(data["avg_width"]))
    print("Średnia wysokość kątowa: "+str(data["avg_height"]))


    plt.show()