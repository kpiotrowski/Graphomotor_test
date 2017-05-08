from __future__ import print_function
import graphomotor
from matplotlib import pyplot as plt
from matplotlib.colors import hsv_to_rgb



if __name__ == "__main__":
    #P1
    files = [
        "dane/33100000000 (M)/01_33100000000_10MLLP.mtb",   #0
        "dane/33100000000 (M)/02_33100000000_10MRLP.mtb",   #1
        "dane/33100000000 (M)/03_33100000000_11MRLP.mtb",   #2
        #P2
        "dane/37100000000 (M)/01_37100000000_10MLLP.mtb",   #3
        "dane/37100000000 (M)/02_37100000000_10MRLP.mtb",   #4
        "dane/37100000000 (M)/03_37100000000_11MLLP.mtb",   #5
        "dane/37100000000 (M)/04_37100000000_11MRLP.mtb",   #6
        #P3
        "dane/37120000000 (M)/01_37120000000_10MRLP.mtb",   #7
        "dane/37120000000 (M)/02_37120000000_11MRLP.mtb",   #8
        #P4
        "dane/39100000000 (M)/01_39100000000_10MLLP.mtb",   #9
        "dane/39100000000 (M)/02_39100000000_10MRLP.mtb",   #10
        "dane/39100000000 (M)/03_39100000000_11MLLP.mtb",   #11
        "dane/39100000000 (M)/04_39100000000_11MRLP.mtb",   #12
        #P5
        "dane/40080000000 (M)/01_40080000000_10MLLP.mtb",   #13
        "dane/40080000000 (M)/02_40080000000_10MRLP.mtb",   #14
        "dane/40080000000 (M)/03_40080000000_11MRLP.mtb"    #15
    ]
    data = graphomotor.read(files[15])

    data = graphomotor.find_figures(data)
    data = graphomotor.create_image(data, show_speed=True, show_figure_box=True)

    plt.imshow(hsv_to_rgb(data["image"]))

    print("Maksymalny nacisk: "+str(data["max_force"]))
    print("Minimalny nacisk: "+str(data['min_force']))
    print("Średni nacisk: "+str(data["avg_force"]))
    print("Maksymalna prędkość: "+str(data['max_speed']))
    print("Średnia prędkość: "+str(data['avg_speed']))
    print("Oderwania: " +str(data["line_breaks"]))
    print("Droga rysowania: "+str(data["line_len"]))
    print("Średnia szerokość kątowa: "+str(data["avg_width"]))
    print("Średnia wysokość kątowa: "+str(data["avg_height"]))


    plt.show()