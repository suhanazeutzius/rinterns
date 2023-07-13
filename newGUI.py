# import important python things
from tkinter import *
from tkinter import filedialog as fd
from PIL import ImageTk, Image
from monopulse_data_prep import *
import os

# create the window
root = Tk()
root.title("Satellite Tracker")
#root.configure(bg='#9494ba')
root.geometry('500x300')

# this will open up the files and browse for the specified data set
def browseFiles():
    global selected_file_name
    selected_file_name = fd.askopenfilename(title = "Select a File", filetypes = [("all files", "*.csv")])
    print(selected_file_name)
    
    # prints a tuple formatted like: ('directory', 'file')
    #path_list = selected_file_name.split('/')
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
    # below is for correlating
    file_name = working_path
    print(file_name + " should be the file name passed to the prepdata file")
    print("Current working directory: " + os.getcwd())

    # sets the PRN number as dropdown selection, sets parameters for prepareDataMonopulse 
    prn = int(clicked.get())
    plot_correlation = True
    wire_delay = 7.13e-9

    # calls prepareDataForMonopulse from tycho's code and plots the correlation
    _, corr = prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation)

    # brings up a new window showing whatever is saved as fig1
    global img
    new_window = Toplevel()
    img = ImageTk.PhotoImage(Image.open('fig1.png'))
    img_label = Label(new_window, image=img).pack()

    

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
drop.config(fg='#ffffff', activeforeground='#bfbfbf', bg='#636b8a', activebackground='#464d77')
drop["menu"].config(fg='#ffffff', bg='#1f295c')
drop.place(x=150, y=109)

# correlate button
corr_butt = Button(root, text="Select PRN:", command=whichPRN)
corr_butt.config(fg='#ffffff', activeforeground='#bfbfbf', bg='#636b8a', activebackground='#464d77')
corr_butt.place(x=50, y=110)

# browse for data file 
data_butt = Button(root, text="Choose File", command=browseFiles)
data_butt.config(fg='#ffffff', activeforeground='#bfbfbf', bg='#636b8a', activebackground='#464d77')
data_butt.place(x=50, y=80)

# this will be to display the plot that Tycho made
#compass_butt = Button(root, text="Compass")
#compass_butt.place(x=25, y=100)

exit_butt = Button(root, text="Exit", command=root.quit)
exit_butt.config(fg='#ffffff', activeforeground='#bfbfbf', bg='#636b8a', activebackground='#464d77')
exit_butt.place(x=130, y=250)


# run the window
root.mainloop()
