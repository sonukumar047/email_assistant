# Smart Email Assistant with LangGraph + Groq

An intelligent, production-ready email automation system built with LangGraph and Groq API that automatically processes, classifies, and responds to customer emails with context-aware replies.


## Features

### Core Capabilities
-  Intent Classification: Automatically categorizes emails (complaint, request, feedback, inquiry)
-  Sentiment Analysis: Detects emotional tone (positive, neutral, negative)
-  Smart Summarization: Generates concise 2-3 line email summaries
-  Persistent Memory: JSON-based conversation history tracking
-  Context-Aware Replies: Generates appropriate responses based on history
-  Parallel Processing: Runs classification and sentiment analysis simultaneously
-  Configurable Tone: Choose from 4 tone styles (professional, friendly, formal, casual)
-  Smart Escalation: Multi-criteria decision logic for issue escalation

### Bonus Features
-  Feedback logging and tracking
-  Batch email processing
-  Interactive CLI mode


## Architecture

### Workflow Graph
```
Entry Point
    ↓
┌─────────────────────────────────┐
│ Classify & Analyze (Parallel)   │
│  ├─ Intent Classification       │
│  └─ Sentiment Analysis          │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Parallel Processing             │
│  ├─ Summarize Email            │
│  └─ Load Memory Context        │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Generate Reply (Sequential)     │
│  - Tone adaptation             │
│  - Context integration         │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Escalation Decision             │
│  - Repeat customer check       │
│  - Urgent keyword detection    │
│  - Sentiment analysis          │
└─────────────────────────────────┘
    ↓
  Output
```
### Tech Stack

- **Framework**: LangGraph (State machine orchestration)
- **LLM Provider**: Groq (Ultra-fast inference with LPUs)
- **Model**: llama-3.3-70b-versatile
- **Language**: Python 3.9+
- **Storage**: JSON-based persistent memory

## Installation

### Prerequisites

- Python 3.9 or higher
- Groq API key ([Get one here](https://console.groq.com))
- pip or conda package manager

### Step 1: Clone Repository


git clone https://github.com/yourusername/email-assistant.git
cd email-assistant


### Step 2: Create Virtual Environment

# Using venv
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate

### Step 3: Install Dependencies


pip install -r requirements.txt

### Step 4: Configure Environment

# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

## Configuration

### Environment Variables (.env)


# Required
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# Optional
LOG_LEVEL=INFO
MAX_HISTORY_LENGTH=5

### Application Settings (config.py)

# Model Configuration
DEFAULT_MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.3
MAX_TOKENS = 1000

# Tone Styles
DEFAULT_TONE = "professional"  professional, friendly, formal, casual

# Escalation Thresholds
REPEAT_THRESHOLD = 2  # Auto-escalate after N interactions
ESCALATION_KEYWORDS = ["urgent", "immediately", "refund", "terrible"]

# Memory Settings
MEMORY_FILE = "data/memory.json"
MAX_HISTORY_LENGTH = 5

## Usage

### Mode 1: Single Email Processing

Process a single email from JSON file:


python main.py --file test_emails/complaint.json --tone friendly


**Input Example** (`test_emails/complaint.json`):

{
  "from": "customer@example.com",
  "to": "support@company.com",
  "subject": "Payment issue",
  "body": "My payment failed twice. Please help!",
  "history": []
}


**Output**:

 EMAIL PROCESSING RESULT

 To: customer@example.com
 From: support@company.com
 Subject: Re: Payment issue

 Intent: REQUEST
 Sentiment: NEGATIVE
 Escalate: YES
   Reason: Urgent keywords detected: payment, failed

Reply Body:
Hi Customer,

I'm sorry to hear about the payment issues. I've escalated this to our 
billing team who will investigate immediately. You should receive a 
response within 24 hours.

Best regards,
Support Team

Processing Time: 2.73s

### Mode 2: Interactive Mode

Run interactive CLI for quick testing:

python main.py --interactive


You'll be prompted to enter:
- From email
- Subject
- Body
- Tone preference (1-4)

### Mode 3: Batch Processing

Process multiple emails from a directory:


python main.py --batch test_emails/

Output files saved to `output/` directory with summary report.

### Mode 4: Memory Management


# Clear memory for specific user
python main.py --clear-memory customer@example.com

# Clear all memory
python main.py --clear-memory all

### Available Tone Styles

| Tone | Use Case | Example Response Style |
|------|----------|----------------------|
| **professional** | Default business communication | "Thank you for contacting us. We will assist you..." |
| **friendly** | Casual, warm interactions | "Hi there! Thanks for reaching out! Let's get this sorted..." |
| **formal** | Official, corporate communication | "Dear Valued Customer, We acknowledge receipt of your inquiry..." |
| **casual** | Relaxed, conversational | "Hey! No worries, we'll fix this right up..." |

## 📁 Project Structure

```
email_assistant/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore rules
│
├── config.py                   # Application configuration
├── main.py                     # Main entry point
├── state.py                    # State management types
├── nodes.py                    # LangGraph node implementations
├── graph.py                    # Workflow graph builder
├── memory_manager.py           # Persistent memory handler
├── utils.py                    # Utility functions
│
├── data/
│   └── memory.json            # Conversation history storage
│
├── test_emails/               # Sample email test cases
│   ├── complaint.json         # Complaint intent
│   ├── request.json           # Request intent
│   ├── feedback.json          # Feedback intent
│   ├── inquiry.json           # Inquiry intent
│   └── request_urgent.json    # Urgent request
│
├── output/                    # Processing results
   ├── result.json           # Latest result
   └── batch_summary.json    # Batch processing summary
```


### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes 
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to all functions
- Maximum line length: 100 characters
- Run `black` formatter before committing


## Authors

Sonu Kumar

## Acknowledgments

- Built with [LangGraph](https://langchain-ai.github.io/langgraph/) by LangChain
- Powered by [Groq](https://groq.com/) ultra-fast LPU inference
- Inspired by the LangGraph Email Assistant assignment


---

**Made with ❤️ using LangGraph + Groq**
