from llama_cpp import Llama

# Define the llama model path + tuning the parameters for better response generation
llm = Llama(model_path="./models/ggml-alpaca-7b-q4.bin",
            max_tokens=100,
            temperature=0.9,
            top_p=0.95)

# another way to print the response
# output = llm(question, model_path="./models/ggml-alpaca-7b-q4.bin", max_tokens=100, temperature=0.9, top_p=0.95)

# Initialize the question and get the response from the model
question = "What is the best database client for an offline application"
response = llm(question)

# Print the response
print(response)