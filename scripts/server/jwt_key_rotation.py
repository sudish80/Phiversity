"""
JWT key rotation policy and management.
Implements key rotation to limit exposure if a key is compromised.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import json


class JWTKeyRotationPolicy:
    """
    Manages JWT signing key rotation.
    
    Strategy:
    - Maintain multiple keys (current + historical)
    - New tokens signed with current key
    - Verification accepts any valid key (current or historical)
    - Old keys automatically retired after retention period
    """

    def __init__(
        self,
        rotation_interval_days: int = 90,
        retention_days: int = 180,
        max_keys: int = 3,
    ):
        """
        Initialize key rotation policy.

        Args:
            rotation_interval_days: How often to rotate the signing key
            retention_days: How long to keep old keys for verification
            max_keys: Maximum number of keys to maintain
        """
        self.rotation_interval_days = rotation_interval_days
        self.retention_days = retention_days
        self.max_keys = max_keys

    def should_rotate_key(self, key_created_at: datetime) -> bool:
        """
        Check if current key should be rotated.

        Args:
            key_created_at: When current key was created

        Returns:
            True if key should be rotated
        """
        now = datetime.now(timezone.utc)
        age = (now - key_created_at).days
        return age >= self.rotation_interval_days

    def is_key_valid_for_verification(
        self,
        key_created_at: datetime,
    ) -> bool:
        """
        Check if key can still be used for token verification.

        Args:
            key_created_at: When key was created

        Returns:
            True if key is still within retention window
        """
        now = datetime.now(timezone.utc)
        age = (now - key_created_at).days
        return age < self.retention_days


class JWTKeyRing:
    """
    Manages a ring of JWT keys for rotation.
    Keys stored as: {'kid': 'key_id', 'secret': 'key_secret', 'created_at': timestamp, 'retired_at': timestamp}
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize keyring.

        Args:
            storage_path: Path to store keys (default: .env-based setting)
        """
        self.storage_path = storage_path or os.getenv(
            "JWT_KEYRING_PATH", ".jwt_keyring.json"
        )
        self._keys: List[Dict[str, Any]] = []
        self._load_keys()

    def _load_keys(self) -> None:
        """Load keys from storage."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self._keys = data.get("keys", [])
            except Exception:
                self._keys = []

    def _save_keys(self) -> None:
        """Persist keys to storage."""
        try:
            os.makedirs(os.path.dirname(self.storage_path) or ".", exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump({"keys": self._keys}, f)
            # Restrict file permissions to owner only
            os.chmod(self.storage_path, 0o600)
        except Exception as e:
            print(f"Warning: Could not save keyring: {e}")

    def get_current_key(self) -> Optional[str]:
        """Get the current (most recent) active key."""
        now = datetime.now(timezone.utc).isoformat()
        active_keys = [
            k
            for k in self._keys
            if k.get("retired_at") is None
        ]
        if active_keys:
            # Return most recently created active key
            return sorted(
                active_keys, key=lambda k: k.get("created_at", "")
            )[-1].get("secret")
        return None

    def get_current_key_id(self) -> Optional[str]:
        """Get key ID of current signing key."""
        now = datetime.now(timezone.utc).isoformat()
        active_keys = [
            k
            for k in self._keys
            if k.get("retired_at") is None
        ]
        if active_keys:
            return sorted(
                active_keys, key=lambda k: k.get("created_at", "")
            )[-1].get("kid")
        return None

    def get_all_valid_keys(self) -> List[str]:
        """Get all keys still valid for verification (not yet expired)."""
        policy = JWTKeyRotationPolicy()
        valid_keys = []
        for key_data in self._keys:
            created_at = datetime.fromisoformat(key_data.get("created_at", ""))
            if policy.is_key_valid_for_verification(created_at):
                valid_keys.append(key_data.get("secret"))
        return valid_keys

    def rotate_key(self, new_secret: str) -> str:
        """
        Add a new key and retire the old active key.

        Args:
            new_secret: New signing key

        Returns:
            Key ID (kid) of new key
        """
        kid = f"key_{len(self._keys) + 1}_{datetime.now(timezone.utc).timestamp()}"

        # Retire current active key
        for key in self._keys:
            if key.get("retired_at") is None:
                key["retired_at"] = datetime.now(timezone.utc).isoformat()

        # Add new key
        self._keys.append(
            {
                "kid": kid,
                "secret": new_secret,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "retired_at": None,
            }
        )

        # Cleanup old keys
        self._cleanup_expired_keys()
        self._save_keys()

        return kid

    def _cleanup_expired_keys(self) -> None:
        """Remove keys that have expired (retention period passed)."""
        policy = JWTKeyRotationPolicy()
        now = datetime.now(timezone.utc)

        self._keys = [
            k
            for k in self._keys
            if policy.is_key_valid_for_verification(
                datetime.fromisoformat(k.get("created_at", ""))
            )
        ]

    def get_key_rotation_schedule(self) -> Dict[str, Any]:
        """Get upcoming key rotation schedule info."""
        policy = JWTKeyRotationPolicy()
        current_key = None

        for key in self._keys:
            if key.get("retired_at") is None:
                current_key = key
                break

        if not current_key:
            return {
                "status": "no_active_key",
                "requires_rotation": True,
            }

        created_at = datetime.fromisoformat(current_key.get("created_at"))
        next_rotation = created_at + timedelta(
            days=policy.rotation_interval_days
        )

        return {
            "status": "active",
            "kid": current_key.get("kid"),
            "created_at": current_key.get("created_at"),
            "next_rotation": next_rotation.isoformat(),
            "requires_rotation": policy.should_rotate_key(created_at),
            "days_until_rotation": max(
                0, (next_rotation - datetime.now(timezone.utc)).days
            ),
        }
