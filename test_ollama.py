import subprocess
import json

def run_ollama(prompt, model='tinyllama'):
    result = subprocess.run(
        ['ollama', 'run', model],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output = result.stdout.decode()
    print("Ollama Response:")
    print(output)

run_ollama("Explain Playwright with an example.")
