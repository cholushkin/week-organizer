from openai import OpenAI

# features:
# - summarize the week
# - generate remarks for the tasks (starting points, hints)

# Function to read API key from a file
def read_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Function to get response from ChatGPT API
def get_chatgpt_response(prompt, api_key):
        
    client = OpenAI( api_key=api_key )


    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use the appropriate model
            messages=[
                {"role": "system", "content": "You are a helpful assistant. You provide short and precise information."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,  # Adjust the number of tokens as needed
            n=1,
            stop=None,
            temperature=0.7,  # Adjust the temperature for more creative (higher) or deterministic (lower) responses
        )
        return chat_completion.choices[0].message['content'].strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    # Read API key from file
    api_key = read_api_key('chatgpt-api-key.txt')
    
    # Array of hardcoded prompts
    prompts = [
        "What is the capital of France?",
       ## "Explain the theory of relativity.",
       ## "What are the benefits of using renewable energy?",
       ## "Tell me a joke.",
       ## "How does photosynthesis work?",
    ]
    
    # Get and print responses for each prompt
    for idx, prompt in enumerate(prompts, start=1):
        response = get_chatgpt_response(prompt, api_key)
        print(f"Prompt {idx}: {prompt}")
        print(f"Response {idx}: {response}\n")

if __name__ == "__main__":
    main()
