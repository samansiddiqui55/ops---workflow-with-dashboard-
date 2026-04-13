import asyncio
import threading
from datetime import datetime, timezone
import logging
import re

from services.email_service import email_service
from services.mapping_service import mapping_service
from services.ticket_service import ticket_service
from models.ticket import TicketCreate

logger = logging.getLogger(__name__)


class EmailPollerJob:
    """Background job to poll emails and create Jira + dashboard tickets."""

    def __init__(self):
        self._is_processing = False
        self._stop_event = threading.Event()
        self._thread = None
        self._loop = None

    async def process_emails(self):
        """Poll and process incoming emails with UID tracking."""
        if self._is_processing:
            logger.info("Email processing already in progress, skipping...")
            return
            
        self._is_processing = True
        
        try:
            logger.info("Starting email processing cycle")

            # Fetch emails (synchronous call, returns list)
            emails = email_service.fetch_new_emails(limit=50)
            logger.info(f"Fetched {len(emails)} filtered emails to process")

            processed = 0

            for email_data in emails:
                try:
                    await self.process_single_email(email_data)
                    processed += 1
                except Exception as e:
                    logger.error(f"Error processing email: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())

            logger.info(f"Email processing completed: {processed} emails processed")

        except Exception as e:
            logger.error(f"Email polling error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            self._is_processing = False

    async def process_single_email(self, email_data: dict):
        """Process a single email and create ticket if not duplicate."""
        message_id = (email_data.get("message_id") or "").strip()
        from_email = (email_data.get("from_email") or "").strip().lower()
        from_name = email_data.get("from_name")
        subject = (email_data.get("subject") or "No Subject").strip()
        body = (email_data.get("text") or "").strip()
        cc_emails = email_data.get("cc", [])

        if not from_email or not subject:
            logger.info("Skipping invalid email with missing sender/subject")
            return

        logger.info(f"Processing email from {from_email} | Subject: {subject}")

        # 1. Check if already processed by message_id
        if message_id:
            existing_mapping = await mapping_service.get_email_mapping_by_thread(message_id)
            if existing_mapping:
                logger.info(f"Email already processed for message_id: {message_id}")
                return

        # 2. Derive brand from sender domain
        brand = self.extract_brand_from_email(from_email)

        # 3. CRITICAL FIX: full_message should ONLY contain the clean email body
        # Remove all headers - just store the body text
        full_message = self.extract_clean_body(body)
        
        # If body is empty, try HTML
        if not full_message.strip():
            html_content = email_data.get("html", "")
            if html_content:
                full_message = self.html_to_text(html_content)

        # 4. Extract AWB from subject and body
        awb = self.extract_awb(subject + " " + body)

        # 5. Create dashboard + Jira ticket
        ticket_payload = TicketCreate(
            brand=brand,
            sender_email=from_email,
            summary=subject,
            full_message=full_message,
            source="email",
            awb=awb
        )

        created_ticket = await ticket_service.create_ticket(ticket_payload)
        
        # Mark email as read
        if email_data.get("uid"):
            await email_service.mark_as_read(email_data["uid"])

        # 6. Save mapping
        if message_id and created_ticket:
            mapping_data = {
                "email_thread_id": message_id,
                "message_id": message_id,
                "jira_ticket_id": created_ticket.get("jira_issue_id"),
                "jira_ticket_key": created_ticket.get("jira_issue_key"),
                "brand": brand,
                "sender_email": from_email,
                "sender_name": from_name,
                "original_subject": subject,
                "cc_emails": cc_emails,
                "status": "open",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }

            await mapping_service.create_email_mapping(mapping_data)

        logger.info(
            f"Email processed successfully | Dashboard Ticket: {created_ticket.get('id')} | Jira: {created_ticket.get('jira_issue_key')}"
        )

    def extract_clean_body(self, text: str) -> str:
        """
        Extract clean email body, removing headers and metadata.
        CRITICAL: full_message should ONLY contain the actual message content.
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        body_lines = []
        in_header = True
        
        for line in lines:
            # Skip header-like lines at the start
            if in_header:
                # Common header patterns to skip
                if line.lower().startswith(('from:', 'to:', 'cc:', 'bcc:', 
                                           'subject:', 'date:', 'sent:', 
                                           'reply-to:', 'x-', 'content-type:',
                                           'mime-version:', 'message-id:')):
                    continue
                # Empty line often separates headers from body
                if line.strip() == '':
                    in_header = False
                    continue
                # If we hit a non-header line, we're in the body
                in_header = False
            
            body_lines.append(line)
        
        # Clean up the result
        result = '\n'.join(body_lines).strip()
        
        # Remove common email signatures and footers
        result = re.sub(r'--\s*\nSent from.*$', '', result, flags=re.MULTILINE | re.IGNORECASE)
        result = re.sub(r'\n*Get Outlook for.*$', '', result, flags=re.MULTILINE | re.IGNORECASE)
        
        return result.strip()

    def html_to_text(self, html: str) -> str:
        """Convert HTML to plain text."""
        import re
        # Remove script and style elements
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Remove all HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Decode common HTML entities
        text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_brand_from_email(self, sender_email: str) -> str:
        """Extract brand/company name from sender email domain."""
        try:
            domain = sender_email.split("@")[-1].lower()

            ignored = {
                "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
                "icloud.com", "proton.me", "protonmail.com"
            }

            if domain in ignored:
                return "Unknown Brand"

            brand = domain.split(".")[0]
            return brand.replace("-", " ").replace("_", " ").title()
        except Exception:
            return "Unknown Brand"

    def extract_awb(self, text: str):
        """
        Extract AWB/tracking-like ID from email subject/body.
        Supports both numeric and alphanumeric tracking IDs.
        """
        patterns = [
            # AWB patterns
            r"\bAWB[:\s\-#]*([A-Za-z0-9]{6,30})\b",
            r"\bawb[:\s\-#]*([A-Za-z0-9]{6,30})\b",
            # Tracking patterns
            r"\bTracking[:\s\-#]*([A-Za-z0-9]{6,30})\b",
            r"\btracking[:\s\-#]*([A-Za-z0-9]{6,30})\b",
            # Shipment ID patterns
            r"\bShipment[:\s\-#]*([A-Za-z0-9]{6,30})\b",
            r"\bshipment[:\s\-#]*([A-Za-z0-9]{6,30})\b",
            # Order ID patterns
            r"\bOrder[:\s\-#]*([A-Za-z0-9]{6,30})\b",
            r"\border[:\s\-#]*([A-Za-z0-9]{6,30})\b",
            # Generic tracking number (10+ digits)
            r"\b(\d{10,20})\b",
            # Alphanumeric tracking (common formats)
            r"\b([A-Z]{2}\d{9}[A-Z]{2})\b",  # International format
            r"\b([A-Z]{3}\d{8,12})\b",  # Courier format
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    async def import_historical_emails(self):
        """
        Import ALL historical emails into dashboard.
        Does NOT create Jira tickets - only stores for dashboard visibility.
        """
        logger.info("=" * 60)
        logger.info("STARTING HISTORICAL EMAIL IMPORT")
        logger.info("=" * 60)

        try:
            # Fetch ALL emails from mailbox
            emails = email_service.fetch_all_emails(limit=500)
            logger.info(f"Found {len(emails)} historical emails to import")

            imported = 0
            skipped = 0

            for email_data in emails:
                try:
                    from_email = (email_data.get("from_email") or "").strip().lower()
                    subject = (email_data.get("subject") or "No Subject").strip()
                    body = (email_data.get("text") or "").strip()

                    if not from_email or not subject:
                        skipped += 1
                        continue

                    brand = self.extract_brand_from_email(from_email)
                    full_message = self.extract_clean_body(body)
                    
                    if not full_message.strip():
                        html_content = email_data.get("html", "")
                        if html_content:
                            full_message = self.html_to_text(html_content)

                    awb = self.extract_awb(subject + " " + (body or ""))
                    
                    # Parse email date for historical accuracy
                    email_date = email_data.get("date")
                    if email_date and not hasattr(email_date, 'tzinfo'):
                        email_date = None

                    ticket_payload = TicketCreate(
                        brand=brand,
                        sender_email=from_email,
                        summary=subject,
                        full_message=full_message or f"Email from {from_email}: {subject}",
                        source="email",
                        awb=awb
                    )

                    # Create display-only ticket (NO JIRA)
                    result = await ticket_service.create_display_ticket(
                        ticket_payload,
                        email_date=email_date
                    )

                    if result:
                        imported += 1
                    else:
                        skipped += 1

                except Exception as e:
                    logger.error(f"Error importing email: {str(e)}")
                    skipped += 1

            logger.info("=" * 60)
            logger.info(f"HISTORICAL IMPORT COMPLETE: {imported} imported, {skipped} skipped")
            logger.info("=" * 60)

            return {
                "status": "success",
                "total_fetched": len(emails),
                "imported": imported,
                "skipped": skipped
            }

        except Exception as e:
            logger.error(f"Historical import error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    def _run_async_loop(self):
        """Run the async event loop in a separate thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        async def poll_loop():
            while not self._stop_event.is_set():
                try:
                    await self.process_emails()
                except Exception as e:
                    logger.error(f"Error in email poll loop: {e}")
                
                # Wait 60 seconds before next poll, checking for stop every second
                for _ in range(60):
                    if self._stop_event.is_set():
                        break
                    await asyncio.sleep(1)
        
        try:
            self._loop.run_until_complete(poll_loop())
        except Exception as e:
            logger.error(f"Event loop error: {e}")
        finally:
            self._loop.close()

    def start(self):
        """Start the email polling in a background thread with its own event loop."""
        logger.info("Starting email poller job (runs every 1 minute)")
        
        if self._thread and self._thread.is_alive():
            logger.info("Email poller already running")
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self._thread.start()
        logger.info("Email polling thread started successfully")

    def stop(self):
        """Stop the email poller."""
        logger.info("Stopping email poller...")
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Email poller stopped")


email_poller = EmailPollerJob()
