"""
Enhanced node implementations with parallel processing support
"""
import os
import time
from typing import Dict, Tuple
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from state import EmailState
from config import (
    DEFAULT_MODEL, TEMPERATURE, MAX_TOKENS, 
    VALID_INTENTS, ESCALATION_KEYWORDS, REPEAT_THRESHOLD
)
import logging

logger = logging.getLogger(__name__)

# Initialize Groq LLM
llm = ChatGroq(
    model=DEFAULT_MODEL,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# ==================== PARALLEL PROCESSING NODES ====================

def classify_and_analyze_parallel(state: EmailState) -> Dict:
    """
    ENHANCED: Classify intent and analyze sentiment in parallel
    Returns: intent, sentiment, and confidence
    """
    start_time = time.time()
    
    # Define classification prompt
    classify_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an email classification expert. Classify the intent into exactly one category:
- complaint: Customer is unhappy or reporting an issue
- request: Customer needs help or wants something done
- feedback: Customer is sharing opinions or suggestions
- inquiry: Customer is asking for information

Respond with ONLY the category name in lowercase."""),
        ("user", "Email: {body}")
    ])
    
    # Define sentiment analysis prompt
    sentiment_prompt = ChatPromptTemplate.from_messages([
        ("system", """Analyze the sentiment of this email. Respond with one word:
- positive: Happy, satisfied, grateful tone
- neutral: Factual, informative tone
- negative: Frustrated, angry, disappointed tone"""),
        ("user", "Email: {body}")
    ])
    
    # Create parallel runnable
    parallel_chain = RunnableParallel(
        intent=classify_prompt | llm,
        sentiment=sentiment_prompt | llm
    )
    
    # Execute in parallel
    result = parallel_chain.invoke({"body": state["body"]})
    
    # Parse results
    intent = result["intent"].content.strip().lower()
    sentiment = result["sentiment"].content.strip().lower()
    
    # Validate intent
    if intent not in VALID_INTENTS:
        intent = "inquiry"
        logger.warning(f"Invalid intent detected, defaulting to 'inquiry'")
    
    elapsed = time.time() - start_time
    logger.info(f"✓ Parallel analysis completed in {elapsed:.2f}s: intent={intent}, sentiment={sentiment}")
    
    return {
        "intent": intent,
        "sentiment": sentiment,
        "confidence": 0.95 if intent in VALID_INTENTS else 0.5
    }


def summarize_node(state: EmailState) -> Dict:
    """
    Node: Summarize the email content
    Returns: 2-3 line summary with sender's tone
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Summarize the email in 2-3 concise sentences. 
Focus on:
1. The main point or request
2. Key details mentioned
3. The sender's tone (urgent, polite, frustrated, etc.)"""),
        ("user", "Email:\nSubject: {subject}\nBody: {body}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "subject": state["subject"],
        "body": state["body"]
    })
    summary = response.content.strip()
    
    logger.info(f"✓ Summary generated: {summary[:80]}...")
    return {"summary": summary}


def memory_node(state: EmailState) -> Dict:
    """
    ENHANCED: Build conversation context from persistent history
    Returns: merged context string with interaction count
    """
    from memory_manager import MemoryManager
    
    memory_mgr = MemoryManager()
    email_from = state["email_from"]
    
    # Load from persistent storage
    history = memory_mgr.load_memory(email_from)
    interaction_count = len(history)
    
    if not history:
        memory_context = "This is the first interaction with this customer."
    else:
        # Format history into readable context
        context_parts = [f"Customer has contacted us {interaction_count} time(s) before:"]
        
        for idx, msg in enumerate(history[-3:], 1):  # Last 3 interactions
            timestamp = msg.get("timestamp", "Unknown time")
            intent = msg.get("intent", "unknown")
            body_preview = msg.get("body", "")[:100]
            escalated = msg.get("escalated", False)
            
            context_parts.append(
                f"{idx}. [{timestamp}] Intent: {intent}, "
                f"Escalated: {escalated}\n   Preview: {body_preview}..."
            )
        
        memory_context = "\n".join(context_parts)
    
    logger.info(f"✓ Memory context built: {interaction_count} previous interactions")
    return {"memory_context": memory_context}


def generate_reply_node(state: EmailState) -> Dict:
    """
    ENHANCED: Generate contextual email reply with configurable tone
    Returns: reply subject and body with tone matching configuration
    """
    intent = state["intent"]
    sentiment = state.get("sentiment", "neutral")
    summary = state["summary"]
    memory = state["memory_context"]
    original_subject = state["subject"]
    sender_name = state["email_from"].split("@")[0].capitalize()
    tone_style = state.get("tone_style", "professional")
    
    # Enhanced tone mapping with style variations
    tone_instructions = {
        "complaint": {
            "professional": "empathetic and solution-focused. Acknowledge the issue professionally.",
            "friendly": "warm and understanding. Show genuine care about their problem.",
            "formal": "respectful and apologetic. Maintain formal business language.",
            "casual": "relaxed but caring. Address the issue conversationally."
        },
        "request": {
            "professional": "helpful and action-oriented. Clearly explain next steps.",
            "friendly": "enthusiastic and supportive. Make them feel valued.",
            "formal": "precise and informative. Use formal business protocol.",
            "casual": "easy-going and helpful. Keep it simple and clear."
        },
        "feedback": {
            "professional": "appreciative and thoughtful. Thank them for their input.",
            "friendly": "warm and grateful. Express genuine excitement for their feedback.",
            "formal": "respectful and acknowledging. Use formal appreciation language.",
            "casual": "enthusiastic and thankful. Keep it light and appreciative."
        },
        "inquiry": {
            "professional": "informative and clear. Provide comprehensive information.",
            "friendly": "helpful and engaging. Make the explanation easy to understand.",
            "formal": "precise and detailed. Use formal informational language.",
            "casual": "straightforward and helpful. Explain simply."
        }
    }
    
    tone = tone_instructions.get(intent, {}).get(
        tone_style, 
        "professional and courteous"
    )
    
    # Sentiment adjustments
    sentiment_adjustment = ""
    if sentiment == "negative":
        sentiment_adjustment = "\nThe customer sounds frustrated. Use extra empathy."
    elif sentiment == "positive":
        sentiment_adjustment = "\nThe customer is positive. Match their energy."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a customer support agent writing email replies.

Tone: {tone}
Tone Style: {tone_style}
{sentiment_adjustment}

Rules:
1. Address the customer by name ({sender_name})
2. Reference their specific issue or question
3. Be concise but complete (3-5 sentences)
4. Use conversation history to provide context-aware responses
5. If this is a repeat issue, acknowledge it explicitly
6. End with an appropriate closing based on tone style
7. Match the tone to both the intent type and style preference"""),
        ("user", """Generate a reply for this email:

Intent: {intent}
Sentiment: {sentiment}
Summary: {summary}

Conversation History:
{memory}

Original Subject: {subject}

Format your response as:
Subject: [your subject line]
Body: [your email body]""")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "intent": intent,
        "sentiment": sentiment,
        "summary": summary,
        "memory": memory,
        "subject": original_subject
    })
    
    # Parse response
    content = response.content.strip()
    
    try:
        # Split by first newline after "Subject:"
        if "Subject:" in content:
            parts = content.split("\n", 1)
            reply_subject = parts[0].replace("Subject:", "").strip()
            
            # Extract body after "Body:"
            if len(parts) > 1 and "Body:" in parts[1]:
                reply_body = parts[1].split("Body:", 1)[1].strip()
            else:
                reply_body = parts[1].strip() if len(parts) > 1 else content
        else:
            reply_subject = f"Re: {original_subject}" if not original_subject.startswith("Re:") else original_subject
            reply_body = content
    except Exception as e:
        logger.error(f"Error parsing reply: {e}")
        reply_subject = f"Re: {original_subject}"
        reply_body = content
    
    logger.info(f"✓ Reply generated with {intent}/{tone_style} tone")
    return {
        "reply_subject": reply_subject,
        "reply_body": reply_body
    }


def decision_node(state: EmailState) -> Dict:
    """
    ENHANCED: Advanced escalation decision with multiple criteria
    Returns: escalate flag and reason
    """
    intent = state["intent"]
    sentiment = state.get("sentiment", "neutral")
    body = state["body"].lower()
    
    should_escalate = False
    escalation_reason = None
    
    # Criteria 1: Negative sentiment complaints
    if intent == "complaint" and sentiment == "negative":
        should_escalate = True
        escalation_reason = "Negative sentiment detected in complaint"
    
    # Criteria 2: Urgent keywords detected
    urgent_keywords_found = [kw for kw in ESCALATION_KEYWORDS if kw in body]
    if urgent_keywords_found:
        should_escalate = True
        escalation_reason = f"Urgent keywords detected: {', '.join(urgent_keywords_found[:3])}"
    
    # Criteria 3: Repeat customer issues
    from memory_manager import MemoryManager
    memory_mgr = MemoryManager()
    interaction_count = memory_mgr.get_interaction_count(state["email_from"])
    
    if interaction_count >= REPEAT_THRESHOLD:
        should_escalate = True
        escalation_reason = f"Repeat customer ({interaction_count} previous interactions)"
    
    # Criteria 4: LLM-based severity check for complaints
    if intent == "complaint" and not should_escalate:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze if this complaint requires escalation to senior support.
Escalate if:
- Very strong negative emotions
- Mentions legal action or regulatory complaints
- Complex technical issue beyond basic support
- Multiple failures or problems mentioned

Respond with only 'yes' or 'no'"""),
            ("user", "Email: {body}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"body": state["body"]})
        
        if "yes" in response.content.lower():
            should_escalate = True
            escalation_reason = "Complex issue requiring senior support"
    
    escalate_status = "YES" if should_escalate else "NO"
    logger.info(f"✓ Escalation decision: {escalate_status}" + 
                (f" - Reason: {escalation_reason}" if escalation_reason else ""))
    
    return {
        "escalate": should_escalate,
        "escalation_reason": escalation_reason
    }
