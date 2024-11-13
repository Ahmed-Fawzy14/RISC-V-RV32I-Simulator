import subprocess
import sys

# Expected output for Test Case 1
expected_output = {
    1: 20,    # x1 should be 20
    2: 20,    # x2 should be 20
    3: 99,    # x3 should be 99
}

def run_simulator(file_path):
    """Run the RISC-V simulator with the given instruction file."""
    try:
        # Prepare the inputs for the simulator
        simulator_input = f"{file_path}\n0\n\n"  # file path, starting address, and empty memory init file
        
        # Run the simulator script and capture the output
        result = subprocess.run(
            [sys.executable, "rv32i_simulator_v1.py"],
            input=simulator_input,
            text=True,
            capture_output=True
        )
        return result.stdout
    except Exception as e:
        print(f"Error running the simulator: {e}")
        return None

def extract_registers(output):
    """Extract the final register values from the simulator output."""
    registers = [0] * 32
    lines = output.splitlines()

    in_decimal_section = False

    for line in lines:
        if "Decimal:" in line:
            in_decimal_section = True
            continue
        if "Binary:" in line or "Hexadecimal:" in line:
            in_decimal_section = False
            continue
        
        if in_decimal_section and "x" in line:
            parts = line.split("|")
            for part in parts:
                try:
                    reg, value = part.strip().split(":")
                    reg_num = int(reg[1:])  # Extract register number (e.g., x1 -> 1)
                    value = value.strip()

                    # Convert the value to an integer
                    registers[reg_num] = int(value)
                except ValueError as e:
                    print(f"Error parsing line '{line}': {e}")
                    continue

    return registers

def run_test(file_path, expected_output):
    """Run a single test case."""
    print(f"Running test: {file_path}")
    output = run_simulator(file_path)
    if not output:
        print("Error: No output from simulator.")
        return False

    # Extract register values from the output
    registers = extract_registers(output)
    
    # Check if the output matches the expected values
    test_passed = True
    for reg, expected_value in expected_output.items():
        actual_value = registers[reg]
        if actual_value != expected_value:
            print(f"Test failed for register x{reg}: Expected {expected_value}, Got {actual_value}")
            test_passed = False

    if test_passed:
        print("Test passed!")
    else:
        print("Some tests failed.")
    return test_passed

if __name__ == "__main__":
    # Define the path to the test file
    test_file = r"C:\Users\ahmed\OneDrive - YAT learning Solutions\AUC\Semesters\Fall 2024\Assembly\Project\RISC-V-RV32I-Simulator\Branch Instructions with Labels.txt"
    
    # Run the test
    run_test(test_file, expected_output)
