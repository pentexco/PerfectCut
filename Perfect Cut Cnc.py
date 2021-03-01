#Orginally Written By: Jeremy Fielding and Altered by Charlie Johnson for Single Axis Stop
#Project based on Youtube Video https://youtu.be/JEImn7s7x1o

from Tkinter import * #required to build GUI Screen
from time import sleep #allows timing
import RPi.GPIO as GPIO #allows talking to gpio pins
import ConfigParser #allows reading and writing to config file

#set GPIO callout status to BCM
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Read Variables from config file
config = ConfigParser.ConfigParser()
config.read("perfect_cut_cfg.ini")

#Get Variables from myvars section of config file - setup output pins & stepper speed/resolution/stepsperinch
title_name = config.get("screen", "title_name")
panel_name = config.get("screen", "panel_name")
panel_color = config.get("screen", "panel_color")


#Get Variables from myvars section of config file - setup output pins & stepper speed/resolution/stepsperinch
dir_x = config.get("myvars", "dir_x") # Direction GPIO Pin for Fence
dir_x = int (dir_x.split('#')[0])

step_x = config.get("myvars", "step_x") # Step GPIO Pin
step_x = int(step_x.split('#')[0])

max_x = config.get("myvars", "max_x")#this is the dimension that should be displayed when the fence is on the max limit sensor
max_x = int(max_x.split('#')[0])

min_x = config.get("myvars", "min_x")#this is the dimension that should be displayed when the fence is on the min limit sensor
min_x = int(min_x.split('#')[0])

cw_x = config.get("myvars", "cw_x") # Clockwise Rotation
cw_x = int(cw_x.split('#')[0])

ccw_x = config.get("myvars", "ccw_x")# Counterclockwise Rotation
ccw_x = int(ccw_x.split('#')[0])

x_zero = config.get("myvars", "x_zero")# GPIO Pin for limit switch 
x_zero = int(x_zero.split('#')[0])

x_endpos = config.get("myvars", "x_endpos")# GPIO Pin for limit switch 
x_endpos = int(x_endpos.split('#')[0])

steps_per_revolution_x = config.get("myvars", "steps_per_revolution_x")# match switch settings on stepper controller
steps_per_revolution_x = int(steps_per_revolution_x.split('#')[0])

Desired_Rotations_Per_Second = config.get("myvars", "Desired_Rotations_Per_Second")# this is approx - higher number = faster speed - caution too high and will loose steps
Desired_Rotations_Per_Second = int(Desired_Rotations_Per_Second.split('#')[0])

stp_per_inch_x = config.get("myvars", "stp_per_inch_x")#calabration setting  
stp_per_inch_x = int(stp_per_inch_x.split('#')[0])

#Calulations for Speed
RPS=1/float(steps_per_revolution_x)/2 # = 1 Rotation per Second - there are 2 pauses - 1 for high and 1 for low
fdelay = RPS / float(Desired_Rotations_Per_Second)

#get Shortcut settings
shortcut_e1 = config.get("presets", "shortcut_e1")  
shortcut_e1 = float(shortcut_e1.split('#')[0])
e1_x = shortcut_e1

shortcut_e2 = config.get("presets", "shortcut_e2")  
shortcut_e2 = float(shortcut_e2.split('#')[0])
e2_x = shortcut_e2

shortcut_e3 = config.get("presets", "shortcut_e3")  
shortcut_e3 = float(shortcut_e3.split('#')[0])
e3_x = shortcut_e3

shortcut_e4 = config.get("presets", "shortcut_e4")  
shortcut_e4 = float(shortcut_e4.split('#')[0])
e4_x = shortcut_e4

#setup root screen 
root = Tk()
root.title(title_name)
root.geometry("620x450")

calframe= LabelFrame(root, text="Calculator", bg=panel_color, fg="white", font="bold", padx=10)
calframe.place(x=25, y=10, width=280, height=430)

x_frame=LabelFrame(root, text= panel_name, bg=panel_color, fg="white", font = "bold", padx=10)
x_frame.place(x=320, y=10, width=280, height=430)

#Entry panels, labels and locations
cal = Entry(calframe, width=22, borderwidth=3, font = ("bold", 13), justify=RIGHT)
cal.grid(row=0, column=0, columnspan=4, padx=0, pady=6)

fen = Entry(x_frame, width=22, borderwidth=3, font = ("bold", 13), justify=RIGHT)
fen.grid(row=0, column=0, columnspan=2, padx=0, pady=6)
#fen.insert(0, 0)

C_fence_position =Label (x_frame, text = "Current Position = ", font=("Arial", 13), bg=panel_color, fg= "white")
C_fence_position.grid (row=3, column=0, pady=8)

current_stop_position = Entry(x_frame, width=8, borderwidth=2, font = ("bold", 13), justify=RIGHT)
current_stop_position.grid(row=3, column=1)
current_stop_position.insert(0,0.0)

C_fence_position =Label (x_frame, text = "Presets - Set with Calculator", font=("Arial", 14), bg=panel_color, fg= "white")
C_fence_position.grid (row=5, column=0, columnspan=2, pady=6)

shortcut_e1 = Entry(x_frame, width=9, borderwidth=2, justify=RIGHT, font=("Arial", 14))
shortcut_e1.grid(row=6, column=1, pady=5)
shortcut_e1.insert(0,e1_x)

shortcut_e2 = Entry(x_frame, width=9, borderwidth=2, justify=RIGHT, font=("Arial", 14))
shortcut_e2.grid(row=7, column=1, pady=5)
shortcut_e2.insert(0,e2_x)

shortcut_e3 = Entry(x_frame, width=9, borderwidth=2, justify=RIGHT, font=("Arial", 14))
shortcut_e3.grid(row=8, column=1, pady=5)
shortcut_e3.insert(0,e3_x)

shortcut_e4 = Entry(x_frame, width=9, borderwidth=2, justify=RIGHT, font=("Arial", 14))
shortcut_e4.grid(row=9, column=1, pady=5)
shortcut_e4.insert(0,e4_x)

#Calculator functions
def button_click(number):
    current = cal.get()
    cal.delete(0, END)
    cal.insert(0, str(current) + str(number))

def button_clear():
    cal.delete(0, END)
    fen.delete(0, END)

def button_add():
    first_number = cal.get()
    global f_num
    global math
    math = "addition"
    f_num = float(first_number)
    cal.delete(0, END)

def button_equal():
    second_number = cal.get()
    cal.delete(0, END)
    
    if math == "addition":
        cal.insert(0, f_num + float(second_number))

    if math == "subtraction":
        cal.insert(0, f_num - float(second_number))

    if math == "multiplication":
        cal.insert(0, f_num * float(second_number))

    if math == "division":
        cal.insert(0, f_num / float(second_number))
  
def button_subtract():
    if len(cal.get()) > 0:
        first_number = cal.get()
        global f_num
        global math
        math = "subtraction"
        f_num = float(first_number)
        cal.delete(0, END)
    else:
        cal.insert(0, "-")

def button_multiply():
    first_number = cal.get()
    global f_num
    global math
    math = "multiplication"
    f_num = float(first_number)
    cal.delete(0, END)

def button_divide():
    first_number = cal.get()
    global f_num
    global math
    math = "division"
    f_num = float(first_number)
    cal.delete(0, END)

#Move motors
def move_fence(new_position):
    #setup variables
    global current_stop_position
    Startposition= current_stop_position.get()
    #new_position = float(fen.get())
    
    #task to complete first
    fen.delete(0, END)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(dir_x, GPIO.OUT)
    GPIO.setup(step_x, GPIO.OUT)
    GPIO.setup(x_zero, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(x_endpos, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.setup(estop, GPIO.IN)

    
    if float(Startposition) < float(new_position):
        dis_to_move =  float(new_position)- float(Startposition)
    
        move_fence_steps = int(stp_per_inch_x * float(dis_to_move))
        
        for steps in range(move_fence_steps):
            if GPIO.input(x_endpos) == 0: #check for hitting limit
                current_stop_position.delete(0,END)
                current_stop_position.insert(0, str(max_x))
                break
            GPIO.output(dir_x, cw_x)
            GPIO.output(step_x, GPIO.HIGH)
            sleep(fdelay)
            GPIO.output(step_x, GPIO.LOW)
            sleep (fdelay)
            current_stop_position.delete(0,END)
            current_stop_position.insert(0, str(new_position))
        
    elif float(Startposition) > float(new_position):
        dis_to_move =  float(Startposition)- float(new_position)
    
        move_fence_steps = int(stp_per_inch_x * float(dis_to_move))
        
        for steps in range(move_fence_steps):
            if GPIO.input(x_zero) == 0: #check for hitting limit
                current_stop_position.delete(0,END)
                current_stop_position.insert(0, str(min_x))
                break
            GPIO.output(dir_x, ccw_x)
            GPIO.output(step_x, GPIO.HIGH)
            sleep (fdelay)
            GPIO.output(step_x, GPIO.LOW)
            sleep(fdelay)
            current_stop_position.delete(0,END)
            current_stop_position.insert(0, str(new_position))
 
    elif Startposition == new_position:
        return
#reset things for next function
    GPIO.cleanup()
    
#preset shortcuts
def shortcut(shortcut_value,shortcut_name):
    if len(cal.get()) > 0:
        C_num = float(cal.get())
        cal.delete(0, END)
        shortcut_value.delete(0, END)
        shortcut_value.insert(0, C_num)
        config.set("presets", shortcut_name, C_num)
        with open("perfect_cut_cfg.ini", "w") as f:
            config.write(f)
    else: 
        C_num= float(shortcut_value.get())
        global new_position
        new_position = C_num
        move_fence(new_position)

def Inch_to_mm():
    C_num= cal.get()
    ans_in_mm = float(C_num)* 25.4
    cal.delete(0, END)
    cal.insert(0, ans_in_mm)

def mm_to_Inch():
    C_num= cal.get()
    ans_in_inch = float(C_num)/ 25.4
    cal.delete(0, END)
    cal.insert(0, ans_in_inch)

def move_cal_to_fence():
    C_num= float(cal.get())
    global new_position
    new_position = C_num
    cal.delete(0, END)
    fen.delete(0, END)
    fen.insert(0, C_num)

def move_cal_to_angle():
    C_num= float(cal.get())
    cal.delete(0, END)
    ang.delete(0, END)
    ang.insert(0, C_num)

def move_cal_to_height():
    C_num= float(cal.get())
    cal.delete(0, END)
    height.delete(0, END)
    height.insert(0, C_num)

def move_cal_to_fence_reset():
    C_num= float(cal.get())
    cal.delete(0, END)
    current_stop_position.delete(0, END)
    current_stop_position.insert(0, C_num)

def move_cal_to_angle_reset():
    C_num= float(cal.get())
    cal.delete(0, END)
    C_angle_e.delete(0, END)
    C_angle_e.insert(0, C_num)

def move_cal_to_height_reset():
    C_num= float(cal.get())
    cal.delete(0, END)
    C_height_e.delete(0, END)
    C_height_e.insert(0, C_num)
   
def go_home():
    fen.delete(0, END)

# Define Calulator Buttons
button_1 = Button(calframe, text="1", width=4, height=2, command=lambda: button_click(1))
button_2 = Button(calframe, text="2", width=4, height=2, command=lambda: button_click(2))
button_3 = Button(calframe, text="3", width=4, height=2, command=lambda: button_click(3))
button_4 = Button(calframe, text="4", width=4, height=2, command=lambda: button_click(4))
button_5 = Button(calframe, text="5", width=4, height=2, command=lambda: button_click(5))
button_6 = Button(calframe, text="6", width=4, height=2, command=lambda: button_click(6))
button_7 = Button(calframe, text="7", width=4, height=2, command=lambda: button_click(7))
button_8 = Button(calframe, text="8", width=4, height=2, command=lambda: button_click(8))
button_9 = Button(calframe, text="9", width=4, height=2, command=lambda: button_click(9))
button_0 = Button(calframe, text="0", width=4, height=2, command=lambda: button_click(0))
button_decimal = Button(calframe, text=".", width=4, height=2, command=lambda: button_click("."))
button_add = Button(calframe, text="+", width=4, height=2, command=button_add)
button_equal = Button(calframe, text="=", width=4, height=2, command=button_equal)
button_clear = Button(calframe, text="Clear", width=25, height=2, command=button_clear, bg="#AD2626")
button_subtract = Button(calframe, text="-", width=4, height=2, command=button_subtract)
button_multiply = Button(calframe, text="*", width=4, height=2, command=button_multiply)
button_divide = Button(calframe, text="/", width=4, height=2, command=button_divide)

inch_to_mm = Button(calframe, text="Inch to mm", width=25, height=2, command=Inch_to_mm)
mm_to_inch = Button(calframe, text="mm to Inch", width=25, height=2, command=mm_to_Inch)

# Put the calc buttons on the screen
button_7.grid(row=1, column=0)
button_8.grid(row=1, column=1)
button_9.grid(row=1, column=2)
button_divide.grid(row=1, column=3)

button_4.grid(row=2, column=0)
button_5.grid(row=2, column=1)
button_6.grid(row=2, column=2)
button_multiply.grid(row=2, column=3)

button_1.grid(row=3, column=0)
button_2.grid(row=3, column=1)
button_3.grid(row=3, column=2)
button_subtract.grid(row=3, column=3)

button_0.grid(row=4, column=0)
button_decimal.grid(row=4, column=1)
button_equal.grid(row=4, column=2)
button_add.grid(row=4, column=3)

button_clear.grid(row=5, column=0, columnspan=4, pady=10)
inch_to_mm.grid(row=6, column=0, columnspan=4)
mm_to_inch.grid(row=7, column=0, columnspan=4)

# Define Other Buttons
cal_to_fen_but = Button(x_frame, text="Grab", width=10, height=1, bd=1, justify= "left", command=move_cal_to_fence)
button_movefence = Button(x_frame, text="Move", width=8, height=1, bd=1, justify= "left", command=lambda: move_fence(new_position))
cal_to_fen_but_reset = Button(x_frame, text="Grab Number to Current Position", width=25, height=2, command=move_cal_to_fence_reset)
button_home = Button(x_frame, text="HOME", width=25, bg="#FFFF00", height=2, pady=4, command=go_home)
button_preset1 = Button(x_frame, text="Grab or Move:", width=13, height=1, bd=1, command=lambda: shortcut(shortcut_e1,"shortcut_e1"))
button_preset2 = Button(x_frame, text="Grab or Move:", width=13, height=1, bd=1, command=lambda: shortcut(shortcut_e2,"shortcut_e2"))
button_preset3 = Button(x_frame, text="Grab or Move:", width=13, height=1, bd=1, command=lambda: shortcut(shortcut_e3,"shortcut_e3"))
button_preset4 = Button(x_frame, text="Grab or Move:", width=13, height=1, bd=1, command=lambda: shortcut(shortcut_e4,"shortcut_e4"))

# Put the Other buttons on the screen
cal_to_fen_but.grid(row=1, column=0, ipadx=4)
button_movefence.grid(row=1, column=1, ipadx =1)
cal_to_fen_but_reset.grid(row=4, column=0, columnspan=2)
button_preset1.grid(row=6, column=0)
button_preset2.grid(row=7, column=0)
button_preset3.grid(row=8, column=0)
button_preset4.grid(row=9, column=0)
button_home.grid(row=10, column=0, columnspan=2)
root.mainloop()
