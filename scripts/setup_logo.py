#!/usr/bin/env python3
"""
Helper script to generate or setup the Phiversity logo for watermarking.
Run this script to create a basic logo if you don't have one yet.
"""

from pathlib import Path

def generate_phiversity_logo(output_path: Path):
    """Generate a simple Phiversity logo using PIL."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("ERROR: PIL not installed. Install with: pip install Pillow")
        return False
    
    # Create image with transparent background
    size = (300, 300)
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw circular border
    border_width = 8
    draw.ellipse(
        [(border_width, border_width), 
         (size[0]-border_width, size[1]-border_width)],
        outline=(0, 0, 0, 255),
        width=border_width
    )
    
    # Draw inner circle border
    inner_border = border_width + 4
    draw.ellipse(
        [(inner_border, inner_border), 
         (size[0]-inner_border, size[1]-inner_border)],
        outline=(0, 0, 0, 200),
        width=3
    )
    
    # Try to add text
    try:
        # Try to use default font, fallback to basic font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Draw "∫" symbol (integral)
    draw.text((85, 70), "∫", fill=(0, 0, 0, 255), font=font)
    
    # Draw "dy/dx"
    try:
        small_font = ImageFont.truetype("arial.ttf", 16)
    except:
        small_font = font
    
    draw.text((140, 100), "dy", fill=(0, 0, 0, 255), font=small_font)
    draw.text((145, 120), "dx", fill=(0, 0, 0, 255), font=small_font)
    
    # Draw underline under dy
    draw.line([(140, 110), (165, 110)], fill=(0, 0, 0, 255), width=2)
    
    # Draw "Phiversity" text at bottom
    try:
        text_font = ImageFont.truetype("arial.ttf", 20)
    except:
        text_font = small_font
    
    draw.text((60, 225), "Phiversity", fill=(0, 0, 0, 255), font=text_font)
    
    # Save image
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    print(f"✓ Logo generated: {output_path}")
    return True


def setup_logo():
    """Setup the logo for watermarking."""
    root = Path(__file__).resolve().parents[1]
    logo_path = root / "media" / "assets" / "logo.png"
    
    # Create directory
    logo_path.parent.mkdir(parents=True, exist_ok=True)
    
    if logo_path.exists():
        print(f"Logo already exists at: {logo_path}")
        return True
    
    print("Generating Phiversity logo...")
    try:
        if generate_phiversity_logo(logo_path):
            print(f"\n✅ Logo setup complete!")
            print(f"Logo saved to: {logo_path}")
            print("\nThe logo will now be automatically added to all generated videos:")
            print("  - Position: Bottom-right corner")
            print("  - Size: ~10% of video width")
            print("  - Opacity: 80%")
            return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    return False


if __name__ == "__main__":
    setup_logo()
