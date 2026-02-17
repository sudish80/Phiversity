"""
Phiversity Database Module - SQLite-based storage for videos and users

This module provides:
1. SQLite database for persistent storage
2. User management (signup, login, sessions)
3. Video history tracking
4. Analytics and statistics
5. API key storage

Author: Phiversity Team
"""

import sqlite3
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict


# Database path
DB_PATH = Path("data/phiversity.db")


def get_db() -> sqlite3.Connection:
    """Get database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            is_admin INTEGER DEFAULT 0,
            api_keys TEXT,
            preferences TEXT
        )
    """)
    
    # Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Videos table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            prompt TEXT NOT NULL,
            solution TEXT,
            video_path TEXT,
            thumbnail_path TEXT,
            duration REAL,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Analytics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            user_id INTEGER,
            video_id INTEGER,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # API keys table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            key_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Templates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            prompt_template TEXT NOT NULL,
            is_public INTEGER DEFAULT 1,
            user_id INTEGER,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")


# User Management
class UserManager:
    """Manage user accounts and authentication."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with salt."""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            salt, pwd_hash = password_hash.split('$')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return new_hash.hex() == pwd_hash
        except:
            return False
    
    @staticmethod
    def create_user(email: str, username: str, password: str) -> int:
        """Create new user."""
        conn = get_db()
        cursor = conn.cursor()
        
        password_hash = UserManager.hash_password(password)
        
        try:
            cursor.execute(
                "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
                (email, username, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
        except sqlite3.IntegrityError as e:
            conn.close()
            raise ValueError(f"User already exists: {e}")
        finally:
            conn.close()
        
        return user_id
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return session info."""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1",
            (email,)
        )
        user = cursor.fetchone()
        
        if not user or not UserManager.verify_password(password, user['password_hash']):
            conn.close()
            return None
        
        # Create session
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=7)
        
        cursor.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user['id'], token, expires_at)
        )
        conn.commit()
        conn.close()
        
        return {
            'user_id': user['id'],
            'email': user['email'],
            'username': user['username'],
            'token': token
        }
    
    @staticmethod
    def get_user(user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, username, created_at, is_admin FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def validate_session(token: str) -> Optional[Dict]:
        """Validate session token."""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT u.id, u.email, u.username, u.is_admin FROM sessions s "
            "JOIN users u ON s.user_id = u.id "
            "WHERE s.token = ? AND s.expires_at > datetime('now') AND u.is_active = 1",
            (token,)
        )
        session = cursor.fetchone()
        conn.close()
        return dict(session) if session else None


# Video Management
class VideoManager:
    """Manage video records."""
    
    @staticmethod
    def create_video(user_id: Optional[int], title: str, prompt: str, solution: str = None) -> int:
        """Create new video record."""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO videos (user_id, title, prompt, solution, status) VALUES (?, ?, ?, ?, ?)",
            (user_id, title, prompt, solution, 'pending')
        )
        conn.commit()
        video_id = cursor.lastrowid
        conn.close()
        
        return video_id
    
    @staticmethod
    def update_video(video_id: int, **kwargs):
        """Update video record."""
        conn = get_db()
        cursor = conn.cursor()
        
        allowed_fields = ['title', 'video_path', 'thumbnail_path', 'duration', 
                         'status', 'error_message', 'metadata', 'completed_at']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [video_id]
        
        cursor.execute(f"UPDATE videos SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_video(video_id: int) -> Optional[Dict]:
        """Get video by ID."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
        video = cursor.fetchone()
        conn.close()
        return dict(video) if video else None
    
    @staticmethod
    def get_user_videos(user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's video history."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM videos WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        videos = [dict(v) for v in cursor.fetchall()]
        conn.close()
        return videos
    
    @staticmethod
    def increment_views(video_id: int):
        """Increment video view count."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE videos SET views = views + 1 WHERE id = ?", (video_id,))
        conn.commit()
        conn.close()


# Analytics
class AnalyticsManager:
    """Track and analyze usage."""
    
    @staticmethod
    def track_event(event_type: str, user_id: Optional[int] = None, 
                   video_id: Optional[int] = None, metadata: Dict = None):
        """Track an analytics event."""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO analytics (event_type, user_id, video_id, metadata) VALUES (?, ?, ?, ?)",
            (event_type, user_id, video_id, json.dumps(metadata) if metadata else None)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_stats(days: int = 30) -> Dict:
        """Get usage statistics."""
        conn = get_db()
        cursor = conn.cursor()
        
        # Total videos
        cursor.execute(
            f"SELECT COUNT(*) FROM videos WHERE created_at > datetime('now', '-{days} days')"
        )
        total_videos = cursor.fetchone()[0]
        
        # Completed videos
        cursor.execute(
            f"SELECT COUNT(*) FROM videos WHERE status = 'completed' AND created_at > datetime('now', '-{days} days')"
        )
        completed_videos = cursor.fetchone()[0]
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Total views
        cursor.execute("SELECT SUM(views) FROM videos")
        total_views = cursor.fetchone()[0] or 0
        
        # Active sessions
        cursor.execute(
            "SELECT COUNT(*) FROM sessions WHERE expires_at > datetime('now')"
        )
        active_sessions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_videos': total_videos,
            'completed_videos': completed_videos,
            'total_users': total_users,
            'total_views': total_views,
            'active_sessions': active_sessions,
            'period_days': days
        }


# Template Management
class TemplateManager:
    """Manage video generation templates."""
    
    @staticmethod
    def create_template(name: str, prompt_template: str, category: str = None,
                       user_id: int = None, is_public: bool = True) -> int:
        """Create new template."""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO templates (name, category, prompt_template, user_id, is_public) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, category, prompt_template, user_id, 1 if is_public else 0)
        )
        conn.commit()
        template_id = cursor.lastrowid
        conn.close()
        
        return template_id
    
    @staticmethod
    def get_templates(category: str = None, user_id: int = None) -> List[Dict]:
        """Get templates."""
        conn = get_db()
        cursor = conn.cursor()
        
        query = "SELECT * FROM templates WHERE (is_public = 1 OR user_id = ?)"
        params = [user_id] if user_id else [None]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY usage_count DESC"
        
        cursor.execute(query, params)
        templates = [dict(t) for t in cursor.fetchall()]
        conn.close()
        
        return templates
    
    @staticmethod
    def increment_usage(template_id: int):
        """Increment template usage count."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE templates SET usage_count = usage_count + 1 WHERE id = ?", (template_id,))
        conn.commit()
        conn.close()


# API Key Management
class APIKeyManager:
    """Manage user API keys."""
    
    @staticmethod
    def store_key(user_id: int, provider: str, api_key: str):
        """Store encrypted API key."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO api_keys (user_id, provider, key_hash) VALUES (?, ?, ?)",
            (user_id, provider, key_hash)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def has_key(user_id: int, provider: str) -> bool:
        """Check if user has API key for provider."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM api_keys WHERE user_id = ? AND provider = ? AND is_active = 1",
            (user_id, provider)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0


# Initialize database on import
if __name__ == "__main__":
    init_db()
    print("Database module ready!")