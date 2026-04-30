import ollama

model = "hf.co/bartowski/Llama-3.2-3B-Instruct-GGUF:Q4_K_M"

prompt = "Are you working?"

# example with ollama.generate() with parameters and print response
"""
response = ollama.generate(
    model="hf.co/bartowski/Llama-3.2-3B-Instruct-GGUF:Q4_K_M",
    prompt="Are you working?",
    options = { # use options to wrap model parameters
        "temperature": 1.0,  # 0.0-2.0, higher = more creative
        "top_p": 0.9,        # 0.0-1.0, most likely words
    }
)

print(response['response'])  # Note: 'response', not 'message'
"""

# proper way to use ollama methods
response = ollama.chat(
    model=model, 
    messages=[
        {'role':'user', 
        'content':prompt
        }
    ],
    options = {
        "temperature": 1.0,
        "top_p": 0.9
    }
)

print(type(response))
print(response['message']['content'])