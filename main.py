"""
Main entry point for the Medical Report Diagnosis Agentic System
Continuous terminal-based interface
"""
import sys
from pathlib import Path
from graph.workflow import run_workflow
from tools.ocr_tools import cleanup_temp_files


def print_banner():
    """Prints the welcome banner"""
    print("\n" + "="*70)
    print("  MEDICAL REPORT DIAGNOSIS AGENTIC SYSTEM")
    print("  Continuous Terminal Interface")
    print("="*70)
    print("\nCommands:")
    print("  --file <path>     : Process a file (PDF, image, audio)")
    print("  --text <message>  : Send a text message or query")
    print("  --patient <id>    : Set current patient ID (default: pt-001)")
    print("  --help            : Show this help message")
    print("  --exit / quit     : Exit the system")
    print("="*70 + "\n")


def print_help():
    """Prints help information"""
    print("\n" + "="*70)
    print("  HELP - How to Use")
    print("="*70)
    print("\nFile Processing:")
    print("  --file report.pdf")
    print("  --file scan.jpg")
    print("  --file symptoms.mp3")
    print("\nText Queries:")
    print("  --text What is my cholesterol level?")
    print("  --text Show me my medical history")
    print("  --text Blood pressure: 145/90, Glucose: 110 mg/dL")
    print("\nChange Patient:")
    print("  --patient pt-002")
    print("\nCombined:")
    print("  --patient pt-001 --file report.pdf")
    print("\nExamples:")
    print("  > --text What were my last test results?")
    print("  > --file blood-test.pdf")
    print("  > --patient pt-002 --text Show history")
    print("="*70 + "\n")


def parse_command(command: str, current_patient: str) -> dict:
    """
    Parses user command
    
    Args:
        command: User input string
        current_patient: Current patient ID
        
    Returns:
        Dictionary with parsed command details
    """
    command = command.strip()
    
    # Handle special commands
    if command.lower() in ['--exit', 'exit', 'quit', '--quit']:
        return {"action": "exit"}
    
    if command.lower() in ['--help', 'help']:
        return {"action": "help"}
    
    if not command:
        return {"action": "empty"}
    
    # Parse arguments
    result = {
        "action": "process",
        "file_path": None,
        "text_input": None,
        "patient_id": current_patient
    }
    
    # Check for --patient flag
    if '--patient' in command:
        parts = command.split('--patient', 1)
        command = parts[0].strip()
        patient_part = parts[1].strip()
        # Extract patient ID (first word after --patient)
        patient_words = patient_part.split()
        if patient_words:
            result["patient_id"] = patient_words[0]
            # Remove patient ID from command
            remaining = ' '.join(patient_words[1:])
            command = command + ' ' + remaining
    
    command = command.strip()
    
    # Check for --file flag
    if '--file' in command:
        parts = command.split('--file', 1)
        if len(parts) > 1:
            file_path = parts[1].strip().split()[0]  # Get first word after --file
            result["file_path"] = file_path
            # Remove --file part for text processing
            remaining_text = ' '.join(parts[1].strip().split()[1:])
            command = parts[0].strip() + ' ' + remaining_text
    
    # Check for --text flag
    if '--text' in command:
        parts = command.split('--text', 1)
        if len(parts) > 1:
            result["text_input"] = parts[1].strip()
    elif not result["file_path"] and command:
        # If no explicit --text flag but there's text, treat it as text input
        result["text_input"] = command
    
    # Validate
    if not result["file_path"] and not result["text_input"]:
        return {"action": "invalid", "message": "Please provide either --file or --text"}
    
    return result


def process_command(cmd_dict: dict) -> str:
    """
    Processes a parsed command
    
    Args:
        cmd_dict: Parsed command dictionary
        
    Returns:
        Response string
    """
    try:
        file_path = cmd_dict.get("file_path")
        text_input = cmd_dict.get("text_input")
        patient_id = cmd_dict.get("patient_id", "pt-001")
        
        # Determine input type
        if file_path:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                return f"ERROR: File not found: {file_path}"
            
            # Determine file type
            suffix = file_path_obj.suffix.lower()
            
            if suffix == ".pdf":
                input_type = "pdf"
            elif suffix in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
                input_type = "image"
            elif suffix in [".mp3", ".wav", ".m4a", ".flac"]:
                input_type = "audio"
            else:
                return f"ERROR: Unsupported file type: {suffix}"
            
            print(f"\n📄 Processing {input_type.upper()} file: {file_path}")
            print(f"👤 Patient ID: {patient_id}")
            print("⏳ Please wait...\n")
            
            # Run workflow
            result = run_workflow(
                input_type=input_type,
                file_path=str(file_path_obj),
                patient_id=patient_id
            )
            
            # Cleanup
            cleanup_temp_files()
            
            return result.get("final_response", "No response generated")
        
        elif text_input:
            print(f"\n💬 Processing text query")
            print(f"👤 Patient ID: {patient_id}")
            print("⏳ Please wait...\n")
            
            # Run workflow
            result = run_workflow(
                input_type="text",
                text_input=text_input,
                patient_id=patient_id
            )
            
            return result.get("final_response", "No response generated")
        
        else:
            return "ERROR: No input provided"
            
    except Exception as e:
        cleanup_temp_files()
        return f"ERROR: {str(e)}"


def main():
    """
    Main continuous loop for terminal interface
    """
    print_banner()
    
    current_patient = "pt-001"
    
    print(f"Current Patient ID: {current_patient}")
    print("Type --help for usage information\n")
    
    while True:
        try:
            # Get user input
            user_input = input(f"[{current_patient}] > ").strip()
            
            if not user_input:
                continue
            
            # Parse command
            cmd_dict = parse_command(user_input, current_patient)
            
            # Handle actions
            if cmd_dict["action"] == "exit":
                print("\n👋 Thank you for using Medical Agentic System. Goodbye!\n")
                break
            
            elif cmd_dict["action"] == "help":
                print_help()
                continue
            
            elif cmd_dict["action"] == "empty":
                continue
            
            elif cmd_dict["action"] == "invalid":
                print(f"\n❌ {cmd_dict.get('message')}\n")
                continue
            
            elif cmd_dict["action"] == "process":
                # Update current patient if changed
                if cmd_dict["patient_id"] != current_patient:
                    current_patient = cmd_dict["patient_id"]
                    print(f"\n✓ Switched to Patient ID: {current_patient}\n")
                
                # Process the command
                response = process_command(cmd_dict)
                print(f"\n{response}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Type --exit to quit or continue...\n")
            continue
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")
            continue


if __name__ == "__main__":
    main()