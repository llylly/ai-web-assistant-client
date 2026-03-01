#!/usr/bin/env python3
"""
Generate Chrome Extension Icons
Creates icons with white "L" on black background in three sizes: 16x16, 48x48, 128x128
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """
    Create an icon with white "L" on black background

    Args:
        size: Icon size (width and height in pixels)
        output_path: Path to save the icon
    """
    # Create black background
    img = Image.new('RGB', (size, size), color='black')
    draw = ImageDraw.Draw(img)

    # Calculate font size (roughly 60% of icon size)
    font_size = int(size * 0.6)

    # Try to use a nice font, fall back to default if not available
    try:
        # Try common system fonts
        if os.path.exists('/System/Library/Fonts/Helvetica.ttc'):  # macOS
            font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', font_size)
        elif os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):  # Linux
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_size)
        elif os.path.exists('C:\\Windows\\Fonts\\arial.ttf'):  # Windows
            font = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Draw white "L" in center
    text = "L"

    # Get text size for centering
    try:
        # Try newer method (Pillow >= 8.0.0)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # Fall back to older method
        text_width, text_height = draw.textsize(text, font=font)

    # Calculate position to center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2

    # Draw the text
    draw.text((x, y), text, fill='white', font=font)

    # Save the icon
    img.save(output_path, 'PNG')
    print(f"✓ Created {output_path} ({size}x{size})")


def main():
    """Generate all required icon sizes"""
    # Create icons directory if it doesn't exist
    icons_dir = 'icons'
    os.makedirs(icons_dir, exist_ok=True)

    # Icon sizes required by Chrome extension
    sizes = [16, 48, 128]

    print("Generating Chrome extension icons...")
    print("Design: White 'L' on black background")
    print()

    for size in sizes:
        output_path = os.path.join(icons_dir, f'icon{size}.png')
        create_icon(size, output_path)

    print()
    print("All icons generated successfully!")
    print(f"Icons saved in: {os.path.abspath(icons_dir)}/")


if __name__ == '__main__':
    main()
