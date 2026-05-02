"""Generate system tray icon for the Desktop App."""
from pathlib import Path

from PIL import Image, ImageDraw

# Create a 64x64 icon with a microphone symbol
img = Image.new('RGB', (64, 64), color='#2C2F33')
draw = ImageDraw.Draw(img)

# Draw microphone body (rectangle)
draw.rectangle([22, 15, 42, 35], fill='#7289DA', outline='#5865F2', width=2)

# Draw microphone base (arc/circle bottom)
draw.ellipse([22, 30, 42, 45], fill='#7289DA', outline='#5865F2', width=2)

# Draw microphone stand
draw.line([32, 45, 32, 55], fill='#FFFFFF', width=3)
draw.line([25, 55, 39, 55], fill='#FFFFFF', width=3)

# Draw sound waves
draw.arc([5, 20, 15, 35], 90, 270, fill='#43B581', width=2)
draw.arc([49, 20, 59, 35], 270, 90, fill='#43B581', width=2)

# Save as ICO and PNG
output_dir = Path("assets")
output_dir.mkdir(exist_ok=True)

img.save(output_dir / 'icon.ico', format='ICO', sizes=[(64, 64)])
img.save(output_dir / 'icon.png', format='PNG')

print("✅ Icon created: assets/icon.ico and assets/icon.png")
