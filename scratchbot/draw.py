





'''
import dearpygui.dearpygui as dpg
import threading

# Create a function to draw a line on a canvas in Dear PyGui
def line(fx, fy, tx, ty):
    with dpg.drawlist(width=315, height=814, parent="main_window"):
        dpg.draw_line((fx, fy), (tx, ty), color=(200, 200, 200), thickness=1)

# Create a function to run the Dear PyGui application
def run_dpg():
    # Create the main window context
    dpg.create_context()

    # Run the Dear PyGui event loop
    dpg.create_viewport(title='Dear PyGui Box Drawing', width=315, height=840)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

# Start the Dear PyGui application in a separate thread
dpg_thread = threading.Thread(target=run_dpg)
dpg_thread.start()


# EITHER NEED TO RUN IN IT"S OWN THREAD OR maybe let's just draw on a canvas in the browser



import tkinter as tk



def line(fx, fy, tx, ty):
	global canvas
	canvas.create_line(fx, fy, tx, ty, fill="black")


# Create the main window
window = tk.Tk()
window.title("Box Drawing")
window.geometry("315x840")

# Create a canvas widget
canvas = tk.Canvas(window, width=315, height=814)
canvas.pack()


# Run the window's main event loop
window.mainloop()
'''