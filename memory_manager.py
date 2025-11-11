# """
# Persistent memory management for conversation history
# """
# import json
# from pathlib import Path
# from typing import Dict, List
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# class MemoryManager:
#     """Manages persistent conversation history"""
    
#     def __init__(self, memory_file: str = "data/memory.json"):
#         self.memory_file = Path(memory_file)
#         self.memory_file.parent.mkdir(parents=True, exist_ok=True)
#         self._initialize_memory()
    
#     def _initialize_memory(self):
#         """Create memory file if it doesn't exist"""
#         if not self.memory_file.exists():
#             self.memory_file.write_text(json.dumps({}, indent=2))
#             logger.info(f"Initialized memory file: {self.memory_file}")
    
#     def load_memory(self, email_address: str) -> List[Dict]:
#         """
#         Load conversation history for a specific email address
        
#         Args:
#             email_address: Email address to lookup
            
#         Returns:
#             List of previous interactions
#         """
#         try:
#             data = json.loads(self.memory_file.read_text())
#             history = data.get(email_address, [])
#             logger.info(f"Loaded {len(history)} messages for {email_address}")
#             return history
#         except Exception as e:
#             logger.error(f"Error loading memory: {e}")
#             return []
    
#     def save_interaction(
#         self, 
#         email_from: str, 
#         email_to: str,
#         subject: str,
#         body: str,
#         intent: str,
#         reply_body: str,
#         escalated: bool
#     ):
#         """
#         Save a new interaction to memory
        
#         Args:
#             email_from: Sender's email
#             email_to: Recipient's email
#             subject: Email subject
#             body: Email body
#             intent: Detected intent
#             reply_body: Generated reply
#             escalated: Whether issue was escalated
#         """
#         try:
#             data = json.loads(self.memory_file.read_text())
            
#             # Create interaction record
#             interaction = {
#                 "timestamp": datetime.now().isoformat(),
#                 "from": email_from,
#                 "to": email_to,
#                 "subject": subject,
#                 "body": body,
#                 "intent": intent,
#                 "reply": reply_body,
#                 "escalated": escalated
#             }
            
#             # Add to user's history
#             if email_from not in data:
#                 data[email_from] = []
            
#             data[email_from].append(interaction)
            
#             # Keep only recent history (prevent unlimited growth)
#             from config import MAX_HISTORY_LENGTH
#             if len(data[email_from]) > MAX_HISTORY_LENGTH:
#                 data[email_from] = data[email_from][-MAX_HISTORY_LENGTH:]
            
#             # Save to file
#             self.memory_file.write_text(json.dumps(data, indent=2))
#             logger.info(f"Saved interaction for {email_from}")
            
#         except Exception as e:
#             logger.error(f"Error saving memory: {e}")
    
#     def get_interaction_count(self, email_address: str) -> int:
#         """Get total number of interactions for an email"""
#         history = self.load_memory(email_address)
#         return len(history)
    
#     def clear_memory(self, email_address: str = None):
#         """
#         Clear memory for specific user or all users
        
#         Args:
#             email_address: Optional specific email to clear
#         """
#         try:
#             if email_address:
#                 data = json.loads(self.memory_file.read_text())
#                 if email_address in data:
#                     del data[email_address]
#                     self.memory_file.write_text(json.dumps(data, indent=2))
#                     logger.info(f"Cleared memory for {email_address}")
#             else:
#                 self.memory_file.write_text(json.dumps({}, indent=2))
#                 logger.info("Cleared all memory")
#         except Exception as e:
#             logger.error(f"Error clearing memory: {e}")



"""
Persistent memory management for conversation history
"""
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages persistent conversation history"""
    
    def __init__(self, memory_file: str = "data/memory.json"):
        self.memory_file = Path(memory_file)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Create memory file if it doesn't exist"""
        if not self.memory_file.exists():
            self.memory_file.write_text(json.dumps({}, indent=2))
            logger.info(f"Initialized memory file: {self.memory_file}")
        else:
            # Validate existing file is not empty/corrupted
            try:
                content = self.memory_file.read_text().strip()
                if not content:
                    # File is empty, initialize it
                    self.memory_file.write_text(json.dumps({}, indent=2))
                    logger.info(f"Reinitialized empty memory file: {self.memory_file}")
                else:
                    # Try to parse to ensure valid JSON
                    json.loads(content)
            except json.JSONDecodeError as e:
                # File is corrupted, reinitialize
                logger.warning(f"Memory file corrupted, reinitializing: {e}")
                self.memory_file.write_text(json.dumps({}, indent=2))
    
    def load_memory(self, email_address: str) -> List[Dict]:
        """
        Load conversation history for a specific email address
        
        Args:
            email_address: Email address to lookup
            
        Returns:
            List of previous interactions
        """
        try:
            content = self.memory_file.read_text().strip()
            
            # Handle empty file
            if not content:
                logger.info(f"Memory file is empty, returning empty history for {email_address}")
                return []
            
            data = json.loads(content)
            history = data.get(email_address, [])
            logger.info(f"Loaded {len(history)} messages for {email_address}")
            return history
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing memory file (invalid JSON): {e}")
            # Reinitialize corrupted file
            self._initialize_memory()
            return []
        except Exception as e:
            logger.error(f"Unexpected error loading memory: {e}")
            return []
    
    def save_interaction(
        self, 
        email_from: str, 
        email_to: str,
        subject: str,
        body: str,
        intent: str,
        reply_body: str,
        escalated: bool
    ):
        """
        Save a new interaction to memory
        
        Args:
            email_from: Sender's email
            email_to: Recipient's email
            subject: Email subject
            body: Email body
            intent: Detected intent
            reply_body: Generated reply
            escalated: Whether issue was escalated
        """
        try:
            content = self.memory_file.read_text().strip()
            
            # Handle empty file
            if not content:
                data = {}
            else:
                data = json.loads(content)
            
            # Create interaction record
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "from": email_from,
                "to": email_to,
                "subject": subject,
                "body": body,
                "intent": intent,
                "reply": reply_body,
                "escalated": escalated
            }
            
            # Add to user's history
            if email_from not in data:
                data[email_from] = []
            
            data[email_from].append(interaction)
            
            # Keep only recent history (prevent unlimited growth)
            from config import MAX_HISTORY_LENGTH
            if len(data[email_from]) > MAX_HISTORY_LENGTH:
                data[email_from] = data[email_from][-MAX_HISTORY_LENGTH:]
            
            # Save to file
            self.memory_file.write_text(json.dumps(data, indent=2))
            logger.info(f"Saved interaction for {email_from}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing memory file when saving (reinitializing): {e}")
            # Start fresh with just this interaction
            data = {email_from: [{
                "timestamp": datetime.now().isoformat(),
                "from": email_from,
                "to": email_to,
                "subject": subject,
                "body": body,
                "intent": intent,
                "reply": reply_body,
                "escalated": escalated
            }]}
            self.memory_file.write_text(json.dumps(data, indent=2))
            logger.info(f"Reinitialized memory and saved interaction for {email_from}")
            
        except Exception as e:
            logger.error(f"Unexpected error saving memory: {e}")
    
    def get_interaction_count(self, email_address: str) -> int:
        """Get total number of interactions for an email"""
        history = self.load_memory(email_address)
        return len(history)
    
    def clear_memory(self, email_address: str = None):
        """
        Clear memory for specific user or all users
        
        Args:
            email_address: Optional specific email to clear
        """
        try:
            content = self.memory_file.read_text().strip()
            
            if not content:
                data = {}
            else:
                data = json.loads(content)
            
            if email_address:
                if email_address in data:
                    del data[email_address]
                    self.memory_file.write_text(json.dumps(data, indent=2))
                    logger.info(f"Cleared memory for {email_address}")
            else:
                self.memory_file.write_text(json.dumps({}, indent=2))
                logger.info("Cleared all memory")
                
        except json.JSONDecodeError as e:
            logger.error(f"Error clearing memory (reinitializing): {e}")
            self._initialize_memory()
        except Exception as e:
            logger.error(f"Unexpected error clearing memory: {e}")
