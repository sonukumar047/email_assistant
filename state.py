"""
Enhanced state management with tone control
"""
from typing import TypedDict, List, Dict, Optional, Literal
from datetime import datetime

ToneStyle = Literal["professional", "friendly", "formal", "casual"]

class EmailState(TypedDict):
    """Enhanced state object for email processing workflow"""
    # Input fields
    email_from: str
    email_to: str
    subject: str
    body: str
    history: List[Dict[str, str]]
    
    # Configuration
    tone_style: ToneStyle  # NEW: Configurable tone
    
    # Processing fields
    intent: Optional[str]
    summary: Optional[str]
    memory_context: Optional[str]
    sentiment: Optional[str]  # NEW: Detected sentiment
    
    # Output fields
    reply_subject: Optional[str]
    reply_body: Optional[str]
    escalate: bool
    escalation_reason: Optional[str]  # NEW: Why escalation needed
    confidence: Optional[float]
    
    # Metadata
    processed_at: Optional[str]
    processing_time: Optional[float]
