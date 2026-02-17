# V3.0 CACHE FEATURES - QUICK REFERENCE

## 🎯 Two Features, Dual Visibility

### Feature 1: Verbose Logging
```python
positions = engine.solve_with_constraints(
    elements,
    verbose_tuning=True  # ← Console logging
)
```
**Output**: `[Tune Cache] HIT - Using cached weights for key (1, 5, 4, 0)`

### Feature 2: Tune Info Return
```python
positions, loss, components, tune_info = engine.solve_with_constraints(
    elements,
    return_loss=True  # ← Get 4-tuple
)

print(tune_info['cache_hit'])  # True/False
```

---

## 🔧 Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `verbose_tuning` | bool | False | Enable cache hit/miss console logging |
| `return_loss` | bool | False | Return 4-tuple with tune_info |
| `tune_mode` | str | "off" | "off", "auto", or "hybrid" |
| `tune_threshold` | int | 60 | Tune if element_count >= threshold |

---

## 📤 Return Values

### Without `return_loss`
```python
positions = engine.solve_with_constraints(elements)
# Returns: Dict[str, Tuple[float, float]]
```

### With `return_loss=True`
```python
positions, loss, components, tune_info = engine.solve_with_constraints(
    elements, 
    return_loss=True
)
# Returns: Tuple[Dict, float, Dict, Dict]
```

### tune_info Structure
```python
{
    "mode": "hybrid",         # Current tune mode
    "auto_tune": True,        # Was tuning active?
    "cache_hit": True,        # Cached weights reused?
    "cache_key": (1, 5, 4, 0), # Problem signature
    "tuned": False            # Did we tune this solve?
}
```

---

## 🎯 Common Patterns

### Pattern 1: Development with Logging
```python
engine = AdvancedLayoutEngine()
positions = engine.solve_with_constraints(
    elements,
    tune_mode="hybrid",
    verbose_tuning=True  # See cache behavior
)
```

### Pattern 2: Production with Metrics
```python
_, loss, _, tune_info = engine.solve_with_constraints(
    elements,
    tune_mode="hybrid",
    return_loss=True,
    verbose_tuning=False  # Quiet
)
logger.info(f"Cache: {tune_info['cache_hit']}, Loss: {loss:.4f}")
```

### Pattern 3: Cache Hit Rate Tracking
```python
hits = sum(1 for info in tune_infos if info['cache_hit'])
rate = hits / len(tune_infos)
print(f"Hit rate: {rate:.1%}")
```

### Pattern 4: Combine Both Features
```python
positions, loss, components, tune_info = engine.solve_with_constraints(
    elements,
    tune_mode="hybrid",
    return_loss=True,      # Get tune_info
    verbose_tuning=True    # Also log to console
)
# Console: [Tune Cache] HIT - ...
# Code: tune_info['cache_hit'] == True
```

---

## 📊 Cache Key Buckets

Cache key: `(element_bucket, density_bucket, overlap_bucket, constraint_count)`

| Element Count | Bucket | Example |
|---------------|--------|---------|
| 0-49 | 0 | 25 → 0 |
| 50-99 | 1 | 75 → 1 |
| 100-149 | 2 | 120 → 2 |
| 150-199 | 3 | 175 → 3 |

Similar element counts → Same bucket → Cache hit

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Cache miss overhead | +30-50ms (tuning) |
| Cache hit overhead | 0ms (instant) |
| Logging overhead | <1ms |
| Return tuple overhead | 0ms |

**Speedup from cache**: 1.2-1.4x for complex problems

---

## ✅ Quick Verification

```bash
cd scripts
python verify_v3_cache_features.py
```

Expected output: `✓ ALL V3.0 CACHE FEATURES VERIFIED!`

---

## 📖 Full Documentation

| Document | Purpose |
|----------|---------|
| [V3_CACHE_FEATURES.md](V3_CACHE_FEATURES.md) | Complete feature guide |
| [V3_IMPLEMENTATION_SUMMARY.md](V3_IMPLEMENTATION_SUMMARY.md) | Implementation details |
| [OVERLAP_ALGORITHM_QUICK_START.md](OVERLAP_ALGORITHM_QUICK_START.md) | Overall v3.0 guide |

---

## 🚀 Example Code

**File**: `scripts/overlap_integration_v3_examples.py`  
**Function**: `example_7_hybrid_backprop_with_cache()`

Run with:
```bash
python scripts/overlap_integration_v3_examples.py
```

---

## ❓ FAQ

**Q: Do I need both parameters?**  
A: No. Use `verbose_tuning` for console logs, `return_loss` for programmatic access. Both work independently.

**Q: What if I don't use `return_loss=True`?**  
A: tune_info still available via `engine.last_tune_info`

**Q: Does logging slow down production?**  
A: Yes, slightly (<1ms). Use `verbose_tuning=False` in production.

**Q: How do I check cache size?**  
A: `len(engine._tuned_weights_cache)`

**Q: Can I clear the cache?**  
A: `engine._tuned_weights_cache.clear()`

**Q: When does tuning trigger?**  
A: When `tune_mode != "off"` and `element_count >= tune_threshold` (default 60)

---

**Version**: v3.0  
**Status**: ✅ Production-ready  
**Date**: February 8, 2026
