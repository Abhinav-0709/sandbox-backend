from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings
from app.core.exceptions import UnauthorizedException

try:
    import jwt
    from jwt import PyJWKClient
    HAS_PYJWT = True
except ImportError:
    jwt = None  # type: ignore
    PyJWKClient = None  # type: ignore
    HAS_PYJWT = False

settings = get_settings()
security = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    """User payload extracted from validated Supabase JWT or guest session."""
    sub: str
    email: Optional[str] = None
    role: str = "learner"
    is_guest: bool = False


class SupabaseValidator:
    """Validates Supabase JWTs via JWKS/secret or dev mock fallback."""

    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL.rstrip("/")
        self.jwks_url = f"{self.supabase_url}/auth/v1/.well-known/jwks.json"
        self._jwks_client: Any = None

    @property
    def jwks_client(self) -> Any:
        if self._jwks_client is None and HAS_PYJWT and PyJWKClient is not None:
            self._jwks_client = PyJWKClient(self.jwks_url)
        return self._jwks_client

    def verify_token(self, token: str) -> Dict[str, Any]:
        if settings.ENABLE_DEV_AUTH and token.startswith("dev-token-"):
            user_id = token.replace("dev-token-", "")
            return {
                "sub": f"dev-{user_id}",
                "email": f"{user_id}@example.com",
                "role": "admin" if user_id == "admin" else "learner",
            }

        if not HAS_PYJWT or jwt is None:
            if settings.ENABLE_DEV_AUTH:
                return {"sub": "dev-user", "role": "learner", "email": "dev@vivoki.ai"}
            raise UnauthorizedException("PyJWT is not installed on this system.")

        try:
            unverified_header = jwt.get_unverified_header(token)
            alg = unverified_header.get("alg", "ES256")
        except Exception as e:
            raise UnauthorizedException(f"Invalid token header: {str(e)}")

        allowed_algs = ["ES256", "RS256", "HS256"]
        try:
            if alg in ["ES256", "RS256"]:
                signing_key = self.jwks_client.get_signing_key_from_jwt(token).key
            elif alg == "HS256" and settings.SUPABASE_JWT_SECRET:
                signing_key = settings.SUPABASE_JWT_SECRET
            else:
                if settings.ENABLE_DEV_AUTH:
                    return jwt.decode(token, options={"verify_signature": False})
                raise UnauthorizedException("SUPABASE_JWT_SECRET not configured.")

            payload = jwt.decode(
                token,
                signing_key,
                algorithms=allowed_algs,
                audience="authenticated",
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Authentication token expired.")
        except Exception as e:
            if settings.ENABLE_DEV_AUTH:
                try:
                    return jwt.decode(token, options={"verify_signature": False})
                except Exception:
                    pass
            raise UnauthorizedException(f"Invalid authentication token: {str(e)}")


supabase_validator = SupabaseValidator()


async def get_current_user_or_guest(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> AuthenticatedUser:
    """
    Returns the authenticated user if valid token present,
    or a transparent guest session user if unauthenticated.
    """
    if credentials and credentials.credentials:
        try:
            payload = supabase_validator.verify_token(credentials.credentials)
            app_meta = payload.get("app_metadata", {})
            user_role = app_meta.get("role") or payload.get("role", "learner")
            return AuthenticatedUser(
                sub=payload.get("sub", "anonymous-learner"),
                email=payload.get("email"),
                role="admin" if user_role == "admin" else "learner",
                is_guest=False,
            )
        except Exception:
            pass

    # Guest user fallback
    return AuthenticatedUser(
        sub="guest-demo-learner",
        email="guest@vivoki.ai",
        role="learner",
        is_guest=True,
    )
