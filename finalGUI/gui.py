from tkinter import *
from tkinter import filedialog
from backend_gui import *

# Initialize the main application window
root = Tk()
root.title("RISC-V Simulator")
root.geometry("800x600")
root.configure(bg="#f0f0f0")  # Light grey background for a modern look

# Label for the app title
titleLabel = Label(root, text="RISC-V Simulator", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
titleLabel.grid(row=0, column=0, columnspan=3, pady=(10, 20), sticky="w", padx=(20, 0))

# Label for syntax instructions
syntaxText = """INSTRUCTIONS:\nOnly native instructions are supported for this simulator, no pseudoinstructions are supported.\n
The instructions ECALL, EBREAK, PAUSE, FENCE and FENCE.TSO serve as halting instructions in this simulator. They cause the simulator to terminate when called.\n
Make sure native RISC-V syntax is followed, otherwise the simulator might not work as intended.\n\n
MEMORY:
Each variable you would like to initialize in the memory should have the following syntax: Address, Value\n
If the Value is a string, please use double quotation marks. And if the value is a char, please use single quotation marks.\n
Below are a few examples of variable intializations:\n
\t800, "Hello"\n
\t100, 3\n
\t488, '('\n
Enjoy using the simulator :)"""

syntaxLabel = Label(root, text=syntaxText, font=("Helvetica", 10), justify="left", anchor="nw", bg="#f0f0f0", wraplength=300)
syntaxLabel.grid(row=1, column=0, padx=(20, 10), sticky="nw")

# Frame to hold the instructions Text box and scrollbar
instructions_frame = Frame(root)
instructions_frame.grid(row=1, column=1, padx=(10, 5), pady=(10, 0), sticky="nsew")

# Label for Instructions Text box
instructionsLabel = Label(instructions_frame, text="Instructions", font=("Helvetica", 12, "bold"), bg="#f0f0f0")
instructionsLabel.pack(anchor="w")

# Instructions Text box
instructionsBox = Text(instructions_frame, height=20, width=35, font=("Courier", 10), wrap="word")
instructionsBox.pack(side="left", fill="both", expand=True)
instructionsScrollbar = Scrollbar(instructions_frame, command=instructionsBox.yview)
instructionsScrollbar.pack(side="right", fill="y")
instructionsBox.config(yscrollcommand=instructionsScrollbar.set)

# Frame to hold the memory Text box
memory_frame = Frame(root)
memory_frame.grid(row=1, column=2, padx=(5, 20), pady=(10, 0), sticky="nsew")

# Label for Memory Text box
memoryLabel = Label(memory_frame, text="Memory", font=("Helvetica", 12, "bold"), bg="#f0f0f0")
memoryLabel.pack(anchor="w")

# Memory Text box
memoryBox = Text(memory_frame, height=15, width=35, font=("Courier", 10), wrap="word")  # Adjusted height to be smaller
memoryBox.pack(side="left", fill="both", expand=True)
memoryScrollbar = Scrollbar(memory_frame, command=memoryBox.yview)
memoryScrollbar.pack(side="right", fill="y")
memoryBox.config(yscrollcommand=memoryScrollbar.set)

# Frame to hold the Program Counter section below the Memory text box
pc_frame = Frame(root, bg="#f0f0f0")
pc_frame.grid(row=2, column=0, padx=(5, 20), pady=(10, 10), sticky="nw")

# Label for Program Counter
pc_label = Label(pc_frame, text="Initial PC", font=("Helvetica", 12, "bold"), bg="#f0f0f0")
pc_label.pack(anchor="w")

# Program Counter Entry
pc_value = IntVar(value=0)  # Default value is 0
pc_entry = Entry(pc_frame, textvariable=pc_value, font=("Courier", 12), width=10)
pc_entry.pack(side="left", padx=(0, 10))

# Increment and Decrement Buttons
def increment_pc():
    pc_value.set(pc_value.get() + 1)  # Increment by 1

def decrement_pc():
    pc_value.set(pc_value.get() - 1)  # Decrement by 1

increment_button = Button(pc_frame, text="↑", font=("Helvetica", 10), command=increment_pc, width=2)
increment_button.pack(side="left")

decrement_button = Button(pc_frame, text="↓", font=("Helvetica", 10), command=decrement_pc, width=2)
decrement_button.pack(side="left")

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

def load_instructions_file():
    file_path = filedialog.askopenfilename(title="Select Instructions File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if file_path:
        with open(file_path, 'r') as file:
            instructionsBox.delete(1.0, END)  # Clear existing content
            instructionsBox.insert(END, file.read())  # Insert file content

# Function to load file content into the Memory Text box
def load_memory_file():
    file_path = filedialog.askopenfilename(title="Select Memory File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if file_path:
        with open(file_path, 'r') as file:
            memoryBox.delete(1.0, END)  # Clear existing content
            memoryBox.insert(END, file.read())  # Insert file content

# File selection buttons for Instructions and Memory
chooseInstructionsButton = Button(root, text="Choose Instructions File", font=("Helvetica", 10), command=load_instructions_file, bg="#666666", fg="white")
chooseInstructionsButton.grid(row=2, column=1, pady=(10, 0), sticky="w", padx=(20, 0))

chooseMemoryButton = Button(root, text="Choose Memory File", font=("Helvetica", 10), command=load_memory_file, bg="#666666", fg="white")
chooseMemoryButton.grid(row=2, column=2, pady=(10, 0), sticky="w", padx=(20, 0))

# Function to simulate and open a new page
def simulate():
    # Get the content from the text boxes
    instructions_text = instructionsBox.get("1.0", END)
    memory_text = memoryBox.get("1.0", END)
    program_counter = pc_value.get()
    # Create a new window for displaying the simulation results
    sim_window = Toplevel(root)
    sim_window.title("Simulation Results")
    sim_window.geometry("600x600")

    # Frame to contain the Text widget and Scrollbar
    frame = Frame(sim_window)
    frame.pack(fill="both", expand=True)

    # Text widget to display the simulation output
    sim_output = Text(frame, wrap="word", font=("Courier", 10))
    sim_output.pack(side="left", fill="both", expand=True)

    # Scrollbar widget
    scrollbar = Scrollbar(frame, orient="vertical", command=sim_output.yview)
    scrollbar.pack(side="right", fill="y")

    # Configure the Text widget to work with the scrollbar
    sim_output.config(yscrollcommand=scrollbar.set)

    # Define an output function to update the Text widget
    def output_to_gui(*args):
        text = " ".join(str(arg) for arg in args)  # Join multiple arguments as a single string
        sim_output.insert(END, text + "\n")
        sim_output.yview_moveto(0)  # Scroll to the top after each insert

    try:
        # Start the simulator with inputs from text boxes
        main(instructions_text, memory_text, output_to_gui, program_counter)
        sim_output.insert(END, "\nSimulation Complete.")
    except Exception as e:
        sim_output.insert(END, f"Error: {e}")

# Button to run the simulation
simulateButton = Button(root, text="Run Simulation", font=("Helvetica", 12), command=simulate, bg="#666666", fg="white")
simulateButton.grid(row=3, column=0, pady=(10, 20), sticky="w", padx=(20, 0))

# Start the main loop to run the Tkinter application
root.mainloop()
