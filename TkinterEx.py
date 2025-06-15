import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
#from PIL import Image, ImageTk
import time
import threading

def textBox():
    
    # Create the main window
    root = tk.Tk()
    root.title("Long Text Display Example")
    
    # Create a ScrolledText widget (Text widget with a scrollbar)
    text_box = scrolledtext.ScrolledText(root, wrap='word', width=30, height=15)
    text_box.pack(expand=True, fill='both')
    
    # Sample long text string
    long_text = """
    Tkinter is a versatile and powerful tool for building desktop applications 
    in Python. Its simplicity and accessibility make it a popular choice for 
    beginners and for creating quick prototypes. Tkinter handles events 
    using an event-driven programming model. Events are bound to widgets 
    using the bind method or the command option for simple button clicks. 
    When an event occurs, a callback function is executed, allowing you to 
    respond to user interactions. Event objects provide additional information 
    about the event, enabling more detailed event handling.
    """
    
    # Insert the long text string into the Text widget
    text_box.insert(tk.END, long_text)
    
    # Run the application
    root.mainloop()

def showImage():

    def resize_image(event):
        # Resize the image to fit the window's dimensions
        new_width = event.width
        new_height = event.height
        resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)

        # Update the label with the resized image
        label.config(image=photo)
        label.image = photo

    # Create the main window
    root = tk.Tk()
    root.title("Scaled Image Example")
    root.geometry("400x400")  # Set initial window size

    # Load the original image
    original_image = Image.open("Dog.jpg")

    # Convert the image for Tkinter display
    photo = ImageTk.PhotoImage(original_image)

    # Create a label to display the image
    label = tk.Label(root, image=photo)
    label.image = photo  # Keep a reference to prevent garbage collection
    label.pack(fill=tk.BOTH, expand=True)

    # Bind the resize event to adjust the image size dynamically
    root.bind("<Configure>", resize_image)

    # Run the application
    root.mainloop()

def radioButton():

    def on_radio_button_select():
        selected_option = radio_var.get()
        # Update the label text and color based on the selected option
        if selected_option == 1:
            result_label.config(text="Selected option: Option 1", fg="red")
        elif selected_option == 2:
            result_label.config(text="Selected option: Option 2", fg="blue")
        elif selected_option == 3:
            result_label.config(text="Selected option: Option 3", fg="green")

    # Create the main window
    root = tk.Tk()
    root.geometry("400x300+100+100")  # Example: 400x300 size, positioned at (100, 100)
    root.title("Radio Button Example")

    # Create an IntVar to store the value of the selected radio button
    radio_var = tk.IntVar()

    # Create radio buttons
    radio1 = tk.Radiobutton(root, text="Option 1", variable=radio_var, value=1, command=on_radio_button_select)
    radio1.pack(anchor=tk.W)

    radio2 = tk.Radiobutton(root, text="Option 2", variable=radio_var, value=2, command=on_radio_button_select)
    radio2.pack(anchor=tk.W)

    radio3 = tk.Radiobutton(root, text="Option 3", variable=radio_var, value=3, command=on_radio_button_select)
    radio3.pack(anchor=tk.W)

    # Create a label to display the selected option
    result_label = tk.Label(root, text="Selected option: None", font=("Arial", 12))
    result_label.pack(pady=10)

    # Run the application
    root.mainloop()


def progressBar():

    def start_progress():
        # Simulate a task in a separate thread to avoid freezing the GUI
        def task():
            progress_bar["value"] = 0  # Reset progress bar
            for i in range(1, 101):  # Simulating 100 steps
                time.sleep(0.05)  # Simulate work with a delay
                progress_bar["value"] = i  # Update progress bar value
                progress_label.config(text=f"Progress: {i}%")  # Update progress label
            progress_label.config(text="Task Complete!")

        threading.Thread(target=task).start()

    # Set up the main window
    root = tk.Tk()
    root.title("Progress Bar Example")
    root.geometry("400x200")

    # Create and place the progress bar
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=20)

    # Create and place the label for progress
    progress_label = tk.Label(root, text="Click 'Start' to begin")
    progress_label.pack(pady=10)

    # Create and place the Start button
    start_button = tk.Button(root, text="Start", command=start_progress)
    start_button.pack(pady=10)

    # Start the GUI main loop
    root.mainloop()

def noteBook():
    # Create the main window
    root = tk.Tk()
    root.geometry("400x300+100+100")  # Example: 400x300 size, positioned at (100, 100)
    root.title("Notebook Widget Example")

    # Create a notebook widget
    notebook = ttk.Notebook(root)

    # Create frames for each tab and set their background colors
    tab1 = tk.Frame(notebook, bg="lightblue")  # Light blue for Tab 1
    tab2 = tk.Frame(notebook, bg="lightgreen")  # Light green for Tab 2
    tab3 = tk.Frame(notebook, bg="lightpink")  # Light pink for Tab 3

    # Add the frames to the notebook
    notebook.add(tab1, text="Tab 1")
    notebook.add(tab2, text="Tab 2")
    notebook.add(tab3, text="Tab 3")

    # Pack the notebook
    notebook.pack(expand=True, fill="both")

    # Add some content to each tab
    label1 = ttk.Label(tab1, text="This is Tab 1", background="lightblue")
    label1.pack(pady=10, padx=10)

    label2 = ttk.Label(tab2, text="This is Tab 2", background="lightgreen")
    label2.pack(pady=10, padx=10)

    label3 = ttk.Label(tab3, text="This is Tab 3", background="lightpink")
    label3.pack(pady=10, padx=10)

    # Start the Tkinter event loop
    root.mainloop()

def menu():

    def show_selected_option(selected_option):
        option_var.set(selected_option)
        label.config(text=f"Selected Option: {selected_option}", fg=color_dict[selected_option])

    # Create the main window
    root = tk.Tk()
    root.geometry("400x300+100+100")  # Example: 400x300 size, positioned at (100, 100)
    root.title("Colorful Option Menu Example")

    # Define options and their colors
    choices = ["Option 1", "Option 2", "Option 3", "Option 4"]
    color_dict = {
        "Option 1": "red",
        "Option 2": "blue",
        "Option 3": "green",
        "Option 4": "purple"
    }

    # Create a StringVar to hold the currently selected option
    option_var = tk.StringVar(root)
    option_var.set("Select an Option")  # Default display text

    # Create the dropdown menu
    menu_button = tk.Menubutton(root, textvariable=option_var, relief="raised", font=("Arial", 12))
    menu_button.menu = tk.Menu(menu_button, tearoff=0)
    menu_button["menu"] = menu_button.menu

    # Add options to the menu
    for choice in choices:
        menu_button.menu.add_command(
            label=choice,
            command=lambda value=choice: show_selected_option(value),
            foreground=color_dict[choice]
        )

    menu_button.pack(pady=10)

    # Create a label to display the selected option
    label = tk.Label(root, text="", font=("Arial", 12))
    label.pack(pady=5)

    # Run the application
    root.mainloop()

def multiButton():

    def on_left_click(event):
        label.config(text=f"Left mouse button clicked at ({event.x}, {event.y})", fg="red")
        draw_circle(event.x, event.y, "red")

    def on_middle_click(event):
        label.config(text=f"Middle mouse button clicked at ({event.x}, {event.y})", fg="blue")
        draw_circle(event.x, event.y, "blue")

    def on_right_click(event):
        label.config(text=f"Right mouse button clicked at ({event.x}, {event.y})", fg="green")
        draw_circle(event.x, event.y, "green")

    def draw_circle(x, y, color):
        # Draw a circle at the given coordinates
        canvas.create_oval(x-10, y-10, x+10, y+10, fill=color, outline=color)

    # Set up the main window
    root = tk.Tk()
    root.title("Mouse Events Example")
    root.geometry("400x300+100+100")  # Example: 400x300 size, positioned at (100, 100)

    # Create a label to display the event text
    label = tk.Label(root, text="Click a mouse button", font=("Arial", 12))
    label.pack(pady=20)

    # Create a canvas for drawing circles
    canvas = tk.Canvas(root, width=400, height=200, bg="white")
    canvas.pack()

    # Bind mouse events
    root.bind("<Button-1>", on_left_click)  # Left mouse button
    root.bind("<Button-2>", on_middle_click)  # Middle mouse button
    root.bind("<Button-3>", on_right_click)  # Right mouse button

    # Start the main loop
    root.mainloop()

def listBox():
    
    def on_listbox_select(event):
        # Get the index of the selected item
        selected_index = listbox.curselection()
        if selected_index:
            # Get the text of the selected item
            selected_text = listbox.get(selected_index)
            # Show a message box with the selected item
            messagebox.showinfo("Item Selected", f"You selected: {selected_text}")
    
    # Create the main window
    root = tk.Tk()
    root.geometry("400x300+100+100")  # Example: 400x300 size, positioned at (100, 100)
    root.title("Simple Listbox Example")
    
    # Create a Listbox widget
    listbox = tk.Listbox(root, height=10)
    listbox.pack(pady=10)
    
    # Insert items into the Listbox
    items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
    for item in items:
        listbox.insert(tk.END, item)
    
    # Bind the Listbox selection event to the on_listbox_select function
    listbox.bind("<<ListboxSelect>>", on_listbox_select)
    
    # Run the application
    root.mainloop()

def focus():

    def on_click(event):
        # Display the coordinates of the mouse click
        label.config(text=f"Mouse clicked at: ({event.x}, {event.y})")
        # Draw a small dot at the click location
        canvas.create_oval(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="black")

    # Create the main window
    root = tk.Tk()
    root.geometry("400x300+100+100")  # Example: 400x300 size, positioned at (100, 100)
    root.title("Mouse Event Example")

    # Create a label to display the coordinates
    label = tk.Label(root, text="Click anywhere inside the window")
    label.pack(pady=20)

    # Create a canvas for drawing dots
    canvas = tk.Canvas(root, width=400, height=300, bg="white")
    canvas.pack()

    # Bind the mouse click event to the function
    canvas.bind("<Button-1>", on_click)

    # Start the Tkinter event loop
    root.mainloop()

def checkBox():

    def update_label():
        # Clear previous colored labels
        for label in colored_labels:
            label.destroy()
        colored_labels.clear()

        # Dynamically create labels for selected items with different colors
        for item, var in checkbox_vars.items():
            if var.get():  # If the checkbox is selected
                label = tk.Label(root, text=item, fg=color_mapping[item])
                label.pack()  # Add the label with the item's color
                colored_labels.append(label)  # Keep track of labels to clear later

    # Create the main window
    root = tk.Tk()
    root.title("Colorful Checkbox Example")
    root.geometry("300x200")

    # List of items and their associated colors
    items = ["Red", "Green", "Blue", "Yellow"]
    color_mapping = {
        "Red": "red",
        "Green": "green",
        "Blue": "blue",
        "Yellow": "gold"
    }
    checkbox_vars = {}  # Dictionary to hold checkbox variables
    colored_labels = []  # Track dynamic labels for clearing old selections

    # Create checkboxes dynamically
    for item in items:
        var = tk.BooleanVar()  # Variable to track checkbox state
        checkbox_vars[item] = var
        chk = tk.Checkbutton(root, text=item, variable=var, command=update_label)
        chk.pack(anchor="w")  # Align checkboxes to the left

    # Start the GUI main loop
    root.mainloop()

def calculator():

    def button_click(event):
        # Get the text from the clicked button
        text = event.widget.cget("text")
        
        # Handle special buttons like "=" and "C"
        if text == "=":
            try:
                # Evaluate the expression and update the display
                result = str(eval(display_var.get()))
                display_var.set(result)
            except Exception as e:
                display_var.set("Error")
        elif text == "C":
            # Clear the display
            display_var.set("")
        else:
            # Append the clicked button text to the display
            display_var.set(display_var.get() + text)
    
    # Create the main window
    root = tk.Tk()
    root.title("Simple Calculator")
    
    # Create a StringVar to store the display text
    display_var = tk.StringVar()
    
    # Create an entry widget for the display
    display = tk.Entry(root, textvar=display_var, font="Arial 20", bd=10, insertwidth=4, width=14, borderwidth=4)
    display.grid(row=0, column=0, columnspan=4)
    
    # List of button texts
    buttons = [
        '7', '8', '9', '/',
        '4', '5', '6', '*',
        '1', '2', '3', '-',
        'C', '0', '=', '+'
    ]
    
    # Create buttons and place them in the grid
    row_val = 1
    col_val = 0
    for button_text in buttons:
        button = tk.Button(root, text=button_text, padx=20, pady=20, font="Arial 14")
        button.grid(row=row_val, column=col_val)
        button.bind("<Button-1>", button_click)
        col_val += 1
        if col_val > 3:
            col_val = 0
            row_val += 1
    
    # Run the application
    root.mainloop()   

def button():
    
    def on_button_click():
        messagebox.showinfo("Button Clicked", "Hello, you clicked the button!")
    
    # Create the main window
    root = tk.Tk()
    root.geometry("400x300+100+100")  # Example: 400x300 size, positioned at (100, 100)
    root.title("Simple Button Example")


    # Create a button widget
    button = tk.Button(root, text="Click Me", command=on_button_click)
    
    # Add the button to the window
    button.pack(pady=20)
    
    # Start the Tkinter event loop
    root.mainloop()
    
def run():
    button()
    calculator()
    checkBox()
    focus()
    listBox()
    multiButton()
    menu()
    noteBook()
    progressBar()
    radioButton()
    showImage()
    textBox()    
    
run()
