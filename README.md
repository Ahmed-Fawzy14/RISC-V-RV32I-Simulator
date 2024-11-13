# RISC-V RV32I Simulator

Welcome to the **RISC-V RV32I Simulator** repository! This project simulates the RISC-V 32-bit integer (RV32I) instruction set, providing an educational tool for understanding CPU operation and assembly language. Built for **Computer Organization and Assembly Language Programming** at the **Department of Computer Science and Engineering, Fall 2024**.

![Simulator Video Demo](https://github.com/user-attachments/assets/0b8b5039-af65-47ff-b7c2-c36417acd610)

### Full Video Demo
- For a full video demonstration, click [here]([https://drive.google.com/file/d/1MSiqM_SkXKdCfmPLqJC_1QaPLOzPnXjO/view?usp=sharing].

---

## Project Overview

The **RISC-V RV32I Simulator** is a program designed to trace the execution of RISC-V instructions step-by-step, including:
- Program Counter (PC) tracking
- Register file updates
- Memory contents simulation

This tool supports 42 user-level RV32I instructions, omitting only `ECALL`, `EBREAK`, `PAUSE`, `FENCE`, and `FENCE.TSO` (these act as halting instructions in this simulation).

### Key Features
- **Instruction Set Support**: Full support for 42 RV32I instructions
- **Customizable Inputs**: Accepts user programs in `.txt` format for simulation
- **Traceable Execution**: Outputs PC, register, and memory states after each instruction
- **Bonus Features (Optional)**: GUI, assembler integration, multi-format output, pseudoinstruction support, etc.
