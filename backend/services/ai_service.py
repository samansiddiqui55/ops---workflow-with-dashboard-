# from emergentintegrations.llm.chat import LlmChat, UserMessage
# from config import get_settings
# import logging
# from typing import Dict, Optional

# logger = logging.getLogger(__name__)

# class AIService:
#     """Service for AI-powered features using Emergent LLM."""
    
#     def __init__(self):
#         settings = get_settings()
#         self.api_key = settings.emergent_llm_key
#         self.chat = None
    
#     def _get_chat_instance(self, session_id: str, system_message: str) -> LlmChat:
#         """Get or create LlmChat instance."""
#         chat = LlmChat(
#             api_key=self.api_key,
#             session_id=session_id,
#             system_message=system_message
#         )
#         chat.with_model("openai", "gpt-5.2")
#         return chat
    
#     async def categorize_issue(self, issue_text: str, source: str) -> Dict[str, str]:
#         """Categorize issue priority and type using AI."""
#         try:
#             system_message = """You are an expert logistics issue classifier. 
#             Analyze the issue and return ONLY a JSON object with:
#             {"priority": "High/Medium/Low", "category": "Delivery/Tracking/Damage/Other", "urgency": "Urgent/Normal"}"""
            
#             chat = self._get_chat_instance(f"categorize_{source}", system_message)
#             user_message = UserMessage(text=f"Categorize this logistics issue: {issue_text}")
            
#             response = await chat.send_message(user_message)
#             import json
#             result = json.loads(response)
#             return result
#         except Exception as e:
#             logger.error(f"AI categorization failed: {str(e)}")
#             return {"priority": "Medium", "category": "Other", "urgency": "Normal"}
    
#     async def detect_brand_from_content(self, email_text: str, sender_email: str) -> Optional[str]:
#         """Detect brand from email content when domain mapping fails."""
#         try:
#             system_message = """You are a brand detection expert. 
#             Extract the brand/company name from the email. Return ONLY the brand name, nothing else."""
            
#             chat = self._get_chat_instance("brand_detect", system_message)
#             user_message = UserMessage(
#                 text=f"Email from: {sender_email}\nContent: {email_text[:500]}\n\nWhat is the brand/company name?"
#             )
            
#             response = await chat.send_message(user_message)
#             return response.strip() if response else None
#         except Exception as e:
#             logger.error(f"AI brand detection failed: {str(e)}")
#             return None
    
#     async def generate_resolution_email(self, ticket_summary: str, resolution_comment: str) -> str:
#         """Generate professional resolution email."""
#         try:
#             system_message = """You are a professional customer service email writer. 
#             Write a polite, professional email informing the customer that their issue has been resolved.
#             Keep it concise and friendly."""
            
#             chat = self._get_chat_instance("email_gen", system_message)
#             user_message = UserMessage(
#                 text=f"Issue: {ticket_summary}\nResolution: {resolution_comment}\n\nGenerate resolution email:"
#             )
            
#             response = await chat.send_message(user_message)
#             return response
#         except Exception as e:
#             logger.error(f"AI email generation failed: {str(e)}")
#             return f"Your issue has been resolved.\n\nIssue: {ticket_summary}\n\nResolution: {resolution_comment}"
    
#     async def suggest_routing(self, issue_description: str) -> Dict[str, str]:
#         """Suggest Jira project routing based on issue content."""
#         try:
#             system_message = """You are a routing expert. Suggest the appropriate team/department.
#             Return ONLY a JSON: {"team": "Delivery/Operations/CustomerService/Tech", "reason": "brief reason"}"""
            
#             chat = self._get_chat_instance("routing", system_message)
#             user_message = UserMessage(text=f"Route this issue: {issue_description}")
            
#             response = await chat.send_message(user_message)
#             import json
#             return json.loads(response)
#         except Exception as e:
#             logger.error(f"AI routing failed: {str(e)}")
#             return {"team": "Operations", "reason": "Default routing"}

# ai_service = AIService()
class MockAIService:
    async def categorize_issue(self, text: str, source: str = "email"):
        text = text.lower()
        if "delay" in text or "delayed" in text:
            return {"category": "Delay Issue", "priority": "High"}
        elif "tracking" in text or "awb" in text or "shipment" in text:
            return {"category": "Tracking Issue", "priority": "Medium"}
        elif "error" in text or "failed" in text:
            return {"category": "System Error", "priority": "High"}
        else:
            return {"category": "General Issue", "priority": "Low"}

    async def generate_resolution_email(self, ticket_summary: str, resolution_comment: str):
        return f"Your issue has been resolved.\n\nIssue: {ticket_summary}\n\nResolution: {resolution_comment}"

    async def detect_brand_from_content(self, email_text: str, sender_email: str):
        return None

    async def suggest_routing(self, issue_description: str):
        return {"team": "Operations", "reason": "Default routing"}

ai_service = MockAIService()