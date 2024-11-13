import subprocess
import sys

#Expected output for Test Case 1
expected_output = {
    1: 10,
    2: 15,
    3: 25,
    4: 15,
    5: 1,
    6: 3,
    7: 6,
    8: 1,
    9: 1
}

def run_simulator(file_path):
    """Run the RISC-V simulator with the given instruction file."""
    try:
        # Run the simulator script and capture the output
        result = subprocess.run(
            [sys.executable, "rv32i_simulator_v1.py"],
            input=f"{file_path}\n0\n\n",  # Provide the inputs to the script
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

    # Flag to indicate we are in the "Decimal" section
    in_decimal_section = False

    for line in lines:
        # Skip header lines
        if "Decimal:" in line:
            in_decimal_section = True
            continue
        if "Binary:" in line or "Hexadecimal:" in line:
            in_decimal_section = False
            continue
        
        # Only process lines after "Decimal:" header
        if in_decimal_section and "x" in line:
            parts = line.split("|")
            for part in parts:
                try:
                    reg, value = part.strip().split(":")
                    reg_num = int(reg[1:])  # Extract register number (e.g., x1 -> 1)
                    value = value.strip()

                    # Convert the value to an integer based on its format
                    if value.startswith("0b"):
                        registers[reg_num] = int(value, 2)  # Binary
                    elif value.startswith("0x"):
                        registers[reg_num] = int(value, 16)  # Hexadecimal
                    else:
                        registers[reg_num] = int(value)  # Decimal
                except ValueError:
                    # Skip lines that do not match the expected format
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
    for reg, expected_value in expected_output.items():
        actual_value = registers[reg]
        if actual_value != expected_value:
            print(f"Test failed for register x{reg}: Expected {expected_value}, Got {actual_value}")
            return False
    
    print("Test passed!")
    return True

if __name__ == "__main__":
    # Define the path to the test file
    test_file = r"C:\Users\ahmed\OneDrive - YAT learning Solutions\AUC\Semesters\Fall 2024\Assembly\Project\RISC-V-RV32I-Simulator\Tests\Arithmatic and Logical Test.txt"
    
    # Run the test
    if run_test(test_file, expected_output):
        print("All tests passed!")
    else:
        print("Some tests failed.")
