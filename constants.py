CANDIDATE_FIELD_NAMES = ["name", "email", "skills", "certificates", "education", "experiences"]
GMAIL_API = {
    "base_gmail_url": "https://www.googleapis.com/gmail/v1/users/{email}/messages",
    "base_messages_url": "https://www.googleapis.com/gmail/v1/users/{email}/messages/{message_id}",
    "base_attachments_url": "https://gmail.googleapis.com/gmail/v1/users/{email}/messages/{message_id}/attachments/{attachment_id}"
}