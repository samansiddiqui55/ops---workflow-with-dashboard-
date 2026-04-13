from imap_tools import MailBox, AND, MailboxFolderSelectError
import smtplib
import ssl
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import get_settings
import logging
from typing import List, Optional, Dict
from datetime import datetime, timezone
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for email operations (IMAP/SMTP) with UID-based tracking.
    
    CRITICAL: Uses UID-based tracking ONLY. No time-based or unread filtering.
    On FIRST RUN: Records current UID and SKIPS processing to prevent bulk spam.
    
    Uses synchronous pymongo for metadata operations to avoid event loop conflicts.
    """

    # Blocked sender patterns
    BLOCKED_SENDERS = [
        "noreply@", "no-reply@", "donotreply@", "do-not-reply@",
        "mailer-daemon@", "postmaster@", "bounce@", "alerts@",
        "notifications@", "newsletter@", "marketing@", "promo@"
    ]
    
    # Blocked subject keywords
    BLOCKED_SUBJECT_KEYWORDS = [
        "unsubscribe", "newsletter", "job alert", 
        "password reset", "verify your email", "confirm your",
        "promotional", "limited time offer", "sale ends"
    ]

    def __init__(self):
        settings = get_settings()
        self.imap_server = settings.email_imap_server
        self.imap_port = settings.email_imap_port
        self.smtp_server = settings.email_smtp_server
        self.smtp_port = settings.email_smtp_port
        self.username = settings.email_username
        self.password = settings.email_password
        self.is_configured = bool(self.username and self.password)
        
        # Allowed test emails - ONLY these senders are processed
        self.allowed_test_emails = set(
            email.strip().lower() 
            for email in settings.allowed_test_emails.split(",") 
            if email.strip()
        )
        self.allowed_test_emails.add("samansiddiqui903@gmail.com")
        
        # Brand domains
        self.brand_domains = set(
            domain.strip().lower() 
            for domain in settings.brand_domains.split(",") 
            if domain.strip()
        )
        
        # Store settings for lazy DB connection
        self._mongo_url = settings.mongo_url
        self._db_name = settings.db_name
        self._db = None
        
        logger.info(f"EMAIL SERVICE INITIALIZED")
        logger.info(f"IMAP: {self.imap_server}:{self.imap_port}")
        logger.info(f"Username: {self.username}")
        logger.info(f"Configured: {self.is_configured}")
        logger.info(f"Allowed senders: {self.allowed_test_emails}")

    def _get_db(self):
        """Get synchronous MongoDB connection (lazy initialization)."""
        if self._db is None:
            client = MongoClient(self._mongo_url)
            self._db = client[self._db_name]
        return self._db

    def connect_imap(self, folder: str = "[Gmail]/All Mail") -> Optional[MailBox]:
        """Connect to IMAP server."""
        if not self.is_configured:
            logger.warning("Email not configured - missing credentials")
            return None

        try:
            mailbox = MailBox(self.imap_server, self.imap_port)
            mailbox.login(self.username, self.password, initial_folder=folder)
            logger.info(f"Connected to IMAP: {folder}")
            return mailbox
        except MailboxFolderSelectError as e:
            logger.warning(f"Folder '{folder}' not found, trying INBOX")
            try:
                mailbox = MailBox(self.imap_server, self.imap_port)
                mailbox.login(self.username, self.password, initial_folder='INBOX')
                logger.info("Connected to INBOX (fallback)")
                return mailbox
            except Exception as e2:
                logger.error(f"IMAP fallback failed: {str(e2)}")
                return None
        except Exception as e:
            logger.error(f"IMAP connection failed: {str(e)}")
            return None

    def get_last_processed_uid(self) -> Optional[int]:
        """
        Get last processed UID from MongoDB (synchronous).
        Returns None if no UID stored (first run).
        """
        try:
            db = self._get_db()
            record = db.email_meta.find_one({"key": "last_processed_uid"})
            if record and "uid" in record:
                uid = record["uid"]
                logger.info(f"Last processed UID from DB: {uid}")
                return uid
            logger.info("No last_processed_uid found in DB - FIRST RUN")
            return None
        except Exception as e:
            logger.error(f"Error getting last UID: {str(e)}")
            return None

    def set_last_processed_uid(self, uid: int):
        """Store last processed UID in MongoDB (synchronous)."""
        try:
            db = self._get_db()
            db.email_meta.update_one(
                {"key": "last_processed_uid"},
                {
                    "$set": {
                        "uid": uid,
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            logger.info(f"Saved last_processed_uid to DB: {uid}")
        except Exception as e:
            logger.error(f"Error saving last UID: {str(e)}")

    def is_email_processed(self, message_id: str) -> bool:
        """Check if email was already processed (synchronous)."""
        if not message_id:
            return False
        try:
            db = self._get_db()
            existing = db.processed_emails.find_one({"message_id": message_id})
            return existing is not None
        except Exception as e:
            logger.error(f"Error checking processed email: {str(e)}")
            return False

    def mark_email_processed(self, message_id: str, uid: int):
        """Mark email as processed to prevent reprocessing (synchronous)."""
        if not message_id:
            return
        try:
            db = self._get_db()
            db.processed_emails.update_one(
                {"message_id": message_id},
                {
                    "$set": {
                        "message_id": message_id,
                        "uid": uid,
                        "processed_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error marking email processed: {str(e)}")

    def is_valid_sender(self, from_email: str) -> bool:
        """Check if sender is allowed."""
        email_lower = from_email.lower().strip()
        
        # Check whitelist first - THIS IS THE MAIN CHECK
        if email_lower in self.allowed_test_emails:
            logger.info(f"✅ ALLOWED: {email_lower} (in whitelist)")
            return True
        
        # Check blocked patterns
        for pattern in self.BLOCKED_SENDERS:
            if pattern.lower() in email_lower:
                logger.info(f"❌ BLOCKED: {email_lower} (matches pattern: {pattern})")
                return False
        
        # Check brand domains if configured
        if self.brand_domains:
            try:
                domain = email_lower.split("@")[-1]
                if domain in self.brand_domains:
                    logger.info(f"✅ ALLOWED: {email_lower} (brand domain: {domain})")
                    return True
                logger.info(f"❌ BLOCKED: {email_lower} (domain {domain} not in brand list)")
                return False
            except:
                pass
        
        # If no brand domains configured, still block unknown senders for safety
        logger.info(f"❌ BLOCKED: {email_lower} (not in whitelist or brand domains)")
        return False

    def is_valid_subject(self, subject: str) -> bool:
        """Check if subject is valid."""
        subject_lower = subject.lower()
        for keyword in self.BLOCKED_SUBJECT_KEYWORDS:
            if keyword.lower() in subject_lower:
                logger.info(f"❌ BLOCKED subject containing: {keyword}")
                return False
        return True

    def _get_current_max_uid(self, mailbox: MailBox) -> int:
        """Get the current maximum UID in mailbox."""
        try:
            messages = list(mailbox.fetch(limit=1, reverse=True))
            if messages:
                max_uid = int(messages[0].uid) if messages[0].uid else 0
                logger.info(f"Current max UID in mailbox: {max_uid}")
                return max_uid
            return 0
        except Exception as e:
            logger.error(f"Error getting max UID: {str(e)}")
            return 0

    def fetch_new_emails(self, limit: int = 50) -> List[Dict]:
        """
        Fetch ONLY NEW emails using UID-based tracking.
        
        FIRST RUN: Records current max UID, returns EMPTY (no processing)
        NORMAL RUN: Fetches only emails with UID > last_processed_uid
        
        This is a synchronous method that returns data for async processing.
        """
        if not self.is_configured:
            logger.info("Email not configured - skipping fetch")
            return []

        mailbox = self.connect_imap("[Gmail]/All Mail")
        if not mailbox:
            return []

        try:
            last_uid = self.get_last_processed_uid()
            
            # ========================================
            # FIRST RUN SAFETY - Skip all old emails
            # ========================================
            if last_uid is None:
                logger.warning("=" * 60)
                logger.warning("🚨 FIRST RUN DETECTED - INITIALIZING UID TRACKING")
                logger.warning("=" * 60)
                
                current_max_uid = self._get_current_max_uid(mailbox)
                
                if current_max_uid > 0:
                    self.set_last_processed_uid(current_max_uid)
                    logger.warning(f"✅ Initialized last_processed_uid to {current_max_uid}")
                    logger.warning("⏭️  SKIPPING all existing emails - only NEW emails will be processed")
                else:
                    self.set_last_processed_uid(0)
                    logger.info("Empty mailbox - starting from UID 0")
                
                return []
            
            # ========================================
            # NORMAL RUN - Fetch and filter new emails
            # ========================================
            logger.info(f"🔍 Looking for emails with UID > {last_uid}")
            
            emails = []
            max_uid = last_uid
            
            # Fetch recent emails (we'll filter by UID)
            messages = list(mailbox.fetch(limit=limit, reverse=True))
            logger.info(f"📥 Fetched {len(messages)} messages from server")
            
            # Stats for logging
            stats = {
                "total": len(messages),
                "new": 0,
                "old_skipped": 0,
                "sender_blocked": 0,
                "subject_blocked": 0,
                "already_processed": 0,
                "processed": 0
            }
            
            for msg in messages:
                try:
                    msg_uid = int(msg.uid) if msg.uid else 0
                    from_email = (msg.from_ or "").strip().lower()
                    subject = msg.subject or "(no subject)"
                    message_id = msg.headers.get('message-id', [''])[0]
                    
                    # Log every email we see
                    logger.debug(f"Checking: UID={msg_uid}, From={from_email}, Subject={subject[:30]}")
                    
                    # Skip old emails (UID <= last processed)
                    if msg_uid <= last_uid:
                        stats["old_skipped"] += 1
                        continue
                    
                    stats["new"] += 1
                    logger.info(f"🆕 NEW EMAIL: UID={msg_uid} | From: {from_email} | Subject: {subject[:50]}")
                    
                    # Track max UID seen
                    max_uid = max(max_uid, msg_uid)
                    
                    # Skip if no sender
                    if not from_email:
                        logger.info(f"  ⏭️ Skipping - no sender")
                        continue
                    
                    # Check if already processed (double safety)
                    if message_id and self.is_email_processed(message_id):
                        stats["already_processed"] += 1
                        logger.info(f"  ⏭️ Skipping - already processed (message_id)")
                        continue
                    
                    # Check sender whitelist
                    if not self.is_valid_sender(from_email):
                        stats["sender_blocked"] += 1
                        continue
                    
                    # Check subject
                    if not self.is_valid_subject(subject):
                        stats["subject_blocked"] += 1
                        continue

                    # BUILD EMAIL DATA
                    email_data = {
                        "message_id": message_id,
                        "in_reply_to": msg.headers.get('in-reply-to', [''])[0],
                        "references": msg.headers.get('references', [''])[0],
                        "from_name": msg.from_,
                        "from_email": from_email,
                        "to": msg.to,
                        "cc": msg.cc,
                        "subject": subject,
                        "text": msg.text or "",
                        "html": msg.html or "",
                        "date": msg.date,
                        "uid": msg.uid
                    }

                    emails.append(email_data)
                    stats["processed"] += 1
                    
                    # Mark as processed
                    if message_id:
                        self.mark_email_processed(message_id, msg_uid)
                    
                    logger.info(f"  ✅ WILL CREATE TICKET for: {from_email} | {subject[:40]}")

                except Exception as e:
                    logger.error(f"Error processing email: {str(e)}")
                    continue

            # Update last processed UID
            if max_uid > last_uid:
                self.set_last_processed_uid(max_uid)
                logger.info(f"📝 Updated last_processed_uid: {last_uid} → {max_uid}")

            # Log summary
            logger.info("=" * 60)
            logger.info(f"📊 EMAIL FETCH SUMMARY:")
            logger.info(f"   Total fetched: {stats['total']}")
            logger.info(f"   Old (skipped): {stats['old_skipped']}")
            logger.info(f"   New emails: {stats['new']}")
            logger.info(f"   Sender blocked: {stats['sender_blocked']}")
            logger.info(f"   Subject blocked: {stats['subject_blocked']}")
            logger.info(f"   Already processed: {stats['already_processed']}")
            logger.info(f"   ✅ TO PROCESS: {stats['processed']}")
            logger.info("=" * 60)
            
            return emails

        except Exception as e:
            logger.error(f"Error in fetch_new_emails: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

        finally:
            try:
                mailbox.logout()
            except:
                pass

    # Alias for backward compatibility
    async def fetch_unread_emails(self, limit: int = 50) -> List[Dict]:
        """Async wrapper for backward compatibility."""
        return self.fetch_new_emails(limit)

    async def mark_as_read(self, uid: str) -> bool:
        """Mark email as read."""
        mailbox = self.connect_imap("[Gmail]/All Mail")
        if not mailbox:
            return False

        try:
            mailbox.flag(uid, "\\Seen", True)
            return True
        except Exception as e:
            logger.error(f"Failed to mark as read: {str(e)}")
            return False
        finally:
            try:
                mailbox.logout()
            except:
                pass

    async def send_email(
        self,
        to_address: str,
        subject: str,
        body_plain: str,
        body_html: Optional[str] = None,
        cc_addresses: Optional[List[str]] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None
    ) -> bool:
        """Send email via SMTP."""
        if not self.is_configured:
            logger.info(f"MOCK: Sending email to {to_address}")
            return True

        try:
            message = MIMEMultipart('alternative')
            message['From'] = self.username
            message['To'] = to_address
            message['Subject'] = subject

            if cc_addresses:
                message['Cc'] = ', '.join(cc_addresses)
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
            if references:
                message['References'] = references

            message.attach(MIMEText(body_plain, 'plain'))
            if body_html:
                message.attach(MIMEText(body_html, 'html'))

            recipients = [to_address]
            if cc_addresses:
                recipients.extend(cc_addresses)

            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.sendmail(self.username, recipients, message.as_string())

            logger.info(f"Email sent to {to_address}")
            return True

        except Exception as e:
            logger.error(f"Email send failed: {str(e)}")
            return False


email_service = EmailService()
