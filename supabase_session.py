import asyncio, os
from typing import List, Optional
from supabase import create_client, Client
from agents.memory import Session
from agents import TResponseInputItem
from utils.config import SUPABASE_URL, SUPABASE_KEY


class SupabaseSession(Session):
    """Supabase (PostgreSQL-based) implementation of session storage.

    Stores conversation history in Supabase.
    """

    def __init__(
        self,
        session_id: str,
        sessions_table: str = "agent_sessions",
        messages_table: str = "agent_messages",
    ):
        """Initialize the Supabase session.

        Args:
            session_id: Unique identifier for the conversation session.
            sessions_table: Table for session metadata (default: 'agent_sessions').
            messages_table: Table for message data (default: 'agent_messages').
        """
        self.session_id = session_id
        self.sessions_table = sessions_table
        self.messages_table = messages_table
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self._initialized = False  # Flag to track initialization

    async def _ensure_session_exists(self) -> None:
        """Ensure the session row exists."""
        if self._initialized:
            return

        def sync_ensure():
            self.supabase.table(self.sessions_table).upsert(
                {"session_id": self.session_id}
            ).execute()

        await asyncio.to_thread(sync_ensure)
        self._initialized = True

    async def get_items(self, limit: Optional[int] = None) -> List[TResponseInputItem]:
        """Retrieve the conversation history for this session."""
        await self._ensure_session_exists()

        def sync_get():
            try:
                query = (
                    self.supabase.table(self.messages_table)
                    .select("message_data")
                    .eq("session_id", self.session_id)
                    .order("created_at", desc=True)
                    .order("id", desc=True)
                )
                if limit:
                    query = query.limit(limit)
                response = query.execute()
                items = [item["message_data"] for item in response.data]
                # print("Retrieved items:", list(reversed(items)))
                return list(reversed(items))  # Chronological order
            except Exception as e:
                print(f"[Supabase Error] Failed to get items: {e}")
                return []

        return await asyncio.to_thread(sync_get)

    async def add_items(self, items: List[TResponseInputItem]) -> None:
        """Add new items to the conversation history."""
        if not items:
            return
        await self._ensure_session_exists()  # Ensure initialized

        def sync_add():
            try:
                data = [
                    {"session_id": self.session_id, "message_data": item}
                    for item in items
                ]
                self.supabase.table(self.messages_table).insert(data).execute()
                self.supabase.table(self.sessions_table).update(
                    {"updated_at": "now()"}
                ).eq("session_id", self.session_id).execute()
            except Exception as e:
                print(f"[Supabase Error] Failed to add items: {e}")
                return []

        await asyncio.to_thread(sync_add)

    async def pop_item(self) -> Optional[TResponseInputItem]:
        """Remove and return the most recent item from the session."""
        await self._ensure_session_exists()  # Ensure initialized

        def sync_pop():
            try:
                latest = (
                    self.supabase.table(self.messages_table)
                    .select("id, message_data")
                    .eq("session_id", self.session_id)
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute()
                )
                if not latest.data:
                    return None
                item = latest.data[0]["message_data"]
                self.supabase.table(self.messages_table).delete().eq(
                    "id", latest.data[0]["id"]
                ).execute()
                return item
            except Exception as e:
                print(f"[Supabase Error] Failed to pop item: {e}")
                return []

        return await asyncio.to_thread(sync_pop)

    async def clear_session(self) -> None:
        """Clear all items for this session."""
        await self._ensure_session_exists()  # Ensure initialized

        def sync_clear():
            try:
                self.supabase.table(self.messages_table).delete().eq(
                    "session_id", self.session_id
                ).execute()
                self.supabase.table(self.sessions_table).delete().eq(
                    "session_id", self.session_id
                ).execute()
            except Exception as e:
                print(f"[Supabase Error] Failed to clear session: {e}")
                return []

        await asyncio.to_thread(sync_clear)
