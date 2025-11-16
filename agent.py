import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model configuration - Claude Sonnet 4.5
MODEL = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5 - smartest model for complex agents and coding
MAX_TOKENS = 4096  # Sonnet 4.5 supports up to 64K tokens output

# Initialize the Claude client
client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def simple_agent(user_message: str) -> str:
    """
    A simple agent that uses Claude to respond to user messages.
    
    Args:
        user_message: The user's input message
        
    Returns:
        The agent's response as a string
    """
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

def interactive_agent():
    """
    An interactive agent that maintains conversation context.
    """
    conversation_history = []
    
    print("🤖 Simple Claude Agent Demo")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the conversation\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye! 👋")
            break
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get response from Claude
        try:
            print("Agent: ", end="", flush=True)
            message = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=conversation_history
            )
            
            response = message.content[0].text
            print(f"{response}\n")
            
            # Add assistant response to history
            conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key:")
        print("  ANTHROPIC_API_KEY=your_api_key_here")
        exit(1)
    
    # Example 1: Simple one-shot interaction
    print("=== Example 1: Simple Agent ===\n")
    response = simple_agent("Hello! Can you introduce yourself in one sentence?")
    print(f"Agent: {response}\n")
    
    # Example 2: Interactive conversation
    print("=== Example 2: Interactive Agent ===\n")
    interactive_agent()

