from llama_cpp import Llama

llm = Llama(model_path="./models/ggml-alpaca-7b-q4.bin",
            max_tokens=100,
            temperature=0.9,
            top_p=0.95)

# Define the few-shot examples so AI model can have reference
examples = [
    {
        "input": "I like to eat sushi every day.",
        "output": "Positive"
    },
    {
        "input": "The movie was boring and the acting was terrible.",
        "output": "Negative"
    },
    {
        "input": "This is a neutral statement.",
        "output": "Neutral"
    }
]

# Create the few-shot prompt
prompt = ""
for example in examples:
    prompt += f"Input: {example['input']}\n"
    prompt += f"Output: {example['output']}\n\n"
prompt += "Input: {input}\n"
prompt += "Output: "

output = llm(prompt, max_tokens=100, stop=["\nInput"])

# Print the response
print(output["choices"][0]["text"])