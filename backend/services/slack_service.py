from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import List, Dict, Any


class SlackService:
    def __init__(self, access_token: str):
        """Initialize Slack service with OAuth token"""
        self.client = WebClient(token=access_token)
    
    async def post_message(self, channel: str, text: str = None, 
                          blocks: List[Dict] = None, thread_ts: str = None) -> bool:
        """Post a message to Slack channel"""
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks,
                thread_ts=thread_ts
            )
            return response['ok']
        except SlackApiError as e:
            print(f"Error posting to Slack: {e}")
            return False
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get Slack user information"""
        try:
            response = self.client.users_info(user=user_id)
            if response['ok']:
                return response['user']
            return {}
        except SlackApiError as e:
            print(f"Error getting user info: {e}")
            return {}
    
    async def get_user_email(self, user_id: str) -> str:
        """Get email address of Slack user"""
        user_info = await self.get_user_info(user_id)
        return user_info.get('profile', {}).get('email', '')
