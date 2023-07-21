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
from datacollect import *

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

check = IntVar()


# this will open up the files and browse for the specified data set
def browseFiles():
    global selected_file_name
    selected_file_name = fd.askopenfilename(title = "Select a File", filetypes = [("all files", "*.csv")])
    #print("selected_file_name: ")
    #print(type(selected_file_name))
    
    
    # prints a tuple formatted like: ('directory', 'file')
    if len(selected_file_name) == 0:
        # open a new window with the error there isn't a file selected
        error = "No file selected. Please select a file."
        disp_error = Toplevel()
        disp_error.geometry('245x25')
        disp_error.title("Error")
        Label(disp_error, text=error).pack()
        
                
    else:
        path_list = selected_file_name.split('/')
        #print("path_list: ")
        #print(path_list)
    
        # displays on the GUI the working directory and file
        file_path_name = "File Seleted: " + str(selected_file_name)
        disp_name = Label(root, text=file_path_name, font=('Arial', 12), padx=10, pady=5).place(x=400, y=70)
        
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
    #canvas2.delete('all')
    
    print("got here 1")
    print("Check value: " + str(check))
    print("file: " + selected_file_name) 
    
    # low is for correlating
    if len(selected_file_name) == 0:
        print("got here 2")

        # open a new window with the error there isn't a file selected
        error = "No file selected. Please select a file."
        disp_error = Toplevel()
        disp_error.geometry('245x25')
        disp_error.title("Error")
        Label(disp_error, text=error).pack()
        # making the frame for the canvas to sit in
        fig2 = ImageTk.PhotoImage(Image.open('overhead_satellites.png'))
        fig2.img = fig2
        frame2 = Frame(root, width=fig2.width() + 12, height=fig2.height() + 12, bg="#3C3B36")
        frame2.place(x=400, y=130)
   
        # placing a canvas that the image will sit in 
        canvas2 = Canvas(root, width=fig2.width(), height=fig2.height())
        canvas2.place(x=405, y=135)
        my_img2 = canvas2.create_image(fig2.width()/2, fig2.height()/2, image=fig2)
    else:
        # path and filename    
        file_name = working_path
    
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


#    elif check == 0 and len(selected_file_name) != 0: 
#        print("got here 3")
#
#        # test to see if this worked
#        print("not checked, file selected and plotted")
#
#        # path and filename    
#        file_name = working_path
#        
#        # sets the PRN numr as dropdown selection, sets parameters for prepareDataMonopulse 
#        prn = int(clicked.get())
#        plot_correlation = True
#        wire_delay = 7.13e-9 
#   
#        # calls prepareDataForMonopulse from tycho's code and plots the correlation
#        _, corr = prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation)
#
#        # puts an image in the GUI showing whatever is saved as fig1
#        img = ImageTk.PhotoImage(Image.open('fig1.png'))
#        
#        # making the frame for the canvas to sit in
#        frame = Frame(root, width=img.width() + 12, height=img.height() + 12, bg="#3C3B36")
#        frame.place(x=400, y=130)        
#    
#        # placing a canvas that the image will sit in 
#        canvas = Canvas(root, width=img.width(), height=img.height())
#        canvas.place(x=405, y=135)
#        my_img = canvas.create_image(img.width()/2, img.height()/2, image=img)     
#    
#    elif check == 1 and len(selected_file_name) != 0:
#        print("got here 4")
#
#        # test to see if this worked
#        print("checked, file selected and plotted")     
#
#        # path and filename    
#        file_name = working_path
#            
#        # sets the PRN numr as dropdown selection, sets parameters for prepareDataMonopulse 
#        prn = int(clicked.get())
#        plot_correlation = True
#        wire_delay = 7.13e-9 
#   
#        # calls prepareDataForMonopulse from tycho's code and plots the correlation
#        _, corr = prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation)
#
#        # puts an image in the GUI showing whatever is saved as fig1
#        img = ImageTk.PhotoImage(Image.open('fig1.png'))
#            
#        # making the frame for the canvas to sit in
#        frame = Frame(root, width=img.width() + 12, height=img.height() + 12, bg="#3C3B36")
#        frame.place(x=400, y=130)    
#    
#        # placing a canvas that the image will sit in 
#        canvas = Canvas(root, width=img.width(), height=img.height())
#        canvas.place(x=405, y=135)
#        my_img = canvas.create_image(img.width()/2, img.height()/2, image=img)

# this takes the user input and does things with it
def seekSatellites():
    # get current time
    ts = load.timescale()
    #t = ts.utc(2023, 7, 18, 11, 40, 0)
    t = ts.now()
    gps_file = 'tle-gps.txt'
    debug = False
    show_plot = False
    _ = getOverheadSatellites(t, gps_file, 26.2, [+39.58709, -104.82873], debug, show_plot)
    #plt.show()
    
    # making the frame for the canvas to sit in
    fig2 = ImageTk.PhotoImage(Image.open('overhead_satellites.png'))
    fig2.img = fig2
    frame2 = Frame(root, width=fig2.width() + 12, height=fig2.height() + 12, bg="#3C3B36")
    frame2.place(x=400, y=130)

    # placing a canvas that the image will sit in 
    canvas2 = Canvas(root, width=fig2.width(), height=fig2.height())
    canvas2.place(x=405, y=135)
    my_img2 = canvas2.create_image(fig2.width()/2, fig2.height()/2, image=fig2) 

def collectData():
    # if data button is clicked then take data and store as a file
    code = datacollect()
    print(code)


prns = list(range(1,33))

# converting the data from the dropdown menu
clicked = StringVar()

# initialize prn
clicked.set(prns[0])

# integer returned from checkmark
#check = IntVar()

# check mark for all PRNs
check_mark = Checkbutton(root, text='Select All', variable=check, onvalue=1, offvalue=0)
check_mark.place(x=50, y=210)


# creating menu
drop = OptionMenu(root, clicked, *prns)
drop.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
drop["menu"].config(fg='#EAE0D5', bg='#4D4D77')
drop.place(x=150, y=139)

# get current satellite sky plot
time_butt = Button(root, text="Show Current Sky Map:", command=seekSatellites)
time_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
time_butt.place(x=50, y=175)

# correlate button
corr_butt = Button(root, text="Select PRN:", command=whichPRN)
corr_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
corr_butt.place(x=50, y=140)

# browse for data file 
browse_butt = Button(root, text="Choose File", command=browseFiles)
browse_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
browse_butt.place(x=50, y=110)

# this button exits the GUI
exit_butt = Button(root, text="Exit", command=root.quit)
exit_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
exit_butt.place(x=230, y=450)

# this button collects data!
cdata_butt = Button(root, text="Collect GPS Samples", command=collectData)
cdata_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
cdata_butt.place(x=50, y=80)


# run the window
root.mainloop()
