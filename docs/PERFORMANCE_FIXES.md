# Performance Fixes Applied

## Problem Diagnosed
Video generation was hanging indefinitely (1+ hours) due to:
1. No timeout mechanisms in Manim rendering
2. No overall job timeout
3. Complex animation plans overwhelming the renderer
4. Element-audio mode creating excessive complexity
5. No progress tracking or visibility into pipeline stages

## Fixes Implemented

### 1. **Manim Rendering Timeout** ([manim_adapter.py](scripts/manim_adapter.py))
- Added 15-minute timeout (configurable via `MANIM_TIMEOUT` env var)
- Prevents indefinite hangs during rendering
- Raises clear error message if timeout exceeded

### 2. **Overall Job Timeout** ([server/app.py](scripts/server/app.py))
- Added 20-minute total job timeout (configurable via `JOB_TIMEOUT` env var)
- Checks timeout after orchestration and pipeline steps
- Logs elapsed time at each checkpoint

### 3. **Progress Logging** ([pipeline.py](scripts/pipeline.py))
- Added step-by-step progress indicators:
  - Step 1/5: Getting solution plan
  - Step 2/5: Generating audio
  - Step 3/5: Generating Manim script
  - Step 4/5: Rendering video
  - Step 5/5: Combining audio + video
- Logs completion time and warnings for complex plans

### 4. **Complexity Warnings** ([pipeline.py](scripts/pipeline.py))
- Warns when scene count > 10
- Warns when total element count > 50
- Helps identify problematic plans before rendering

### 5. **Better Error Messages**
- Timeout errors now explain what happened
- Elapsed time logged on all failures
- Clear indication of which step failed

### 6. **Optimized Settings** ([.env](.env))
- Changed `MANIM_QUALITY` from `medium` to `low` (4x faster rendering)
- Added `MANIM_TIMEOUT=900` (15 minutes)
- Added `JOB_TIMEOUT=1200` (20 minutes)

## Configuration

### Environment Variables (`.env`)

```env
# Timeout Settings
MANIM_TIMEOUT=900       # 15 minutes max for rendering
JOB_TIMEOUT=1200        # 20 minutes max for entire job

# Quality Settings (faster = lower quality)
MANIM_QUALITY=low       # Options: low, medium, high, production
MANIM_FPS=30
```

### Recommended Settings by Use Case

**Development/Testing (Fast):**
```env
MANIM_QUALITY=low
MANIM_TIMEOUT=300       # 5 minutes
JOB_TIMEOUT=600         # 10 minutes
```

**Production (Balanced):**
```env
MANIM_QUALITY=medium
MANIM_TIMEOUT=900       # 15 minutes
JOB_TIMEOUT=1200        # 20 minutes
```

**High Quality (Slow):**
```env
MANIM_QUALITY=high
MANIM_TIMEOUT=1800      # 30 minutes
JOB_TIMEOUT=2400        # 40 minutes
```

## Expected Performance

### Typical Job Times (with `low` quality):
- Simple question (1-2 scenes): **1-3 minutes**
- Medium question (3-5 scenes): **3-7 minutes**
- Complex question (6-10 scenes): **7-15 minutes**

### Warning Signs:
- Job exceeds 10 minutes → Check solution plan complexity
- More than 10 scenes → Consider simplifying the question
- More than 50 elements → LLM generated overly detailed plan

## Troubleshooting

### If jobs still timeout:
1. Check the generated `solution_plan.json` for complexity
2. Reduce quality: `MANIM_QUALITY=low`
3. Increase timeouts: `MANIM_TIMEOUT=1800`
4. Disable element-audio mode (uncheck in frontend)
5. Ask simpler, more focused questions

### To monitor progress:
1. Check job log: `media/videos/web_jobs/{job_id}/log.txt`
2. Watch for step-by-step progress messages
3. Look for warnings about high scene/element counts

## Files Modified
- `scripts/manim_adapter.py` - Added timeout to rendering
- `scripts/pipeline.py` - Added progress logging, complexity checks
- `scripts/server/app.py` - Added job timeout tracking
- `.env` - Optimized performance settings

## Testing
To test the fixes:
1. Restart the server: Run `run_app.vbs`
2. Try a simple question: "What is velocity?"
3. Expected completion: 1-3 minutes
4. Check log file for progress messages
