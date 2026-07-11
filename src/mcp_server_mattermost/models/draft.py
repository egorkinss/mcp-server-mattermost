"""Synced draft response model."""

from typing import Any

from pydantic import Field

from .base import MattermostResponse
from .common import ChannelId, FileId, PostId, UserId


class Draft(MattermostResponse):
    """Mattermost synced draft."""

    create_at: int = Field(description="Creation timestamp in milliseconds")
    update_at: int = Field(description="Last update timestamp in milliseconds")
    delete_at: int = Field(default=0, description="Deprecated deletion timestamp")
    user_id: UserId
    channel_id: ChannelId
    root_id: PostId | str = Field(default="", description="Thread root ID, empty for channel draft")
    message: str
    type: str = ""
    props: dict[str, Any] = Field(default_factory=dict)
    file_ids: list[FileId] = Field(default_factory=list)
    metadata: dict[str, Any] | None = None
    priority: dict[str, Any] = Field(default_factory=dict)
