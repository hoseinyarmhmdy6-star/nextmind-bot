import requests
from config import META_GRAPH_API_URL, META_PAGE_ACCESS_TOKEN, META_INSTAGRAM_ACCOUNT_ID

class MetaGraphAPI:
    def __init__(self):
        self.base_url = META_GRAPH_API_URL
        self.access_token = META_PAGE_ACCESS_TOKEN
        self.account_id = META_INSTAGRAM_ACCOUNT_ID

    def is_configured(self) -> bool:
        return bool(self.access_token and self.access_token != "your_meta_page_access_token_here")

    def reply_to_comment(self, comment_id: str, message_text: str) -> bool:
        """Replies publicly to a comment on Instagram post"""
        if not self.is_configured():
            print(f"[Simulation] Replying to comment {comment_id}: {message_text}")
            return True
        
        url = f"{self.base_url}/{comment_id}/replies"
        params = {"access_token": self.access_token}
        payload = {"message": message_text}
        
        try:
            res = requests.post(url, params=params, json=payload, timeout=10)
            res_json = res.json()
            if "id" in res_json:
                print(f"[Meta API] Comment reply sent successfully. ID: {res_json['id']}")
                return True
            else:
                print(f"[Meta API Error] Reply comment failed: {res_json}")
                return False
        except Exception as e:
            print(f"[Meta API Exception] reply_to_comment: {e}")
            return False

    def send_dm(self, recipient_id: str, message_text: str) -> bool:
        """Sends a direct message to a user via Instagram Messaging API"""
        if not self.is_configured():
            print(f"[Simulation] Sending DM to {recipient_id}: {message_text}")
            return True
        
        url = f"{self.base_url}/me/messages"
        params = {"access_token": self.access_token}
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }
        
        try:
            res = requests.post(url, params=params, json=payload, timeout=10)
            res_json = res.json()
            if "message_id" in res_json or "recipient_id" in res_json:
                print(f"[Meta API] DM sent successfully to {recipient_id}")
                return True
            else:
                print(f"[Meta API Error] Send DM failed: {res_json}")
                return False
        except Exception as e:
            print(f"[Meta API Exception] send_dm: {e}")
            return False

    def send_button_dm(self, recipient_id: str, text: str, buttons: list) -> bool:
        """Sends a rich template DM with quick buttons (e.g. 'فالو کردم', 'مشاهده سایت')"""
        if not self.is_configured():
            print(f"[Simulation] Sending Button DM to {recipient_id}: {text}")
            return True
            
        url = f"{self.base_url}/me/messages"
        params = {"access_token": self.access_token}
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": text,
                        "buttons": buttons
                    }
                }
            }
        }
        try:
            res = requests.post(url, params=params, json=payload, timeout=10)
            return "message_id" in res.json()
        except Exception as e:
            print(f"[Meta API Exception] send_button_dm: {e}")
            return False

meta_api = MetaGraphAPI()
