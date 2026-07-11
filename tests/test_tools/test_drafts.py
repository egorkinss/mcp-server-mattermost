"""Tests for synced draft tools."""

from unittest.mock import AsyncMock

import pytest

from mcp_server_mattermost.models import Draft
from mcp_server_mattermost.tools import drafts


USER_ID = "user1234567890123456789012"
TEAM_ID = "team1234567890123456789012"
CHANNEL_ID = "chan1234567890123456789012"
ROOT_ID = "root1234567890123456789012"
FILE_ID = "file1234567890123456789012"


def make_draft_data(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "create_at": 1_700_000_000_000,
        "update_at": 1_700_000_000_001,
        "delete_at": 0,
        "user_id": USER_ID,
        "channel_id": CHANNEL_ID,
        "root_id": "",
        "message": "Draft text",
        "type": "",
        "props": {},
        "file_ids": [],
        "metadata": None,
        "priority": {},
    }
    data.update(overrides)
    return data


@pytest.mark.asyncio
async def test_get_drafts_uses_current_user_and_returns_models() -> None:
    client = AsyncMock()
    client.get_me.return_value = {"id": USER_ID}
    client.get_drafts.return_value = [make_draft_data()]
    result = await drafts.get_drafts(team_id=TEAM_ID, client=client)
    client.get_drafts.assert_awaited_once_with(user_id=USER_ID, team_id=TEAM_ID)
    assert result == [Draft(**make_draft_data())]


@pytest.mark.asyncio
async def test_upsert_draft_builds_payload_for_current_user() -> None:
    client = AsyncMock()
    client.get_me.return_value = {"id": USER_ID}
    client.upsert_draft.return_value = make_draft_data(
        message="Привет, это draft!", root_id=ROOT_ID, file_ids=[FILE_ID],
        props={"draft": True}, priority={"priority": "important"},
     )
    result = await drafts.upsert_draft(
        channel_id=CHANNEL_ID, message="Привет, это draft!", root_id=ROOT_ID,
        file_ids=[FILE_ID], props={"draft": True},
        priority={"priority": "important"}, client=client,
    )
    client.upsert_draft.assert_awaited_once_with(
        user_id=USER_ID, channel_id=CHANNEL_ID, message="Привет, это draft!",
        root_id=ROOT_ID, file_ids=[FILE_ID], props={"draft": True},
        priority={"priority": "important"},
    )
    assert result.message == "Привет, это draft!"


@pytest.mark.asyncio
async def test_delete_draft_uses_current_user_and_optional_root() -> None:
    client = AsyncMock()
    client.get_me.return_value = {"id": USER_ID}
    client.delete_draft.return_value = {"status": "OK"}
    result = await drafts.delete_draft(channel_id=CHANNEL_ID, root_id=ROOT_ID, client=client)
    client.delete_draft.assert_awaited_once_with(
        user_id=USER_ID, channel_id=CHANNEL_ID, root_id=ROOT_ID,
    )
    assert result == {"status": "OK"}
