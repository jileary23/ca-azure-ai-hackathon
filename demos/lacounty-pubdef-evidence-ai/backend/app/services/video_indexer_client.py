"""Azure Video Indexer client.

Wraps the Azure Video Indexer REST API.
Reference: https://learn.microsoft.com/en-us/azure/azure-video-indexer/video-indexer-use-apis

Authentication uses DefaultAzureCredential (Managed Identity in production,
VS Code / CLI login in development). No API keys stored in code.
"""

from __future__ import annotations

import logging

import httpx
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

_AVI_BASE = "https://api.videoindexer.ai"
_ARM_SCOPE = "https://management.azure.com/.default"
_AVI_SCOPE = "https://www.videoindexer.ai/.default"


class VideoIndexerClient:
    """Thin async client for the Azure Video Indexer REST API."""

    def __init__(
        self,
        account_id: str,
        location: str,
        subscription_id: str,
        resource_group: str,
        account_name: str,
    ) -> None:
        self.account_id = account_id
        self.location = location
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.account_name = account_name
        self._credential = DefaultAzureCredential()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _arm_token(self) -> str:
        """Acquire an ARM token used to request a Video Indexer access token."""
        token = self._credential.get_token(_ARM_SCOPE)
        return token.token

    async def _avi_access_token(
        self, http: httpx.AsyncClient, scope: str = "Account"
    ) -> str:
        """Exchange ARM token for a Video Indexer account/video access token.

        scope: "Account" | "Video"
        """
        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self.account_name}"
            f"/generateAccessToken"
            "?api-version=2024-01-01"
        )
        arm_token = self._arm_token()
        payload = {"permissionType": "Contributor", "scope": scope}
        resp = await http.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {arm_token}"},
        )
        resp.raise_for_status()
        return resp.json()["accessToken"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def upload_video_url(
        self,
        video_url: str,
        name: str,
        description: str = "",
        language: str = "en-US",
    ) -> str:
        """Upload a video by URL and return the Video Indexer video_id."""
        async with httpx.AsyncClient(timeout=60) as http:
            access_token = await self._avi_access_token(http)
            url = f"{_AVI_BASE}/{self.location}/Accounts/{self.account_id}/Videos"
            params = {
                "name": name,
                "description": description,
                "videoUrl": video_url,
                "language": language,
                "indexingPreset": "Default",
                "accessToken": access_token,
            }
            resp = await http.post(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            video_id: str = data["id"]
            logger.info("Video Indexer job submitted: video_id=%s", video_id)
            return video_id

    async def get_video_index(self, video_id: str) -> dict:
        """Return the full video index JSON from Video Indexer."""
        async with httpx.AsyncClient(timeout=60) as http:
            access_token = await self._avi_access_token(http)
            url = (
                f"{_AVI_BASE}/{self.location}/Accounts/{self.account_id}"
                f"/Videos/{video_id}/Index"
            )
            resp = await http.get(url, params={"accessToken": access_token})
            resp.raise_for_status()
            return resp.json()

    async def get_transcript(self, video_id: str) -> list[dict]:
        """Return the raw transcript blocks from Video Indexer."""
        index = await self.get_video_index(video_id)
        videos = index.get("videos", [])
        if not videos:
            return []
        insights = videos[0].get("insights", {})
        return insights.get("transcript", [])

    async def get_processing_state(self, video_id: str) -> str:
        """Return processing state: 'Processing' | 'Processed' | 'Failed'."""
        index = await self.get_video_index(video_id)
        videos = index.get("videos", [])
        if not videos:
            return "Processing"
        return videos[0].get("state", "Processing")
