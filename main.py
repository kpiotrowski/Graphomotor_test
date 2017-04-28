from __future__ import print_function
import graphomotor
from matplotlib import pyplot as plt
from matplotlib.colors import hsv_to_rgb



if __name__ == "__main__":
    data = graphomotor.read("dane/33100000000 (M)/01_33100000000_10MLLP.mtb")
    data = graphomotor.create_image(data)

    plt.imshow(hsv_to_rgb(data["image"]), interpolation='none')
    plt.show()

    print(len(data['data']))
