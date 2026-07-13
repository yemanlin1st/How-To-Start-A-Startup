from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import Settings, get_settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class AuthContext:
    user_id: UUID
    org_id: UUID
    roles: tuple[str, ...]
    subject: str
    development_auth: bool = False

    def has_any_role(self, *required: str) -> bool:
        return bool(set(required).intersection(self.roles))


async def get_auth_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    x_vf_user_id: str | None = Header(default=None),
    x_vf_organization_id: str | None = Header(default=None),
    x_vf_roles: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> AuthContext:
    if credentials:
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.vf_jwt_secret,
                algorithms=[settings.vf_jwt_algorithm],
                audience=settings.vf_jwt_audience,
                issuer=settings.vf_jwt_issuer,
                options={"require": ["exp", "iat", "sub", "org_id", "roles"]},
            )
            roles = payload.get("roles")
            if not isinstance(roles, list) or not all(isinstance(role, str) for role in roles):
                raise ValueError("roles claim must be an array of strings")
            return AuthContext(
                user_id=UUID(str(payload["sub"])),
                org_id=UUID(str(payload["org_id"])),
                roles=tuple(sorted(set(roles))),
                subject=str(payload["sub"]),
            )
        except (jwt.PyJWTError, ValueError, KeyError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    if settings.vf_dev_auth_enabled:
        try:
            roles = tuple(
                role.strip()
                for role in (x_vf_roles.split(",") if x_vf_roles else settings.vf_dev_default_roles)
                if role.strip()
            )
            return AuthContext(
                user_id=UUID(x_vf_user_id or settings.vf_dev_default_user_id),
                org_id=UUID(x_vf_organization_id or settings.vf_dev_default_org_id),
                roles=roles or ("viewer",),
                subject=f"development:{x_vf_user_id or settings.vf_dev_default_user_id}",
                development_auth=True,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid development identity headers") from exc

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Bearer authentication is required",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_roles(*required_roles: str):
    async def dependency(context: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if not context.has_any_role(*required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"message": "Insufficient role", "required_any": list(required_roles)},
            )
        return context

    return dependency
