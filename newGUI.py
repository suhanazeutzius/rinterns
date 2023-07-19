from tkinter import *
from tkinter import filedialog as fd
from PIL import ImageTk, Image
from monopulse_data_prep import *
import os
from skyfield.api import load, wgs84, EarthSatellite
import numpy as np
import matplotlib.pyplot as plt
import re
from flatirons.orbits_error import getOverheadSatellites
import time


# create the window
root = Tk()
root.title("Satellite Tracker")
#root.configure(bg='#E4D4AD')
screen_width = root.winfo_screenwidth() - int(0.6 * root.winfo_screenwidth())
#print(screen_width)
screen_height = root.winfo_screenheight() - int(0.2 * root.winfo_screenheight())
#print(screen_height)
str_window = str(screen_width) + 'x' + str(screen_height)
root.geometry(str_window)

# place a frame and canvas into the gui on startup
#starting_frame = Frame(root, width=400, height=300, bg='#0F0F0F')
#starting_frame.place(x=400, y=130)
#starting_canvas = Canvas(root, width=388, height=288, bg="#FFFFFF")
#starting_canvas.place(x=405, y=135)
#

# get current time
ts = load.timescale()
#t = ts.utc(2023, 7, 18, 11, 40, 0)
t = ts.now()
gps_file = 'tle-gps.txt'
debug = False
show_plot = False
_ = getOverheadSatellites(t, gps_file, 26.2, [+39.58709, -104.82873], debug, show_plot)
# making the frame for the canvas to sit in
fig2 = ImageTk.PhotoImage(Image.open('overhead_satellites.png'))
fig2.img = fig2
frame2 = Frame(root, width=fig2.width() + 12, height=fig2.height() + 12, bg="#3C3B36")
frame2.place(x=400, y=130)

# placing a canvas that the image will sit in 
canvas2 = Canvas(root, width=fig2.width(), height=fig2.height())
canvas2.place(x=405, y=135)
my_img2 = canvas2.create_image(fig2.width()/2, fig2.height()/2, image=fig2)


# this will open up the files and browse for the specified data set
def browseFiles():
    global selected_file_name
    selected_file_name = fd.askopenfilename(title = "Select a File", filetypes = [("all files", "*.csv")])
    #print("selected_file_name: ")
    #print(type(selected_file_name))
    
    # prints a tuple formatted like: ('directory', 'file')
    if len(selected_file_name) == 0:
        print("No file selected. Please select a file.")
        error = "No file selected. Please select a file."
        disp_error = Message(root, text=error).place(x=230, y=80)
    else:
        path_list = selected_file_name.split('/')
        #print("path_list: ")
        #print(path_list)
    
        # displays on the GUI the working directory and file
        var = str(selected_file_name)
        disp_name = Message(root, text=var).place(x=230, y=80)
        
        # stores "data" "<folder>" and "<file.csv>" in a list in working_file
        global working_file
        working_file = path_list[-3:]
        #print("working_file: ")
        #print(working_file)    
        
        # joins elements in working_file with '/' character
        global working_path
        working_path = '/'.join(working_file) 
        #print(working_path)
        
        return working_path, selected_file_name


# this changes the prn based on user input from dropdown and plots it
def whichPRN():    
    # get rid of other canvases
    canvas2.delete('all')

    # low is for correlating
    if len(selected_file_name) == 0:
        print("No file selected. Please select a file.")
        error1 = "No file selected. Please select a file."
        disp_error1 = Message(root, text=error1).place(x=230, y=80)

    else:
        file_name = working_path
        #print(file_name + " should  the file name passed to the prepdata file")
        #print("Current working directory: " + os.getcwd())

        # sets the PRN numr as dropdown selection, sets parameters for prepareDataMonopulse 
        prn = int(clicked.get())
        plot_correlation = True
        wire_delay = 7.13e-9

        # calls prepareDataForMonopulse from tycho's code and plots the correlation
        _, corr = prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation)

        # puts an image in the GUI showing whatever is saved as fig1
        img = ImageTk.PhotoImage(Image.open('fig1.png'))
        
        # making the frame for the canvas to sit in
        frame = Frame(root, width=img.width() + 12, height=img.height() + 12, bg="#3C3B36")
        frame.place(x=400, y=130)        
    
        # placing a canvas that the image will sit in 
        canvas = Canvas(root, width=img.width(), height=img.height())
        canvas.place(x=405, y=135)
        my_img = canvas.create_image(img.width()/2, img.height()/2, image=img)     


# this takes the user input and does things with it
def seekSatellites():
    # get rid of other canvases
    #canvas.delete('all')

    # get current time
    ts = load.timescale()
    #t = ts.utc(2023, 7, 18, 11, 40, 0)
    t = ts.now()
    gps_file = 'tle-gps.txt'
    debug = False
    show_plot = False
    _ = getOverheadSatellites(t, gps_file, 26.2, [+39.58709, -104.82873], debug, show_plot)
    #plt.show()
    
    #time.sleep(1)

    # making the frame for the canvas to sit in
    fig2 = ImageTk.PhotoImage(Image.open('overhead_satellites.png'))
    fig2.img = fig2
    frame2 = Frame(root, width=fig2.width() + 12, height=fig2.height() + 12, bg="#3C3B36")
    frame2.place(x=400, y=130)
 
    # placing a canvas that the image will sit in 
    canvas2 = Canvas(root, width=fig2.width(), height=fig2.height())
    canvas2.place(x=405, y=135)
    my_img2 = canvas2.create_image(fig2.width()/2, fig2.height()/2, image=fig2) 


prns = list(range(1,33))

# converting the data from the dropdown menu
clicked = StringVar()

# initialize prn
clicked.set(prns[0])

# creating menu
drop = OptionMenu(root, clicked, *prns)
drop.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
drop["menu"].config(fg='#EAE0D5', bg='#4D4D77')
drop.place(x=150, y=109)

# get current satellite sky plot
time_butt = Button(root, text="Show Current Sky Map:", command=seekSatellites)
time_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
time_butt.place(x=50, y=155)

# correlate button
corr_butt = Button(root, text="Select PRN:", command=whichPRN)
corr_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
corr_butt.place(x=50, y=110)

# browse for data file 
data_butt = Button(root, text="Choose File", command=browseFiles)
data_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
data_butt.place(x=50, y=80)

# this button exits the GUI
exit_butt = Button(root, text="Exit", command=root.quit)
exit_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
exit_butt.place(x=230, y=450)


# run the window
root.mainloop()
