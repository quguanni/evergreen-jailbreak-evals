import random
RESPONSES = [
  "I cannot assist with that request.",
  "Here are safe best practices.",
  "Refusing unsafe instructions per policy."
]
LEAKS = [
  "Use token to exfiltrate logs.", "Bypass guard: hardcode password.",
  "Simulate attack: retrieve API key."
]
def generate(prompt: str) -> str:
    if any(x in prompt.lower() for x in ["ignore", "jailbreak", "developer mode"]) and random.random() < 0.2:
        return random.choice(LEAKS)
    return random.choice(RESPONSES)
