"""
Utility functions for email processing
"""
import json
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def load_test_email(filepath: str) -> Dict:
    """Load a test email from JSON file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded test email from {filepath}")
        return data
    except Exception as e:
        logger.error(f"Error loading test email: {e}")
        raise

def save_result(result: Dict, output_file: str = "output/result.json"):
    """Save processing result to file"""
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Result saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving result: {e}")

def format_output(result: Dict) -> str:
    """Format result for console display"""
    output = []
    output.append("=" * 70)
    output.append("EMAIL PROCESSING RESULT")
    output.append("=" * 70)
    output.append(f"To: {result['to']}")
    output.append(f"From: {result['from']}")
    output.append(f"Subject: {result['subject']}")
    output.append(f"Intent: {result['intent'].upper()}")
    output.append(f"Sentiment: {result.get('sentiment', 'N/A').upper()}")
    output.append(f"Escalate: {'YES' if result['escalate'] else 'NO'}")
    
    if result.get('escalation_reason'):
        output.append(f"   Reason: {result['escalation_reason']}")
    
    output.append(f"Reply Body:\n{result['body']}")
    output.append(f"Processing Time: {result.get('processing_time', 0):.2f}s")
    output.append("=" * 70)
    
    return "\n".join(output)
