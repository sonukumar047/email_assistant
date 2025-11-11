"""
Enhanced main application with all bonus features
"""
import json
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

from graph import create_email_workflow
from state import EmailState, ToneStyle
from memory_manager import MemoryManager
from utils import load_test_email, save_result, format_output
from config import DEFAULT_TONE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_email(
    email_input: dict, 
    tone_style: ToneStyle = DEFAULT_TONE,
    save_to_memory: bool = True
) -> dict:
    """
    Process an incoming email through the enhanced LangGraph workflow
    
    Args:
        email_input: Dictionary containing email data
        tone_style: Response tone (professional/friendly/formal/casual)
        save_to_memory: Whether to save interaction to persistent memory
        
    Returns:
        Dictionary with structured reply and metadata
    """
    start_time = time.time()
    
    # Create workflow
    app = create_email_workflow()
    
    # Prepare initial state
    initial_state: EmailState = {
        "email_from": email_input["from"],
        "email_to": email_input["to"],
        "subject": email_input["subject"],
        "body": email_input["body"],
        "history": email_input.get("history", []),
        "tone_style": tone_style,
        "intent": None,
        "summary": None,
        "memory_context": None,
        "sentiment": None,
        "reply_subject": None,
        "reply_body": None,
        "escalate": False,
        "escalation_reason": None,
        "confidence": None,
        "processed_at": None,
        "processing_time": None
    }
    
    # Run the workflow
    logger.info("Starting Enhanced Email Processing Workflow...")
    logger.info(f"   Tone Style: {tone_style}")
    
    try:
        final_state = app.invoke(initial_state)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Format output
        output = {
            "subject": final_state["reply_subject"],
            "body": final_state["reply_body"],
            "to": final_state["email_from"],
            "from": final_state["email_to"],
            "intent": final_state["intent"],
            "sentiment": final_state.get("sentiment", "unknown"),
            "escalate": final_state["escalate"],
            "escalation_reason": final_state.get("escalation_reason"),
            "confidence": final_state.get("confidence", 0.0),
            "tone_style": tone_style,
            "processed_at": datetime.now().isoformat(),
            "processing_time": round(processing_time, 2)
        }
        
        # Save to persistent memory
        if save_to_memory:
            memory_mgr = MemoryManager()
            memory_mgr.save_interaction(
                email_from=final_state["email_from"],
                email_to=final_state["email_to"],
                subject=final_state["subject"],
                body=final_state["body"],
                intent=final_state["intent"],
                reply_body=final_state["reply_body"],
                escalated=final_state["escalate"]
            )
        
        logger.info(f"✅ Processing complete in {processing_time:.2f}s")
        return output
        
    except Exception as e:
        logger.error(f"Error processing email: {e}", exc_info=True)
        raise


def interactive_mode():
    """Interactive CLI for testing different tone styles"""
    print("\n" + "="*70)
    print("EMAIL ASSISTANT - INTERACTIVE MODE")
    print("="*70)
    
    # Get email input
    print("\nEnter email details:")
    from_addr = input("From: ").strip() or "customer@example.com"
    subject = input("Subject: ").strip() or "Test email"
    body = input("Body: ").strip() or "This is a test email"
    
    # Get tone preference
    print("\nSelect tone style:")
    print("1. Professional (default)")
    print("2. Friendly")
    print("3. Formal")
    print("4. Casual")
    
    tone_choice = input("Choice (1-4): ").strip() or "1"
    tone_map = {
        "1": "professional",
        "2": "friendly",
        "3": "formal",
        "4": "casual"
    }
    tone_style = tone_map.get(tone_choice, "professional")
    
    # Build email object
    email_input = {
        "from": from_addr,
        "to": "support@company.com",
        "subject": subject,
        "body": body,
        "history": []
    }
    
    # Process
    result = process_email(email_input, tone_style=tone_style)
    
    # Display
    print("\n" + format_output(result))


def batch_process(input_dir: str = "test_emails", output_dir: str = "output"):
    """Process multiple test emails from a directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    if not input_path.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return
    
    email_files = list(input_path.glob("*.json"))
    
    if not email_files:
        logger.warning(f"No JSON files found in {input_dir}")
        return
    
    logger.info(f"Batch processing {len(email_files)} emails...")
    
    results = []
    for email_file in email_files:
        try:
            logger.info(f"\nProcessing: {email_file.name}")
            email_data = load_test_email(str(email_file))
            
            result = process_email(email_data)
            results.append({
                "file": email_file.name,
                "result": result
            })
            
            # Save individual result
            output_file = output_path / f"result_{email_file.stem}.json"
            save_result(result, str(output_file))
            
        except Exception as e:
            logger.error(f"Failed to process {email_file.name}: {e}")
    
    # Save batch summary
    summary_file = output_path / "batch_summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "processed_count": len(results),
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)
    
    logger.info(f"Batch processing complete. Results saved to {output_dir}/")


def main():
    """Main entry point with multiple modes"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Email Assistant with LangGraph + Groq")
    parser.add_argument("--file", type=str, help="Path to email JSON file")
    parser.add_argument("--tone", type=str, choices=["professional", "friendly", "formal", "casual"],
                        default="professional", help="Reply tone style")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--batch", type=str, help="Batch process directory")
    parser.add_argument("--clear-memory", type=str, help="Clear memory for email address")
    
    args = parser.parse_args()
    
    # Clear memory mode
    if args.clear_memory:
        memory_mgr = MemoryManager()
        memory_mgr.clear_memory(args.clear_memory if args.clear_memory != "all" else None)
        print(f"✓ Memory cleared for: {args.clear_memory}")
        return
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Batch processing mode
    if args.batch:
        batch_process(args.batch)
        return
    
    # Single file processing mode
    if args.file:
        email_data = load_test_email(args.file)
    else:
        # Default example
        email_data = {
            "from": "sarah@example.com",
            "to": "support@company.com",
            "subject": "Payment not going through",
            "body": "Hi, I tried paying for my subscription twice but it keeps failing. This is really frustrating! Can you please fix this ASAP?",
            "history": []
        }
    
    # Process email
    result = process_email(email_data, tone_style=args.tone)
    
    # Display result
    print("\n" + format_output(result))
    
    # Save result
    save_result(result)


if __name__ == "__main__":
    main()
