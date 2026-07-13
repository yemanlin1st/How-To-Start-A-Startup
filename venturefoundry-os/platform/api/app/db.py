from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import asyncpg

from .config import Settings
from .security import AuthContext


class Database:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self.pool is not None:
            return
        self.pool = await asyncpg.create_pool(
            dsn=self.settings.database_url,
            min_size=self.settings.vf_db_pool_min,
            max_size=self.settings.vf_db_pool_max,
            command_timeout=self.settings.vf_request_timeout_seconds,
            server_settings={"application_name": "venturefoundry-api"},
        )

    async def disconnect(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def ping(self) -> bool:
        if self.pool is None:
            return False
        try:
            async with self.pool.acquire() as connection:
                return await connection.fetchval("SELECT 1") == 1
        except (asyncpg.PostgresError, OSError):
            return False

    @asynccontextmanager
    async def tenant_connection(
        self,
        context: AuthContext,
        request_id: str,
        *,
        readonly: bool = False,
    ) -> AsyncIterator[asyncpg.Connection]:
        if self.pool is None:
            raise RuntimeError("Database pool is not initialized")
        async with self.pool.acquire() as connection:
            async with connection.transaction(readonly=readonly):
                await connection.execute("SELECT set_config('app.current_org_id', $1, true)", str(context.org_id))
                await connection.execute("SELECT set_config('app.current_user_id', $1, true)", str(context.user_id))
                await connection.execute("SELECT set_config('app.current_roles', $1, true)", ",".join(context.roles))
                await connection.execute("SELECT set_config('app.request_id', $1, true)", request_id)
                yield connection

    async def verify_membership(self, connection: asyncpg.Connection, context: AuthContext) -> dict[str, Any]:
        row = await connection.fetchrow(
            """
            SELECT m.status::text AS status, m.roles, i.display_name, i.email
            FROM memberships m
            JOIN identities i ON i.id = m.identity_id
            WHERE m.org_id = $1 AND m.identity_id = $2
            """,
            context.org_id,
            context.user_id,
        )
        if row is None or row["status"] != "active":
            raise PermissionError("Active organization membership is required")
        return dict(row)
