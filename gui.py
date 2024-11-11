from tkinter import *
from tkinter import filedialog

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
The required syntax is as follows: Instruction_Name, Destination_Register, Register_1, Register_2, Address or Immediate\n
If any of these slots are not used, please place the comma but leave it empty.\n
Below are a few examples of instruction syntaxes:\n
\tANDI,x11,x12,,60\n
\tLW,x21,x22,,0xA0\n
\tXORI,x7,x8,,40\n
Make sure this syntax is followed, otherwise the simulator might not work as intended.\n\n
MEMORY:
Each variable you would like to initialize in the memory should have the following syntax: Address, Value\n
If the Value is a string, please use double quotation marks. And if the value is a char, please use single quotation marks.\n
Below are a few examples of variable intializations:\n
\t800, "Hello"\n
\t100, 3.14\n
\t488, '('\n
Enjoy using the simulator :)"""

syntaxLabel = Label(root, text=syntaxText, font=("Helvetica", 10), justify="left", anchor="nw", bg="#f0f0f0", wraplength=300)
syntaxLabel.grid(row=1, column=0, padx=(20, 10), sticky="nw")

# Label for credits
creditLabel = Label(root, text="Developed by Ahmed Fawzy, Ahmed Ayman, and Omar Leithy", font=("Helvetica", 8), fg="grey", bg="#f0f0f0")
creditLabel.grid(row=4, column=0, columnspan=3, pady=(20, 10), sticky="sw", padx=(20, 0))

# Frame to hold the instructions Text box and scrollbar
instructions_frame = Frame(root)
instructions_frame.grid(row=1, column=1, padx=(10, 5), pady=(10, 0), sticky="nsew")

# Label for Instructions Text box
instructionsLabel = Label(instructions_frame, text="Instructions", font=("Helvetica", 12, "bold"), bg="#f0f0f0")
instructionsLabel.pack(anchor="w")

# Instructions Text box with scrollbar
instructionsBox = Text(instructions_frame, height=20, width=35, font=("Courier", 10), wrap="word")
instructionsBox.pack(side="left", fill="both", expand=True)
instructionsScrollbar = Scrollbar(instructions_frame, command=instructionsBox.yview)
instructionsScrollbar.pack(side="right", fill="y")
instructionsBox.config(yscrollcommand=instructionsScrollbar.set)

# Frame to hold the memory Text box and scrollbar
memory_frame = Frame(root)
memory_frame.grid(row=1, column=2, padx=(5, 20), pady=(10, 0), sticky="nsew")

# Label for Memory Text box
memoryLabel = Label(memory_frame, text="Memory", font=("Helvetica", 12, "bold"), bg="#f0f0f0")
memoryLabel.pack(anchor="w")

# Memory Text box with scrollbar
memoryBox = Text(memory_frame, height=20, width=35, font=("Courier", 10), wrap="word")
memoryBox.pack(side="left", fill="both", expand=True)
memoryScrollbar = Scrollbar(memory_frame, command=memoryBox.yview)
memoryScrollbar.pack(side="right", fill="y")
memoryBox.config(yscrollcommand=memoryScrollbar.set)

# Configure row and column weights for layout stretching
root.grid_rowconfigure(1, weight=1)  # Allows row 1 to expand
root.grid_columnconfigure(1, weight=1)  # Allows column 1 to expand
root.grid_columnconfigure(2, weight=1)  # Allows column 2 to expand

# Function to load file content into the Instructions Text box
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
    # Create a new window for the simulation results
    sim_window = Toplevel(root)
    sim_window.title("Simulation Results")
    sim_window.geometry("400x400")

    # Add label and back button
    Label(sim_window, text="Simulation in Progress...", font=("Helvetica", 14)).pack(pady=20)
    Button(sim_window, text="Back", font=("Helvetica", 12), command=sim_window.destroy, bg="#666666", fg="white").pack(pady=20)

# Simulate button
simulateButton = Button(root, text="Simulate", font=("Helvetica", 12), command=simulate, bg="#666666", fg="white", padx=10, pady=5)
simulateButton.grid(row=3, column=2, pady=(20, 10), sticky="e", padx=(0, 20))

# Run the application
root.mainloop()
