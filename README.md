# RISC-V RV32I Simulator

This project is a **RISC-V RV32I Simulator** developed for **Computer Organization and Assembly Language Programming** in **Fall 2024** at the **Department of Computer Science and Engineering** at **The American University in Cairo (AUC)**. The simulator provides a practical tool for understanding the operation of the RISC-V RV32I instruction set by allowing users to trace instruction execution step-by-step.

![Simulator Video Demo](https://github.com/user-attachments/assets/0b8b5039-af65-47ff-b7c2-c36417acd610)

### Full Video Demo
  - For a full video demonstration, click [here](https://drive.google.com/file/d/1MSiqM_SkXKdCfmPLqJC_1QaPLOzPnXjO/view?usp=sharing).

---

## Project Overview

The **RISC-V RV32I Simulator** supports a broad range of instructions to allow users to simulate basic CPU functionalities, including:
- **Program Counter (PC) tracking**
- **Register File Management**: Registers are initialized and updated per instruction.
- **Memory Management**: Relevant memory locations are tracked without the need for allocating the entire address space.

The simulator supports 42 RV32I instructions, with halting functionality for unsupported instructions like `ECALL`, `EBREAK`, `PAUSE`, `FENCE`, and `FENCE.TSO`.

### Key Features
- **Comprehensive Instruction Support**: Includes the entire 32-bit integer base instruction set (RV32I)
- **Traceable Execution**: Provides updates for PC, registers, and memory after each instruction
- **Flexible Input**: Allows users to input assembly instructions through text files or manual entry
- **Bonus Functionalities**: Includes options for GUI and multi-format output (binary, hexadecimal, etc.)

---

## Getting Started

### Prerequisites
- **Python 3.x** is required to run the simulator.

### Running the Simulator

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/Ahmed-Fawzy14/RISC-V-RV32I-Simulator/tree/main.git
    cd RISC-V-RV32I-Simulator
    ```

2. **Prepare Your Instruction Files**:
   Save assembly programs as `.txt` files and place them in the designated `instructions/` folder, or enter them manually when prompted.

3. **Run the Simulator**:
   Start the simulator with:
   ```bash
   python3 simulator.py

### Team Members
Name: Ahmed Ayman Elkhodary
ID: 900213472
Email: aae121@aucegypt.edu

Name: Ahmed Fawzy Abdelkader
ID: 900222633
Email: ahmed-fawzy@aucegypt.edu

Name: Omar Leithy
ID: 900221663
Email: omarleithym@aucegypt.edu

