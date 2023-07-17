# import important python things
from tkinter import *
from tkinter import filedialog as fd
from PIL import ImageTk, Image
from monopulse_data_prep import *
import os

# create the window
root = Tk()
root.title("Satellite Tracker")
#root.configure(bg='#E4D4AD')
screen_width = root.winfo_screenwidth() - int(0.6 * root.winfo_screenwidth())
print(screen_width)
screen_height = root.winfo_screenheight() - int(0.2 * root.winfo_screenheight())
print(screen_height)
str_window = str(screen_width) + 'x' + str(screen_height)
root.geometry(str_window)


starting_frame = Frame(root, width=400, height=300, bg='#0F0F0F')
starting_frame.place(x=400, y=130)
starting_canvas = Canvas(root, width=388, height=288, bg="#FFFFFF")
starting_canvas.place(x=405, y=135)


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

prns = [
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    '10',
    '11',
    '12',
    '13',
    '14',
    '15',
    '16',
    '17',
    '18',
    '19',
    '20',
    '21',
    '22',
    '23',
    '24',
    '25',
    '26',
    '27',
    '28',
    '29',
    '30',
    '31',
    '32'
]

# converting the data from the dropdown menu
clicked = StringVar()

# initialize prn
clicked.set(prns[0])

# creating menu
drop = OptionMenu(root, clicked, *prns)
drop.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
drop["menu"].config(fg='#EAE0D5', bg='#4D4D77')
drop.place(x=150, y=109)

# correlate button
corr_butt = Button(root, text="Select PRN:", command=whichPRN)
corr_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
corr_butt.place(x=50, y=110)

# browse for data file 
data_butt = Button(root, text="Choose File", command=browseFiles)
data_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
data_butt.place(x=50, y=80)

# this will  to display the plot that Tycho made
#compass_butt = Button(root, text="Compass")
#compass_butt.place(x=25, y=100)

# this button exits the GUI
exit_butt = Button(root, text="Exit", command=root.quit)
exit_butt.config(fg='#EAE0D5', activeforeground='#EAE0D5', bg='#4D4D77', activebackground='#81829C')
exit_butt.place(x=130, y=250)

# define the image that will go in the GUI
#img = ImageTk.PhotoImage(Image.open('bee.png'))
#rz_img = img.resize((100, 100))


# run the window
root.mainloop()
