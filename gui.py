from tkinter import *

# Initialize the main application window
root = Tk()
root.title("RISC-V Simulator")
root.geometry("700x600")
root.configure(bg="#f0f0f0")  # Light grey background for a modern look

# Label for the app title
titleLabel = Label(root, text="RISC-V Simulator", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
titleLabel.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w", padx=(20, 0))

# Label for syntax instructions
syntaxText = """Only native instructions are supported for this simulator, no pseudoinstructions are supported.\n
The instructions ECALL, EBREAK, PAUSE, FENCE and FENCE.TSO serve as halting instructions in this simulator. They cause the simulator to terminate when called.\n
The required syntax is as follows: Instruction_Name, Destination_Register, Register_1, Register_2, Address or Immediate\n
If any of these slots are not used, please place the comma but leave it empty.\n
Below are a few examples of instruction syntaxes:\n
\tANDI,x11,x12,,60\n
\tLW,x21,x22,,0xA0\n
\tXORI,x7,x8,,40\n
Make sure this syntax is followed, otherwise the simulator might not work as intended.\n
Enjoy using the simulator :)"""

syntaxLabel = Label(root, text=syntaxText, font=("Helvetica", 10), justify="left", anchor="nw", bg="#f0f0f0", wraplength=300)
syntaxLabel.grid(row=1, column=0, padx=(20, 10), sticky="nw")

# Label for credits
creditLabel = Label(root, text="Developed by Ahmed Fawzy, Ahmed Ayman, and Omar Leithy", font=("Helvetica", 8), fg="grey", bg="#f0f0f0")
creditLabel.grid(row=3, column=0, columnspan=2, pady=(20, 10), sticky="sw", padx=(20, 0))

# Frame to hold the Text box and scrollbar
text_frame = Frame(root)
text_frame.grid(row=1, column=1, padx=(10, 20), pady=(10, 0), sticky="nsew")

# Text box for user instructions with scrollbar
instructionsBox = Text(text_frame, height=25, width=50, font=("Courier", 10), wrap="word")
instructionsBox.pack(side="left", fill="both", expand=True)

# Scrollbar for the text box
scrollbar = Scrollbar(text_frame, command=instructionsBox.yview)
scrollbar.pack(side="right", fill="y")
instructionsBox.config(yscrollcommand=scrollbar.set)

# Configure row and column weights for layout stretching
root.grid_rowconfigure(1, weight=1)  # Allows row 1 to expand
root.grid_columnconfigure(1, weight=1)  # Allows column 1 to expand

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
simulateButton.grid(row=2, column=1, pady=(20, 10), sticky="e", padx=(0, 20))

# Run the application
root.mainloop()
