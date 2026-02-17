# Logo Watermark Feature Setup

## Overview
Every generated video now automatically gets the Phiversity logo watermarked in the **bottom-right corner** with 80% opacity.

## Setup Instructions

### 1. Save the Logo Image
The logo image file should be saved as `media/assets/logo.png`

**Save the provided Phiversity logo image to:**
```
c:\Users\user\Downloads\Phiversity-main\media\assets\logo.png
```

### 2. Logo Requirements
- **Format**: PNG (recommended for transparency support)
- **Transparency**: Supported (alpha channel)
- **Recommended Size**: 200x200px or larger (will be automatically scaled)
- **Aspect Ratio**: Square (1:1) works best, but any aspect ratio is supported

### 3. How It Works
- Logo is automatically scaled to 10% of video width (max 150px)
- Positioned 10px from bottom-right corner
- 80% opacity (slight transparency) to avoid obscuring content
- Gracefully skips watermarking if logo file not found

### 4. Configuration
You can customize the watermark in your code:

```python
# In scripts/pipeline.py, customize these parameters:
add_logo_watermark(
    final_path, 
    watermarked_path,
    logo_path=Path("media/assets/logo.png"),  # Custom path
    margin=10,                                 # Pixels from corner
    opacity=0.8                                # 0.0 (transparent) to 1.0 (opaque)
)
```

## Integration

The logo watermark is automatically applied to:
- ✅ Voice-first with element-wise audio pipeline
- ✅ Voice-first with scene-wise audio pipeline  
- ✅ Video-first pipeline
- ✅ All videos with intro prepending
- ✅ All cloud-uploaded videos

## Troubleshooting

**Logo not appearing?**
- Verify `media/assets/logo.png` exists
- Check file format (should be PNG)
- Check file permissions

**Logo too large/small?**
- Modify the `max_logo_width` calculation in `scripts/av_sync.py` line ~168
- Default: 10% of video width, max 150px

**Logo quality issues?**
- Use a high-resolution PNG source (1024x1024px or larger)
- Avoid heavily compressed JPG files

## Disabling Watermark (Optional)

To disable watermarking temporarily, comment out in `scripts/pipeline.py`:

```python
# add_logo_watermark(final_path, watermarked_path)
# shutil.move(str(watermarked_path), str(final_path))
```
