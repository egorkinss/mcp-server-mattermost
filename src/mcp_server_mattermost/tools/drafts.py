"""Synced draft management tools."""

from typing import Annotated, Any

from fastmcp.dependencies import Depends
from fastmcp.tools import tool
from pydantic import Field

from mcp_server_mattermost.client import MattermostClient
from mcp_server_mattermost.deps import get_client
from mcp_server_mattermost.enums import Capability, ToolTag
from mcp_server_mattermost.exceptions import ValidationError
from mcp_server_mattermost.models import ChannelId, Draft, FileId, PostId, TeamId


async def _current_user_id(client: MattermostClient) -> str:
    profile = await client.get_me()
    user_id = profile.get("id")
    if not isinstance(user_id, str) or not user_id:
        message = "Mattermost current-user response has no valid id"
        raise ValidationError(message)
    return user_id


@tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
    tags={ToolTag.MATTERMOST, ToolTag.DRAFT, ToolTag.TEAM},
    meta={"capability": Capability.READ},
)
async def get_drafts(
    team_id: TeamId,
    client: MattermostClient = Depends(get_client),  # noqa: B008
) -> list[Draft]:
    """Get all synced drafts for the current user in a team."""
    user_id = await _current_user_id(client)
    data = await client.get_drafts(user_id=user_id, team_id=team_id)
    return [Draft(**item) for item in data]


@tool(
    annotations={"destructiveHint": False, "idempotentHint": True},
    tags={ToolTag.MATTERMOST, ToolTag.DRAFT, ToolTag.CHANNEL},
    meta={"capability": Capability.WRITE},
)
async def upsert_draft(  # noqa: PLR0913
    channel_id: ChannelId,
    message: Annotated[str, Field(min_length=1, description="Draft message text")],
    root_id: Annotated[PostId | None, Field(default=None, description="Thread root ID")] = None,
    file_ids: Annotated[list[FileId] | None, Field(default=None, description="Attached file IDs")] = None,
    props: Annotated[dict[str, Any] | None, Field(default=None, description="Draft properties")] = None,
    priority: Annotated[dict[str, Any] | None, Field(default=None, description="Post priority metadata")] = None,
    client: MattermostClient = Depends(get_client),  # noqa: B008
) -> Draft:
    """Create or update a synced draft without sending a message."""
    user_id = await _current_user_id(client)
    data = await client.upsert_draft(
        user_id=user_id,
        channel_id=channel_id,
        message=message,
        root_id=root_id,
        file_ids=file_ids,
        props=props,
        priority=priority,
    )
    return Draft(**data)


@tool(
    tags={ToolTag.MATTERMOST, ToolTag.DRAFT, ToolTag.CHANNEL},
    meta={"capability": Capability.DELETE},
)
async def delete_draft(
    channel_id: ChannelId,
    root_id: Annotated[PostId | None, Field(default=None, description="Thread root ID")] = None,
    client: MattermostClient = Depends(get_client),  # noqa: B008
) -> dict[str, Any]:
    """Delete the current user's channel draft or a specific thread draft."""
    user_id = await _current_user_id(client)
    return await client.delete_draft(user_id=user_id, channel_id=channel_id, root_id=root_id)
