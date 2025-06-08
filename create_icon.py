from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    # Create a new image with a dark background
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a circle
    circle_color = (41, 128, 185)  # Blue color
    draw.ellipse([size*0.1, size*0.1, size*0.9, size*0.9], fill=circle_color)
    
    # Add text
    try:
        font_size = int(size * 0.4)
        font = ImageFont.truetype("Arial", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "MCP"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Save the image
    image.save(output_path)

def main():
    # Create assets directory if it doesn't exist
    os.makedirs("assets", exist_ok=True)
    
    # Create Windows icon
    create_icon(256, "assets/icon.ico")
    
    # Create Mac icon
    create_icon(1024, "assets/icon.icns")

if __name__ == "__main__":
    main() 