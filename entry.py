from client import call_ollama_model
from parser import parse_response
from playwright_actions import perform_action

def main():
    user_prompt = input(" What do you want to automate?\n> ")

    ollama_output = call_ollama_model(user_prompt)
    if not ollama_output:
        print(" No response from model.")
        return

    print("\n Raw Output from Ollama:\n", ollama_output)

    parsed_instruction = parse_response(ollama_output)
    if not parsed_instruction:
        print(" Couldn't parse instruction.")
        return

    print("\n Parsed instruction:\n", parsed_instruction)

    perform_action(parsed_instruction)

if __name__ == "__main__":
    main()
