# Claude Agent Demo

A simple demo agent built with the Claude SDK (Anthropic) using **Claude Sonnet 4.5** - Anthropic's smartest model for complex agents and coding.

## Setup

### 1. Activate the conda environment
```bash
conda activate claude-agent
```

### 2. Set up your API key

Create a `.env` file in the project root:
```bash
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

Or manually create `.env` with:
```
ANTHROPIC_API_KEY=sk-ant-...
```

Get your API key from: https://console.anthropic.com/

### 3. Run the agent

```bash
python agent.py
```

## Features

- **Simple Agent**: One-shot interactions with Claude
- **Interactive Agent**: Maintains conversation context for multi-turn dialogues

## Project Structure

```
makethempay/
├── agent.py           # Main agent implementation
├── requirements.txt   # Python dependencies
├── .env              # API key (not in git)
├── .gitignore        # Git ignore rules
└── README.md         # This file
```

## Usage Examples

### Simple one-shot query
The script automatically runs a simple example when executed.

### Interactive mode
After the simple example, you'll enter interactive mode where you can have a conversation with the agent. Type `quit` or `exit` to end.

# AI_Payment_Concierge
