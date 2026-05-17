"""
Content Maximizer — enriches LLM prompts with real MIT lecture transcripts.

Workflow
────────
1.  Load the 271-topic CSV shipped with the project.
2.  Fuzzy-match the user's question to the best topic(s).
3.  Extract YouTube video IDs from the search-results URL.
4.  Download English captions via ``youtube_transcript_api``.
5.  Return the combined transcript text so the orchestrator can inject
    it into the solver prompt as authoritative reference material.

The LLM is told:  "Use this transcript as your primary source of truth.
Solve the problem yourself, but shape the voiceover, depth, and
notation style to match this MIT-level lecture."
"""

from __future__ import annotations

import csv
import datetime as _dt
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class YouTubeVideo:
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: Optional[_dt.datetime]
    view_count: int
    duration_seconds: Optional[int]
    channel_subscribers: Optional[int]


@dataclass(frozen=True)
class TranscriptSegment:
    start: float
    duration: float
    text: str


def _truthy_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _cache_dir() -> Path:
    raw = os.getenv("CONTENT_MAX_CACHE_DIR", "").strip()
    if raw:
        return Path(raw)
    return Path(__file__).resolve().parents[1] / "media" / "cache" / "content_maximizer"


def _cache_ttl_seconds() -> int:
    try:
        hours = float(os.getenv("CONTENT_MAX_CACHE_TTL_HOURS", "168"))
    except Exception:
        hours = 168.0
    return int(max(0.0, hours * 3600.0))


def _load_cached_transcript(video_id: str) -> Optional[List[TranscriptSegment]]:
    path = _cache_dir() / "transcripts" / f"{video_id}.json"
    try:
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        fetched_at = data.get("fetched_at")
        if fetched_at:
            fetched_dt = _parse_rfc3339_datetime(str(fetched_at))
            if fetched_dt is not None:
                age = (_dt.datetime.now(tz=_dt.timezone.utc) - fetched_dt.astimezone(_dt.timezone.utc)).total_seconds()
                if age > _cache_ttl_seconds():
                    return None
        segments = data.get("segments") or []
        out: List[TranscriptSegment] = []
        for s in segments:
            if not isinstance(s, dict):
                continue
            text = str(s.get("text") or "").strip()
            if not text:
                continue
            out.append(
                TranscriptSegment(
                    start=float(s.get("start") or 0.0),
                    duration=float(s.get("duration") or 0.0),
                    text=text,
                )
            )
        return out or None
    except Exception:
        return None


def _write_cached_transcript(video_id: str, segments: List[TranscriptSegment], source: str) -> None:
    base = _cache_dir() / "transcripts"
    try:
        base.mkdir(parents=True, exist_ok=True)
        path = base / f"{video_id}.json"
        tmp = path.with_suffix(".json.tmp")
        payload = {
            "video_id": video_id,
            "source": source,
            "fetched_at": _dt.datetime.now(tz=_dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "segments": [
                {"start": s.start, "duration": s.duration, "text": s.text} for s in segments
            ],
        }
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
    except Exception:
        return

_EN_STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "did",
    "do",
    "does",
    "doing",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "me",
    "more",
    "most",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "s",
    "same",
    "she",
    "should",
    "so",
    "some",
    "such",
    "t",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "will",
    "with",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    # common query filler
    "video",
    "videos",
    "explain",
    "explains",
    "explained",
    "explanation",
    "meaning",
    "definition",
}


def extract_search_query(question: str, max_keywords: int = 12) -> str:
    """Convert a natural-language question to a compact YouTube search query.

    This intentionally uses a lightweight keyword heuristic (O(n) in tokens) to
    avoid any heavy model dependency.
    """
    words = re.findall(r"[a-zA-Z0-9']+", question.lower())
    keywords: List[str] = []
    seen: set[str] = set()
    for w in words:
        if len(w) < 3:
            continue
        if w in _EN_STOPWORDS:
            continue
        if w not in seen:
            seen.add(w)
            keywords.append(w)
        if len(keywords) >= max_keywords:
            break

    query = " ".join(keywords).strip()
    if query and "lecture" not in query and "tutorial" not in query and "explained" not in query:
        query = f"{query} lecture"
    return query or question.strip()


def _parse_iso8601_duration_to_seconds(duration: str) -> Optional[int]:
    """Parse YouTube ISO-8601 duration (e.g. PT1H2M3S) to seconds."""
    if not duration:
        return None
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not m:
        return None
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    seconds = int(m.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def _parse_rfc3339_datetime(dt: str) -> Optional[_dt.datetime]:
    if not dt:
        return None
    # Example: 2020-01-01T00:00:00Z
    try:
        if dt.endswith("Z"):
            return _dt.datetime.fromisoformat(dt.replace("Z", "+00:00"))
        parsed = _dt.datetime.fromisoformat(dt)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=_dt.timezone.utc)
        return parsed
    except Exception:
        return None


def _youtube_api_key() -> str:
    key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY is not set")
    return key


def search_videos(query: str, max_results: int = 10) -> List[YouTubeVideo]:
    """Discover YouTube videos using the YouTube Data API v3."""
    try:
        import requests  # type: ignore
    except Exception as e:
        print(f"[content_maximizer] requests not available for YouTube API search: {e}")
        return []

    try:
        api_key = _youtube_api_key()
    except Exception as e:
        print(f"[content_maximizer] YouTube API disabled: {e}")
        return []

    timeout = int(os.getenv("CONTENT_MAX_HTTP_TIMEOUT", "10"))

    # 1) Search by query to get video IDs
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "key": api_key,
                "part": "snippet",
                "type": "video",
                "q": query,
                "maxResults": max_results,
                "safeSearch": "moderate",
            },
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[content_maximizer] YouTube API search failed: {type(e).__name__}: {e}")
        return []

    video_ids: List[str] = []
    for item in data.get("items", []) or []:
        vid = ((item.get("id") or {}).get("videoId") or "").strip()
        if vid and vid not in video_ids:
            video_ids.append(vid)
    if not video_ids:
        return []

    # 2) Fetch statistics + duration for the candidate videos
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "key": api_key,
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(video_ids),
                "maxResults": len(video_ids),
            },
            timeout=timeout,
        )
        r.raise_for_status()
        vdata = r.json()
    except Exception as e:
        print(f"[content_maximizer] YouTube API videos() failed: {type(e).__name__}: {e}")
        return []

    by_id: Dict[str, YouTubeVideo] = {}
    channel_ids: List[str] = []
    for item in vdata.get("items", []) or []:
        vid = (item.get("id") or "").strip()
        snippet = item.get("snippet") or {}
        stats = item.get("statistics") or {}
        content = item.get("contentDetails") or {}

        channel_id = (snippet.get("channelId") or "").strip()
        if channel_id and channel_id not in channel_ids:
            channel_ids.append(channel_id)

        by_id[vid] = YouTubeVideo(
            video_id=vid,
            title=(snippet.get("title") or "").strip(),
            description=(snippet.get("description") or "").strip(),
            channel_id=channel_id,
            channel_title=(snippet.get("channelTitle") or "").strip(),
            published_at=_parse_rfc3339_datetime((snippet.get("publishedAt") or "").strip()),
            view_count=int(stats.get("viewCount") or 0),
            duration_seconds=_parse_iso8601_duration_to_seconds((content.get("duration") or "").strip()),
            channel_subscribers=None,
        )

    # 3) Channel authority (subscribers), best-effort
    subs_map: Dict[str, int] = {}
    if channel_ids:
        try:
            r = requests.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "key": api_key,
                    "part": "statistics",
                    "id": ",".join(channel_ids[:50]),
                    "maxResults": min(len(channel_ids), 50),
                },
                timeout=timeout,
            )
            r.raise_for_status()
            cdata = r.json()
            for c in cdata.get("items", []) or []:
                cid = (c.get("id") or "").strip()
                subs = (c.get("statistics") or {}).get("subscriberCount")
                if cid and subs is not None:
                    try:
                        subs_map[cid] = int(subs)
                    except Exception:
                        continue
        except Exception as e:
            print(f"[content_maximizer] YouTube API channels() failed (non-fatal): {type(e).__name__}: {e}")

    # Preserve search order
    results: List[YouTubeVideo] = []
    for vid in video_ids:
        v = by_id.get(vid)
        if not v:
            continue
        subs = subs_map.get(v.channel_id)
        if subs is not None:
            v = YouTubeVideo(
                video_id=v.video_id,
                title=v.title,
                description=v.description,
                channel_id=v.channel_id,
                channel_title=v.channel_title,
                published_at=v.published_at,
                view_count=v.view_count,
                duration_seconds=v.duration_seconds,
                channel_subscribers=subs,
            )
        results.append(v)

    return results


def _minmax(values: List[float]) -> List[float]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if hi <= lo:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def rank_videos(question: str, videos: List[YouTubeVideo]) -> List[YouTubeVideo]:
    """Rank candidate videos for knowledge quality and relevance."""
    if not videos:
        return []

    import math as _math

    query_kw = set(re.findall(r"[a-z]+", extract_search_query(question).lower()))

    semantic: List[float] = []
    view_scores: List[float] = []
    recency_scores: List[float] = []
    auth_scores: List[float] = []

    now = _dt.datetime.now(tz=_dt.timezone.utc)
    for v in videos:
        text = f"{v.title} {v.description}".lower()
        v_words = set(re.findall(r"[a-z]+", text))
        sem = 0.0
        if query_kw:
            sem = len(query_kw & v_words) / max(1, len(query_kw))
        semantic.append(float(max(0.0, min(1.0, sem))))

        view_scores.append(float(_math.log1p(v.view_count)))

        if v.published_at is not None:
            days = max(0.0, (now - v.published_at.astimezone(_dt.timezone.utc)).total_seconds() / 86400.0)
            recency_scores.append(1.0 / (1.0 + (days / 365.0)))
        else:
            recency_scores.append(0.0)

        auth_scores.append(float(_math.log1p(v.channel_subscribers or 0)))

    view_norm = _minmax(view_scores)
    auth_norm = _minmax(auth_scores)
    # Recency already in (0,1], but normalize within candidates to avoid over-weighting.
    recency_norm = _minmax(recency_scores)

    scored: List[Tuple[YouTubeVideo, float]] = []
    for i, v in enumerate(videos):
        score = (
            0.4 * semantic[i]
            + 0.3 * view_norm[i]
            + 0.2 * recency_norm[i]
            + 0.1 * auth_norm[i]
        )
        scored.append((v, float(score)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [v for v, _ in scored]


@dataclass(frozen=True)
class TranscriptChunk:
    video_id: str
    title: str
    start: float
    end: float
    text: str


def _safe_cache_key(value: str, max_len: int = 120) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_.-]+", "-", value)
    return value[:max_len] if value else "default"


def _embeddings_cache_path(video_id: str, chunk_size: int, overlap: int) -> Path:
    backend = os.getenv("CONTENT_MAX_EMBED_BACKEND", "hash").strip().lower()
    if backend == "openai":
        model = os.getenv("CONTENT_MAX_EMBED_MODEL", "text-embedding-3-small")
        model_key = _safe_cache_key(model)
    else:
        dim = int(os.getenv("CONTENT_MAX_HASH_DIM", "512"))
        model_key = f"hash{dim}"
    key = _safe_cache_key(f"{backend}-{model_key}-cs{chunk_size}-ov{overlap}")
    return _cache_dir() / "embeddings" / f"{video_id}__{key}.json"


def _load_cached_embeddings(video_id: str, chunk_size: int, overlap: int) -> Optional[List[Tuple[TranscriptChunk, List[float]]]]:
    path = _embeddings_cache_path(video_id, chunk_size, overlap)
    try:
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        created_at = data.get("created_at")
        if created_at:
            created_dt = _parse_rfc3339_datetime(str(created_at))
            if created_dt is not None:
                age = (_dt.datetime.now(tz=_dt.timezone.utc) - created_dt.astimezone(_dt.timezone.utc)).total_seconds()
                if age > _cache_ttl_seconds():
                    return None
        items = data.get("items") or []
        out: List[Tuple[TranscriptChunk, List[float]]] = []
        for it in items:
            if not isinstance(it, dict):
                continue
            vec = it.get("vector")
            text = str(it.get("text") or "").strip()
            if not isinstance(vec, list) or not text:
                continue
            try:
                vector = [float(x) for x in vec]
            except Exception:
                continue
            chunk = TranscriptChunk(
                video_id=video_id,
                title=str(it.get("title") or "").strip(),
                start=float(it.get("start") or 0.0),
                end=float(it.get("end") or 0.0),
                text=text,
            )
            out.append((chunk, vector))
        return out or None
    except Exception:
        return None


def _write_cached_embeddings(
    video_id: str,
    chunk_size: int,
    overlap: int,
    items: List[Tuple[TranscriptChunk, List[float]]],
) -> None:
    path = _embeddings_cache_path(video_id, chunk_size, overlap)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        payload = {
            "video_id": video_id,
            "created_at": _dt.datetime.now(tz=_dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "chunk_size": int(chunk_size),
            "overlap": int(overlap),
            "items": [
                {
                    "title": c.title,
                    "start": c.start,
                    "end": c.end,
                    "text": c.text,
                    "vector": v,
                }
                for c, v in items
            ],
        }
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
    except Exception:
        return

def _tokenize_words(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def _hash_embed(text: str, dim: int = 512) -> List[float]:
    """Fast local embedding using a hashing trick + L2 normalization."""
    import hashlib
    import math

    vec = [0.0] * dim
    for tok in _tokenize_words(text):
        if not tok or tok in _EN_STOPWORDS:
            continue
        h = hashlib.blake2b(tok.encode("utf-8"), digest_size=8).digest()
        n = int.from_bytes(h, byteorder="little", signed=False)
        idx = n % dim
        sign = -1.0 if (n >> 63) & 1 else 1.0
        vec[idx] += sign

    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _openai_embed(texts: List[str]) -> Optional[List[List[float]]]:
    try:
        from .orchestrator.llm_clients import get_chatgpt_client  # type: ignore
    except Exception:
        try:
            from scripts.orchestrator.llm_clients import get_chatgpt_client  # type: ignore
        except Exception:
            return None
    try:
        client = get_chatgpt_client()
    except Exception:
        return None

    model = os.getenv("CONTENT_MAX_EMBED_MODEL", "text-embedding-3-small")
    try:
        resp = client.embeddings.create(model=model, input=texts)
        data = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
        if not isinstance(data, list):
            return None
        out: List[List[float]] = []
        for item in data:
            emb = getattr(item, "embedding", None) or (item.get("embedding") if isinstance(item, dict) else None)
            if isinstance(emb, list) and emb and isinstance(emb[0], (int, float)):
                out.append([float(x) for x in emb])
        return out if len(out) == len(texts) else None
    except Exception as e:
        print(f"[content_maximizer] OpenAI embedding failed (non-fatal): {type(e).__name__}: {e}")
        return None


def embed(texts: List[str]) -> List[List[float]]:
    backend = os.getenv("CONTENT_MAX_EMBED_BACKEND", "hash").strip().lower()
    if backend == "openai":
        out = _openai_embed(texts)
        if out is not None:
            return out
        print("[content_maximizer] Falling back to local hash embeddings")
    dim = int(os.getenv("CONTENT_MAX_HASH_DIM", "512"))
    return [_hash_embed(t, dim=dim) for t in texts]


def _cosine(a: List[float], b: List[float]) -> float:
    import math

    dot = 0.0
    na = 0.0
    nb = 0.0
    for i in range(min(len(a), len(b))):
        av = float(a[i])
        bv = float(b[i])
        dot += av * bv
        na += av * av
        nb += bv * bv
    denom = math.sqrt(na) * math.sqrt(nb) or 1.0
    return dot / denom


class InMemoryVectorDB:
    def __init__(self) -> None:
        self._items: List[Tuple[List[float], TranscriptChunk]] = []

    def store(self, vector: List[float], chunk: TranscriptChunk) -> None:
        self._items.append((vector, chunk))

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        min_score: Optional[float] = None,
    ) -> List[Tuple[TranscriptChunk, float]]:
        scored: List[Tuple[TranscriptChunk, float]] = []
        for v, chunk in self._items:
            score = _cosine(query_vector, v)
            if min_score is not None and score < float(min_score):
                continue
            scored.append((chunk, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[: max(0, int(top_k))]


def _filter_segments_by_similarity(question: str, segments: List[TranscriptSegment]) -> List[TranscriptSegment]:
    """Advanced trick: keep only transcript segments relevant to the question."""
    try:
        threshold = float(os.getenv("CONTENT_MAX_SEGMENT_SIM_THRESHOLD", "0.18"))
    except Exception:
        threshold = 0.18

    q_kw = set(re.findall(r"[a-z]+", extract_search_query(question).lower()))
    if not q_kw:
        return segments

    keep_idx: set[int] = set()
    for i, seg in enumerate(segments):
        words = set(re.findall(r"[a-z]+", seg.text.lower()))
        sim = len(q_kw & words) / max(1, len(q_kw))
        if sim >= threshold:
            keep_idx.add(i)
            # include immediate neighbors for context
            if i - 1 >= 0:
                keep_idx.add(i - 1)
            if i + 1 < len(segments):
                keep_idx.add(i + 1)

    if not keep_idx:
        return segments
    kept = [segments[i] for i in sorted(keep_idx)]
    # If we filtered too aggressively, fall back to full transcript.
    if len(kept) < max(5, int(0.05 * len(segments))):
        return segments
    return kept


def chunk_transcript(
    video: YouTubeVideo,
    segments: List[TranscriptSegment],
    chunk_size: int = 400,
    overlap: int = 50,
) -> List[TranscriptChunk]:
    """Algorithm 6 â€” chunk transcript into overlapping windows (token ~= word)."""
    if chunk_size <= 0:
        return []
    overlap = max(0, min(overlap, max(0, chunk_size - 1)))

    # Tokenize while keeping mapping back to segment index for timestamps.
    token_seg_idx: List[int] = []
    tokens: List[str] = []
    for idx, seg in enumerate(segments):
        seg_tokens = seg.text.split()
        if not seg_tokens:
            continue
        tokens.extend(seg_tokens)
        token_seg_idx.extend([idx] * len(seg_tokens))

    if not tokens:
        return []

    chunks: List[TranscriptChunk] = []
    start = 0
    while start < len(tokens):
        end = min(len(tokens), start + chunk_size)
        chunk_tokens = tokens[start:end]
        first_seg = segments[token_seg_idx[start]] if token_seg_idx else segments[0]
        last_seg = segments[token_seg_idx[end - 1]] if token_seg_idx else segments[-1]
        start_t = float(first_seg.start)
        end_t = float(last_seg.start + (last_seg.duration or 0.0))
        chunks.append(
            TranscriptChunk(
                video_id=video.video_id,
                title=video.title,
                start=start_t,
                end=end_t,
                text=" ".join(chunk_tokens).strip(),
            )
        )
        if end >= len(tokens):
            break
        start = max(0, end - overlap)
    return chunks


def retrieve_relevant_chunks(
    question: str,
    video_transcripts: List[Tuple[YouTubeVideo, List[TranscriptSegment]]],
    top_k: int = 5,
    chunk_size: int = 400,
    overlap: int = 50,
) -> List[Tuple[TranscriptChunk, float]]:
    """Algorithms 6-8 — chunk, embed, store, then retrieve top context chunks."""
    all_chunks: List[TranscriptChunk] = []
    for video, segments in video_transcripts:
        filtered = _filter_segments_by_similarity(question, segments)
        all_chunks.extend(chunk_transcript(video, filtered, chunk_size=chunk_size, overlap=overlap))

    if not all_chunks:
        return []

    vectors = embed([c.text for c in all_chunks])
    db = InMemoryVectorDB()
    for vec, chunk in zip(vectors, all_chunks):
        db.store(vec, chunk)

    q_vec = embed([question])[0]
    min_score = None
    try:
        min_score = float(os.getenv("CONTENT_MAX_CHUNK_SIM_THRESHOLD", "0") or 0.0)
    except Exception:
        min_score = None
    return db.search(q_vec, top_k=top_k, min_score=min_score)


def _chunks_and_vectors_for_video(
    question: str,
    video: YouTubeVideo,
    segments: List[TranscriptSegment],
    chunk_size: int,
    overlap: int,
) -> List[Tuple[TranscriptChunk, List[float]]]:
    cache_enabled = _truthy_env("CONTENT_MAX_CACHE_EMBEDDINGS", default=True)
    pre_filter = _truthy_env("CONTENT_MAX_PRE_FILTER_SEGMENTS", default=False)

    if cache_enabled and not pre_filter:
        cached = _load_cached_embeddings(video.video_id, chunk_size, overlap)
        if cached:
            return cached

    segs = _filter_segments_by_similarity(question, segments) if pre_filter else segments
    chunks = chunk_transcript(video, segs, chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        return []
    vectors = embed([c.text for c in chunks])
    items = list(zip(chunks, vectors))

    if cache_enabled and not pre_filter:
        _write_cached_embeddings(video.video_id, chunk_size, overlap, items)

    return items

# ══════════════════════════════════════════════════════════════════════════════
# TOPIC DATABASE
# ══════════════════════════════════════════════════════════════════════════════

# Each row: (subject, topic, youtube_search_url)
TopicRow = Tuple[str, str, str]

_TOPICS_CACHE: Optional[List[TopicRow]] = None


def _csv_path() -> Path:
    """Return the default CSV path (project root)."""
    return Path(__file__).resolve().parents[1] / "mit_style_150_lecture_topics.csv"


def load_topics(csv_file: Optional[Path] = None) -> List[TopicRow]:
    """Load and cache the topic CSV.  No header row expected."""
    global _TOPICS_CACHE
    if _TOPICS_CACHE is not None:
        return _TOPICS_CACHE

    path = csv_file or _csv_path()
    if not path.exists():
        print(f"[content_maximizer] WARNING: Topic CSV not found at {path}")
        _TOPICS_CACHE = []
        return _TOPICS_CACHE

    rows: List[TopicRow] = []
    with open(path, encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3:
                subject, topic, url = row[0].strip(), row[1].strip(), row[2].strip()
                if subject and topic and url:
                    rows.append((subject, topic, url))
    _TOPICS_CACHE = rows
    print(f"[content_maximizer] Loaded {len(rows)} topics from {path}")
    return _TOPICS_CACHE


# ══════════════════════════════════════════════════════════════════════════════
# TOPIC MATCHING
# ══════════════════════════════════════════════════════════════════════════════

def _similarity(a: str, b: str) -> float:
    """Case-insensitive SequenceMatcher ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _keyword_overlap(question: str, topic: str) -> float:
    """Fraction of topic words found in the question."""
    q_words = set(re.findall(r"[a-z]+", question.lower()))
    t_words = set(re.findall(r"[a-z]+", topic.lower()))
    if not t_words:
        return 0.0
    return len(q_words & t_words) / len(t_words)


def match_topics(
    question: str,
    topics: Optional[List[TopicRow]] = None,
    top_k: int = 3,
    min_score: float = 0.25,
) -> List[Tuple[TopicRow, float]]:
    """Return the *top_k* best-matching topics for *question*.

    Score = 0.4 * sequence_similarity + 0.6 * keyword_overlap.
    Results below *min_score* are dropped.
    """
    topics = topics or load_topics()
    if not topics:
        return []

    scored: List[Tuple[TopicRow, float]] = []
    for row in topics:
        subject, topic, url = row
        combined = f"{subject} {topic}"
        sim  = _similarity(question, combined)
        kw   = _keyword_overlap(question, topic)
        score = 0.4 * sim + 0.6 * kw
        scored.append((row, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    results = [(row, sc) for row, sc in scored[:top_k] if sc >= min_score]
    return results


# ══════════════════════════════════════════════════════════════════════════════
# YOUTUBE VIDEO ID EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════

_VIDEO_ID_RE = re.compile(r'"videoId"\s*:\s*"([a-zA-Z0-9_-]{11})"')

# Cache the result of the YouTube reachability check for the process lifetime.
_YOUTUBE_REACHABLE: Optional[bool] = None


def _check_youtube_reachable(timeout: int = 5) -> bool:
    """Quick TCP probe to youtube.com:443 to avoid slow timeouts per video."""
    global _YOUTUBE_REACHABLE
    if _YOUTUBE_REACHABLE is not None:
        return _YOUTUBE_REACHABLE
    import socket
    try:
        sock = socket.create_connection(("www.youtube.com", 443), timeout=timeout)
        sock.close()
        _YOUTUBE_REACHABLE = True
    except (OSError, socket.timeout):
        print("[content_maximizer] YouTube is unreachable — skipping transcript fetching")
        _YOUTUBE_REACHABLE = False
    return _YOUTUBE_REACHABLE


def _extract_video_ids_from_search(search_url: str, max_ids: int = 3) -> List[str]:
    """Fetch a YouTube search-results page and scrape video IDs from the HTML."""
    if not _check_youtube_reachable():
        return []
    try:
        req = urllib.request.Request(
            search_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        timeout = int(os.getenv("CONTENT_MAX_HTTP_TIMEOUT", "10"))
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[content_maximizer] Could not fetch search page: {e}")
        return []

    # Deduplicate while preserving order
    seen: set = set()
    ids: List[str] = []
    for m in _VIDEO_ID_RE.finditer(html):
        vid = m.group(1)
        if vid not in seen:
            seen.add(vid)
            ids.append(vid)
        if len(ids) >= max_ids:
            break
    return ids


# ══════════════════════════════════════════════════════════════════════════════
# TRANSCRIPT FETCHING
# ══════════════════════════════════════════════════════════════════════════════

# Track consecutive transcriptapi.com failures to stop retrying.
_TRANSCRIPT_API_FAILURES: int = 0
_TRANSCRIPT_API_MAX_FAILURES: int = 2


def _segments_from_youtube_transcript_api(video_id: str) -> Optional[List[TranscriptSegment]]:
    """Primary: download transcript segments via youtube-transcript-api."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
    except ImportError:
        print("[content_maximizer] youtube-transcript-api not installed â€” pip install youtube-transcript-api")
        return None

    if not _check_youtube_reachable():
        return None

    import requests as _req

    timeout_sec = int(os.getenv("CONTENT_MAX_HTTP_TIMEOUT", "10"))
    session = _req.Session()
    adapter = _req.adapters.HTTPAdapter()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    _orig_request = session.request

    def _patched_request(*args, **kwargs):
        kwargs.setdefault("timeout", timeout_sec)
        return _orig_request(*args, **kwargs)

    session.request = _patched_request  # type: ignore[assignment]

    try:
        api = YouTubeTranscriptApi(http_client=session)
    except Exception:
        api = YouTubeTranscriptApi()

    def _to_segments(fetched) -> List[TranscriptSegment]:
        segs: List[TranscriptSegment] = []
        for snip in fetched or []:
            if isinstance(snip, dict):
                text = str(snip.get("text") or "").strip()
                start = float(snip.get("start") or 0.0)
                dur = float(snip.get("duration") or 0.0)
            else:
                text = str(getattr(snip, "text", "") or "").strip()
                start = float(getattr(snip, "start", 0.0) or 0.0)
                dur = float(getattr(snip, "duration", 0.0) or 0.0)
            if text:
                segs.append(TranscriptSegment(start=start, duration=dur, text=text))
        return segs

    lang_attempts = [("en",), ("en-US",), ("en-GB",), None]
    for langs in lang_attempts:
        try:
            if hasattr(api, "fetch"):
                fetched = api.fetch(video_id, languages=langs) if langs is not None else api.fetch(video_id)
            else:
                fetched = api.get_transcript(video_id, languages=list(langs) if langs is not None else None)  # type: ignore[attr-defined]
            segments = _to_segments(fetched)
            if segments:
                return segments
        except (OSError, _req.exceptions.ConnectionError, _req.exceptions.Timeout):
            print(f"[content_maximizer] youtube-transcript-api network error for {video_id}")
            global _YOUTUBE_REACHABLE
            _YOUTUBE_REACHABLE = False
            return None
        except Exception as e:
            err_msg = str(e)
            if "blocking" in err_msg.lower() or "RequestBlocked" in type(e).__name__:
                print("[content_maximizer] YouTube is blocking requests â€” skipping remaining transcripts")
                _YOUTUBE_REACHABLE = False
                return None
            if langs is None:
                print(f"[content_maximizer] youtube-transcript-api failed for {video_id}: {e}")
            continue

    return None


def _segments_from_transcriptapi(video_id: str) -> Optional[List[TranscriptSegment]]:
    """Fallback: transcriptapi.com (best-effort)."""
    global _TRANSCRIPT_API_FAILURES
    api_key = os.getenv("TRANSCRIPT_API_KEY", "")
    if not api_key:
        return None
    if _TRANSCRIPT_API_FAILURES >= _TRANSCRIPT_API_MAX_FAILURES:
        return None

    url = (
        f"https://transcriptapi.com/api/v2/youtube/transcript"
        f"?video_url={video_id}&format=json"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
    )
    timeout = int(os.getenv("CONTENT_MAX_HTTP_TIMEOUT", "10"))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        _TRANSCRIPT_API_FAILURES = 0
    except Exception as e:
        _TRANSCRIPT_API_FAILURES += 1
        if _TRANSCRIPT_API_FAILURES >= _TRANSCRIPT_API_MAX_FAILURES:
            print(f"[content_maximizer] transcriptapi.com failed {_TRANSCRIPT_API_FAILURES} times â€” disabling for this run")
        else:
            print(f"[content_maximizer] transcriptapi.com failed for {video_id}: {e}")
        return None

    transcript_items = data if isinstance(data, list) else data.get("transcript", data.get("captions", []))
    if not isinstance(transcript_items, list) or not transcript_items:
        return None

    out: List[TranscriptSegment] = []
    t = 0.0
    for item in transcript_items:
        if isinstance(item, dict):
            text = str(item.get("text") or "").strip()
            start = float(item.get("start") or t)
            dur = float(item.get("duration") or 0.0)
        else:
            text = str(item or "").strip()
            start = t
            dur = 0.0
        if text:
            out.append(TranscriptSegment(start=start, duration=dur, text=text))
        t += max(dur, 0.0)
    return out or None


def getTranscript(video_id: str) -> Optional[List[TranscriptSegment]]:
    """Algorithm 4 â€” transcript retrieval (cached)."""
    cached = _load_cached_transcript(video_id)
    if cached:
        return cached

    segments = _segments_from_youtube_transcript_api(video_id)
    if segments:
        _write_cached_transcript(video_id, segments, source="youtube-transcript-api")
        return segments

    segments = _segments_from_transcriptapi(video_id)
    if segments:
        _write_cached_transcript(video_id, segments, source="transcriptapi.com")
        return segments

    return None


def _download_audio_ytdlp(video_id: str, out_dir: Path) -> Optional[Path]:
    import shutil
    import subprocess

    ytdlp = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")
    if not ytdlp:
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    out_tpl = str(out_dir / "%(id)s.%(ext)s")
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        ytdlp,
        "--no-playlist",
        "-f",
        "bestaudio/best",
        "-x",
        "--audio-format",
        "mp3",
        "-o",
        out_tpl,
        url,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except Exception as e:
        print(f"[content_maximizer] yt-dlp failed for {video_id}: {type(e).__name__}: {e}")
        return None

    candidate = out_dir / f"{video_id}.mp3"
    if candidate.exists():
        return candidate
    files = list(out_dir.glob(f"{video_id}.*"))
    return files[0] if files else None


def _speech_to_text_openai(audio_path: Path) -> Optional[str]:
    try:
        from .orchestrator.llm_clients import get_chatgpt_client  # type: ignore
    except Exception:
        try:
            from scripts.orchestrator.llm_clients import get_chatgpt_client  # type: ignore
        except Exception as e:
            print(f"[content_maximizer] OpenAI client unavailable for STT: {e}")
            return None

    try:
        client = get_chatgpt_client()
    except Exception as e:
        print(f"[content_maximizer] STT disabled (no OPENAI_API_KEY): {e}")
        return None

    model = os.getenv("CONTENT_MAX_STT_MODEL", "whisper-1")
    try:
        with open(audio_path, "rb") as f:
            resp = client.audio.transcriptions.create(model=model, file=f)
        text = getattr(resp, "text", None) or (resp.get("text") if isinstance(resp, dict) else None)
        if isinstance(text, str) and text.strip():
            return text.strip()
    except Exception as e:
        print(f"[content_maximizer] OpenAI STT failed: {type(e).__name__}: {e}")
    return None


def generateTranscript(video_id: str) -> Optional[List[TranscriptSegment]]:
    """Algorithm 5 â€” fallback speech-to-text (optional; enable via CONTENT_MAX_STT_ENABLED)."""
    if not _truthy_env("CONTENT_MAX_STT_ENABLED"):
        return None

    import tempfile

    with tempfile.TemporaryDirectory(prefix=f"phiversity-stt-{video_id}-") as td:
        audio = _download_audio_ytdlp(video_id, Path(td))
        if not audio:
            print("[content_maximizer] STT fallback unavailable (yt-dlp missing or download failed)")
            return None

        backend = os.getenv("CONTENT_MAX_STT_BACKEND", "openai").strip().lower()
        text: Optional[str] = None
        if backend == "openai":
            text = _speech_to_text_openai(audio)
        else:
            print(f"[content_maximizer] Unsupported STT backend: {backend}")
            return None

        if not text:
            return None
        segs = [TranscriptSegment(start=0.0, duration=0.0, text=text)]
        _write_cached_transcript(video_id, segs, source=f"stt:{backend}")
        return segs


def _fetch_transcript_api(video_id: str) -> Optional[str]:
    """Fetch transcript via transcriptapi.com (fallback method).

    Uses the v2 REST endpoint with Bearer token auth.
    Stops trying after repeated failures to avoid wasting time.
    """
    global _TRANSCRIPT_API_FAILURES
    api_key = os.getenv("TRANSCRIPT_API_KEY", "")
    if not api_key:
        return None
    if _TRANSCRIPT_API_FAILURES >= _TRANSCRIPT_API_MAX_FAILURES:
        return None

    url = (
        f"https://transcriptapi.com/api/v2/youtube/transcript"
        f"?video_url={video_id}&format=json"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
    )
    timeout = int(os.getenv("CONTENT_MAX_HTTP_TIMEOUT", "10"))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        _TRANSCRIPT_API_FAILURES = 0  # reset on success
    except Exception as e:
        _TRANSCRIPT_API_FAILURES += 1
        if _TRANSCRIPT_API_FAILURES >= _TRANSCRIPT_API_MAX_FAILURES:
            print(f"[content_maximizer] transcriptapi.com failed {_TRANSCRIPT_API_FAILURES} times — disabling for this run")
        else:
            print(f"[content_maximizer] transcriptapi.com failed for {video_id}: {e}")
        return None

    # The API may return {"transcript": [{"text": ..., ...}, ...]} or similar
    transcript_items = data if isinstance(data, list) else data.get("transcript", data.get("captions", []))
    if isinstance(transcript_items, list):
        lines = []
        for item in transcript_items:
            if isinstance(item, dict):
                lines.append(item.get("text", ""))
            elif isinstance(item, str):
                lines.append(item)
        text = " ".join(line for line in lines if line).strip()
        if text:
            return text

    # Fallback: maybe the response is a plain string
    if isinstance(data, str) and len(data) > 50:
        return data.strip()

    print(f"[content_maximizer] transcriptapi.com returned empty for {video_id}")
    return None


def _fetch_transcript_lib(video_id: str) -> Optional[str]:
    """Primary: download transcript via youtube-transcript-api library."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
    except ImportError:
        print("[content_maximizer] youtube-transcript-api not installed — pip install youtube-transcript-api")
        return None

    if not _check_youtube_reachable():
        return None

    import requests as _req

    # The library uses requests internally without a timeout, so we configure
    # a session with a connect/read timeout to avoid hanging.
    timeout_sec = int(os.getenv("CONTENT_MAX_HTTP_TIMEOUT", "10"))
    session = _req.Session()
    adapter = _req.adapters.HTTPAdapter()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    # Monkey-patch the session's request method to enforce a timeout
    _orig_request = session.request
    def _patched_request(*args, **kwargs):
        kwargs.setdefault("timeout", timeout_sec)
        return _orig_request(*args, **kwargs)
    session.request = _patched_request

    api = YouTubeTranscriptApi(http_client=session)
    # Try English variants first, then any available language
    lang_attempts = [("en",), ("en-US",), ("en-GB",), None]
    for langs in lang_attempts:
        try:
            if langs is not None:
                fetched = api.fetch(video_id, languages=langs)
            else:
                fetched = api.fetch(video_id)
            lines = [snippet.text for snippet in fetched]
            text = " ".join(lines).strip()
            if text:
                return text
        except (OSError, _req.exceptions.ConnectionError, _req.exceptions.Timeout) as e:
            print(f"[content_maximizer] youtube-transcript-api network error for {video_id}: {type(e).__name__}")
            # Mark YouTube unreachable to skip remaining videos
            global _YOUTUBE_REACHABLE
            _YOUTUBE_REACHABLE = False
            return None
        except Exception as e:
            err_msg = str(e)
            # IP ban / bot detection — no point retrying other lang variants
            if "blocking" in err_msg.lower() or "RequestBlocked" in type(e).__name__:
                print(f"[content_maximizer] YouTube is blocking requests — skipping remaining transcripts")
                _YOUTUBE_REACHABLE = False
                return None
            if langs is None:
                print(f"[content_maximizer] youtube-transcript-api failed for {video_id}: {e}")
            continue
    return None


def _fetch_transcript(video_id: str) -> Optional[str]:
    """Download English transcript for a single YouTube video.

    Strategy: try youtube-transcript-api library first (free, no key needed),
    fall back to transcriptapi.com REST API.
    """
    # Primary: local library (no API key needed)
    text = _fetch_transcript_lib(video_id)
    if text:
        return text

    # Fallback: transcriptapi.com REST API
    text = _fetch_transcript_api(video_id)
    if text:
        return text

    print(f"[content_maximizer] No transcript for video {video_id}")
    return None


def fetch_transcripts(
    search_url: str,
    max_videos: int = 2,
    max_chars: int = 30000,
) -> str:
    """From a YouTube search URL, get transcripts of the top videos.

    Returns combined transcript text, truncated to *max_chars*.
    """
    video_ids = _extract_video_ids_from_search(search_url, max_ids=max_videos + 2)
    if not video_ids:
        return ""

    parts: List[str] = []
    total_len = 0
    for vid in video_ids:
        if len(parts) >= max_videos:
            break
        # If YouTube was marked unreachable mid-run, stop early
        if _YOUTUBE_REACHABLE is False:
            print("[content_maximizer] YouTube unreachable — skipping remaining videos")
            break
        text = _fetch_transcript(vid)
        if text and len(text) > 100:  # skip very short transcripts
            parts.append(text)
            total_len += len(text)
            if total_len >= max_chars:
                break
        # Be polite: small delay between requests
        time.sleep(0.3)

    combined = "\n\n---\n\n".join(parts)
    if len(combined) > max_chars:
        combined = combined[:max_chars] + "\n[transcript truncated]"
    return combined


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRYPOINT — CONTENT MAXIMIZER
# ══════════════════════════════════════════════════════════════════════════════

def _format_hms(seconds: float) -> str:
    try:
        total = int(max(0.0, float(seconds)) + 0.5)
    except Exception:
        total = 0
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _format_views(n: int) -> str:
    try:
        n = int(n)
    except Exception:
        return "0"
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def _build_youtube_context(
    user_question: str,
    max_videos: int,
    max_transcript_chars: int,
) -> str:
    query = extract_search_query(user_question)
    max_results = int(os.getenv("CONTENT_MAX_YOUTUBE_MAX_RESULTS", "10"))
    top_k_chunks = int(os.getenv("CONTENT_MAX_CONTEXT_TOP_K", "5"))
    chunk_size = int(os.getenv("CONTENT_MAX_CHUNK_SIZE", "400"))
    overlap = int(os.getenv("CONTENT_MAX_CHUNK_OVERLAP", "50"))

    print(f"[content_maximizer] YouTube query: {query}")
    videos = search_videos(query, max_results=max_results)
    if not videos:
        print("[content_maximizer] No videos found via YouTube API")
        return ""

    ranked = rank_videos(user_question, videos)
    selected = ranked[: max(1, int(max_videos))]
    print(f"[content_maximizer] Selected top {len(selected)} video(s):")
    for v in selected:
        dur = _format_hms(v.duration_seconds or 0) if v.duration_seconds else "?"
        pub = v.published_at.date().isoformat() if v.published_at else "?"
        subs = _format_views(v.channel_subscribers or 0) if v.channel_subscribers is not None else "?"
        print(
            f"  - {v.title} (id={v.video_id}, views={_format_views(v.view_count)}, dur={dur}, pub={pub}, subs={subs})"
        )

    # Fetch transcripts in parallel (top videos only)
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def _fetch_one(video: YouTubeVideo) -> Tuple[YouTubeVideo, Optional[List[TranscriptSegment]]]:
        segs = getTranscript(video.video_id)
        if segs is None:
            segs = generateTranscript(video.video_id)
        return (video, segs)

    video_transcripts: List[Tuple[YouTubeVideo, List[TranscriptSegment]]] = []
    with ThreadPoolExecutor(max_workers=min(4, len(selected))) as ex:
        futures = [ex.submit(_fetch_one, v) for v in selected]
        for fut in as_completed(futures):
            try:
                video, segs = fut.result()
            except Exception:
                continue
            if segs and len(segs) > 3:
                video_transcripts.append((video, segs))

    if not video_transcripts:
        print("[content_maximizer] No transcripts retrieved â€” proceeding without reference")
        return ""

    db = InMemoryVectorDB()
    for video, segs in video_transcripts:
        for chunk, vec in _chunks_and_vectors_for_video(user_question, video, segs, chunk_size, overlap):
            db.store(vec, chunk)

    q_vec = embed([user_question])[0]
    min_score = None
    try:
        min_score = float(os.getenv("CONTENT_MAX_CHUNK_SIM_THRESHOLD", "0") or 0.0)
    except Exception:
        min_score = None
    retrieved = db.search(q_vec, top_k=top_k_chunks, min_score=min_score)
    if not retrieved:
        print("[content_maximizer] No relevant transcript chunks found")
        return ""

    header = (
        "\n=== REFERENCE MATERIAL â€” YOUTUBE TRANSCRIPTS (RAG) ===\n"
        "Use these excerpts as supporting reference for depth, notation, and explanation style.\n\n"
    )

    parts: List[str] = []
    total = len(header)
    for chunk, _score in retrieved:
        block = (
            f"=== Source: {chunk.title} (video_id={chunk.video_id}) "
            f"[t={_format_hms(chunk.start)}-{_format_hms(chunk.end)}] ===\n"
            f"{chunk.text.strip()}"
        )
        if total + len(block) + 2 > max_transcript_chars:
            break
        parts.append(block)
        total += len(block) + 2

    out = header + "\n\n".join(parts)
    if len(out) > max_transcript_chars:
        out = out[:max_transcript_chars] + "\n[reference truncated]"
    return out


def maximize_content(
    user_question: str,
    max_topics: int = 3,
    max_transcript_chars: int = 25000,
) -> str:
    """Fetch and retrieve relevant transcript excerpts for a question.

    Returns a formatted context block ready to be prepended to the solver
    prompt, or an empty string if nothing was found.
    """
    if os.getenv("CONTENT_MAXIMIZER_DISABLED", "").lower() in ("1", "true", "yes"):
        print("[content_maximizer] Disabled via CONTENT_MAXIMIZER_DISABLED env var")
        return ""

    mode = os.getenv("CONTENT_MAXIMIZER_MODE", "auto").strip().lower()
    if mode == "auto":
        mode = "youtube" if os.getenv("YOUTUBE_API_KEY") else "mit"

    if mode in ("youtube", "yt", "rag"):
        block = _build_youtube_context(
            user_question,
            max_videos=max_topics,
            max_transcript_chars=max_transcript_chars,
        )
        if block:
            return block
        # If explicitly configured for YouTube mode, don't silently switch behavior.
        if os.getenv("CONTENT_MAXIMIZER_MODE", "auto").strip().lower() != "auto":
            return ""

    matches = match_topics(user_question, top_k=max_topics)
    if not matches:
        print("[content_maximizer] No matching topics found — proceeding without transcript")
        return ""

    print(f"[content_maximizer] Matched {len(matches)} topic(s):")
    for (subj, topic, url), score in matches:
        print(f"  [{subj}] {topic}  (score={score:.2f})")

    all_transcripts: List[str] = []
    total_chars = 0
    for (subj, topic, url), score in matches:
        if total_chars >= max_transcript_chars:
            break
        remaining = max_transcript_chars - total_chars
        print(f"[content_maximizer] Fetching transcript for: {topic}...")
        text = fetch_transcripts(url, max_videos=2, max_chars=remaining)
        if text:
            all_transcripts.append(
                f"=== MIT Lecture Reference: {topic} ({subj}) ===\n{text}"
            )
            total_chars += len(text)
            print(f"[content_maximizer] Got {len(text)} chars for '{topic}'")
        else:
            print(f"[content_maximizer] No transcript available for '{topic}'")

    if not all_transcripts:
        print("[content_maximizer] No transcripts retrieved — proceeding without reference")
        return ""

    header = (
        "\n╔══════════════════════════════════════════════════════════════╗\n"
        "║  REFERENCE MATERIAL — MIT-LEVEL LECTURE TRANSCRIPTS        ║\n"
        "║  Use this as your primary source of truth for depth,       ║\n"
        "║  notation, and pedagogical style. Solve the problem        ║\n"
        "║  yourself but match this caliber of explanation.           ║\n"
        "╚══════════════════════════════════════════════════════════════╝\n\n"
    )
    return header + "\n\n".join(all_transcripts)


# ══════════════════════════════════════════════════════════════════════════════
# CLI — standalone testing
# ══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Content Maximizer — retrieve transcript context for a question")
    parser.add_argument("question", help="The user's question or topic")
    parser.add_argument("--top-k", type=int, default=3, help="Number of videos/topics to process")
    parser.add_argument("--max-chars", type=int, default=25000, help="Max transcript characters")
    args = parser.parse_args()

    result = maximize_content(args.question, max_topics=args.top_k, max_transcript_chars=args.max_chars)
    if result:
        print(f"\n{'='*80}\nRESULT ({len(result)} chars):\n{'='*80}")
        print(result[:3000] + ("..." if len(result) > 3000 else ""))
    else:
        print("No content found.")


if __name__ == "__main__":
    main()
