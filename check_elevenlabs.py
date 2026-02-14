#!/usr/bin/env python
"""Check ElevenLabs configuration and API status."""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[0]
load_dotenv(ROOT / ".env", override=True)

print("=== ELEVENLABS CONFIGURATION CHECK ===\n")

# Check .env values
env_file = Path(".env")
if env_file.exists():
    with open(env_file) as f:
        content = f.read()
    
    # Extract values
    for line in content.split('\n'):
        if line.startswith('ELEVENLABS') or line.startswith('VOICE_ENGINE'):
            if '=' in line:
                key, val = line.split('=', 1)
                if 'API_KEY' in key:
                    val = val.strip()
                    val = val[:15] + '***' if len(val) > 15 else '***'
                print(f"{key.strip()} = {val}")

print("\n=== VOICE ENGINE LOGIC ===\n")

# Test the logic
voice_engine = os.getenv("VOICE_ENGINE", "gtts").lower()
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")
prefer_eleven = bool(elevenlabs_key)

print(f"VOICE_ENGINE: {voice_engine}")
print(f"ELEVENLABS_API_KEY present: {bool(elevenlabs_key)}")
print(f"prefer_eleven flag: {prefer_eleven}")
print()

if prefer_eleven or voice_engine == "elevenlabs":
    print("STATUS: Should use ElevenLabs as primary")
else:
    print("STATUS: Using gTTS (fallback)")

print("\n=== PACKAGE CHECK ===\n")

packages = ["elevenlabs", "pyttsx3", "gtts", "moviepy"]
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✓ {pkg} installed")
    except ImportError:
        print(f"✗ {pkg} NOT installed - pip install {pkg}")

print("\n=== ELEVENLABS API TEST ===\n")

if elevenlabs_key:
    print("Testing ElevenLabs API call...")
    try:
        text = "Testing ElevenLabs TTS"
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        payload = {"text": text}
        data = json.dumps(payload).encode("utf-8")
        
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("xi-api-key", elevenlabs_key)
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "audio/mpeg")
        
        with urllib.request.urlopen(req, timeout=5) as resp:
            audio = resp.read()
            if audio:
                print(f"✓ ElevenLabs API WORKING! (received {len(audio)} bytes of audio)")
                print("✓ API key is valid and active")
    except urllib.error.HTTPError as e:
        print(f"✗ ElevenLabs API ERROR: HTTP {e.code}")
        if e.code == 401:
            print("  PROBLEM: API Key is invalid, expired, or has no credits")
            print("  FIX: Get a new API key from https://elevenlabs.io/app/api-keys")
        elif e.code == 400:
            print("  PROBLEM: Bad request - check voice_id or text format")
        elif e.code == 429:
            print("  PROBLEM: Rate limit exceeded")
        else:
            print(f"  MESSAGE: {e.reason}")
    except urllib.error.URLError as e:
        print(f"✗ Network error: {e}")
        print("  PROBLEM: Cannot reach ElevenLabs API (internet issue?)")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("✗ ELEVENLABS_API_KEY not set in .env")
    print("\nTO FIX:")
    print("1. Sign up at https://elevenlabs.io")
    print("2. Get API key from https://elevenlabs.io/app/api-keys")
    print("3. Add to .env: ELEVENLABS_API_KEY=sk_xxx...")
    print("4. Set VOICE_ENGINE=elevenlabs (optional, will use if key exists)")

print("\n=== SUMMARY ===\n")

if elevenlabs_key and prefer_eleven:
    print("✓ ElevenLabs is configured and should be used")
elif elevenlabs_key:
    print("⚠ ElevenLabs API key exists but VOICE_ENGINE != elevenlabs")
    print("  (Currently using: " + voice_engine + ")")
else:
    print("✗ ElevenLabs not configured - using gTTS fallback")
