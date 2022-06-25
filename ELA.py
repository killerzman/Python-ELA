#importing libraries
import tkinter as tk
from tkinter import filedialog as fd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

import skimage
from skimage.util import compare_images
from skimage import img_as_ubyte

import numpy as np

import io
import imageio
import os.path
import copy

#creating main program window
root_window = tk.Tk()
root_window.title("ELA")

#variables for the image handles
original_image = None
original_file_name = None
original_image_blurred = None

#variables for altering the image
to_blur_var = tk.IntVar()
compress_quality_var = tk.IntVar()

#main work function
def processImages():
    #check if the image is loaded
    if original_image is not None:
        #creating memory stream for the compressed image
        buffer = io.BytesIO()

        #compress the image using JPEG in-memory
        #use the normal image or the blurred image depending on the checkbox
        imageio.imwrite(buffer,
                        original_image if to_blur_var.get() == 0
                        else original_image_blurred, format = 'jpg',
                        quality = compress_quality_var.get())
        image_compressed = imageio.imread(buffer.getbuffer(), format='jpg')

        #subtrack the original image from the compressed image
        image_difference = compare_images(original_image, image_compressed, 'diff')
        image_difference = img_as_ubyte(image_difference)

        #get the maximum difference value
        max_diff = np.amax(image_difference)

        #enhance the brightness of the difference image
        image_ELA = skimage.exposure.adjust_gamma(image_difference, max_diff / 255.0)

        #calculate the inverse of the ELA image
        inverted_image_ELA = skimage.util.invert(image_ELA)

        #setting the figures
        sp1.title.set_text(f'Original image: \n{original_file_name}')
        sp1.imshow(original_image)

        sp2.title.set_text(f'Blurred image: \n{original_file_name}')
        sp2.imshow(original_image_blurred)

        sp3.title.set_text(f'ELA on ' +
                           f'{"original" if to_blur_var.get() == 0 else "blurred"} ' +
                           f'image: \n{original_file_name}')
        sp3.imshow(image_ELA)

        sp4.title.set_text(f'ELA on ' +
                           f'{"original" if to_blur_var.get() == 0 else "blurred"} ' +
                           f'inverted image: \n{original_file_name}')
        sp4.imshow(inverted_image_ELA)

        figure.suptitle(f'Compression level used: {str(compress_quality_var.get())} %')

        #update the canvas
        figure_canvas.draw()

#function for loading the image
def openImage():
    file_types = [
        ('JPG', '*.jpg')
        ]

    file_path = fd.askopenfilename(
        title = 'Open Image',
        filetypes = file_types
        )

    if file_path:
        #load the image and its' info in global variables
        global original_image
        global original_file_name
        global original_image_blurred

        image = skimage.io.imread(file_path)
        original_image = copy.deepcopy(image)

        _, file_name = os.path.split(file_path)
        original_file_name = file_name

        #process the image with gaussian blur
        image_blurred = skimage.filters.gaussian(image,
                                                 sigma=2,
                                                 multichannel = True)
        original_image_blurred = copy.deepcopy(image_blurred)

        #once the images are loaded, process them
        processImages()

#setting up the interface
open_image_button = tk.Button(
    root_window,
    text = "Open Image",
    command = openImage
)

use_blurred_image_checkbox = tk.Checkbutton(
    root_window,
    text = "Use blurred image",
    command = lambda : processImages(),
    var = to_blur_var
)

compression_label = tk.Label(
    root_window,
    text = "Compression level: "
)

compression_slider = tk.Scale(
    root_window,
    from_ = 0,
    to = 100,
    length = 300,
    tickinterval = 10,
    orient = tk.HORIZONTAL,
    var = compress_quality_var
)

#default compression level
compression_slider.set(90)

compression_slider.bind("<ButtonRelease-1>", lambda event: processImages())

#binding matplotlib figure to the canvas
figure = plt.figure()
figure_canvas = FigureCanvasTkAgg(figure, master = root_window)
NavigationToolbar2Tk(figure_canvas, root_window)
sp1 = figure.add_subplot(221)
sp2 = figure.add_subplot(222)
sp3 = figure.add_subplot(223)
sp4 = figure.add_subplot(224)

#pack the interface
open_image_button.pack()
use_blurred_image_checkbox.pack()
compression_label.pack()
compression_slider.pack()
figure_canvas.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = 1)

#start the main loop
root_window.mainloop()