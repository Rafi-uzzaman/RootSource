#!/usr/bin/env python3
"""
Generate social preview image for RootSource AI
This script creates a 1200x630 PNG image for social media sharing
"""

import os
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

def create_social_preview():
    # Create image with the right dimensions
    width, height = 1200, 630
    
    # Create gradient background
    image = Image.new('RGB', (width, height), color='#2ecc71')
    draw = ImageDraw.Draw(image)
    
    # Create gradient effect
    for y in range(height):
        r = int(46 + (30 - 46) * y / height)
        g = int(204 + (174 - 204) * y / height)
        b = int(113 + (73 - 113) * y / height)
        color = f'#{r:02x}{g:02x}{b:02x}'
        draw.line([(0, y), (width, y)], fill=color)
    
    try:
        # Try to use custom fonts
        title_font = ImageFont.truetype("arial.ttf", 64)
        subtitle_font = ImageFont.truetype("arial.ttf", 32)
        feature_font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 20)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        feature_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Add logo circle
    logo_x, logo_y = 80, 100
    logo_size = 100
    draw.ellipse([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], 
                 fill='white', outline='#27ae60', width=3)
    
    # Add emoji logo (simplified as text)
    draw.text((logo_x + logo_size//2, logo_y + logo_size//2), '🌱', 
              font=title_font, fill='#2ecc71', anchor='mm')
    
    # Add title
    title_text = "RootSource AI"
    title_x = logo_x + logo_size + 30
    title_y = logo_y + 10
    draw.text((title_x, title_y), title_text, font=title_font, fill='white')
    
    # Add subtitle
    subtitle_text = "Revolutionizing Agriculture Through AI"
    subtitle_y = title_y + 80
    draw.text((title_x, subtitle_y), subtitle_text, font=subtitle_font, fill='white')
    
    # Add features
    features = [
        "🤖 AI-Powered Expert Advice",
        "🎙️ Voice-First Interface", 
        "🌍 40+ Languages Support",
        "⚡ Real-time Research"
    ]
    
    feature_y = subtitle_y + 60
    for i, feature in enumerate(features):
        y_pos = feature_y + (i * 35)
        draw.text((title_x, y_pos), feature, font=feature_font, fill='white')
    
    # Add tech stack
    tech_text = "Built with: FastAPI • Python • LangChain • OpenAI"
    tech_y = feature_y + len(features) * 35 + 30
    draw.text((title_x, tech_y), tech_text, font=small_font, fill='#e8f5e8')
    
    # Add right side dashboard mockup (simplified rectangle)
    dashboard_x = width - 350 - 50
    dashboard_y = 80
    dashboard_w = 300
    dashboard_h = 400
    
    # Dashboard background
    draw.rounded_rectangle([dashboard_x, dashboard_y, 
                           dashboard_x + dashboard_w, dashboard_y + dashboard_h],
                          radius=20, fill='white', outline='#ddd', width=2)
    
    # Dashboard header
    header_text = "Agricultural AI Assistant"
    draw.text((dashboard_x + dashboard_w//2, dashboard_y + 30), 
              header_text, font=feature_font, fill='#2ecc71', anchor='mt')
    
    # Chat bubbles (simplified)
    bubble_y = dashboard_y + 80
    
    # User message
    draw.rounded_rectangle([dashboard_x + 100, bubble_y, 
                           dashboard_x + dashboard_w - 20, bubble_y + 30],
                          radius=15, fill='#2ecc71')
    draw.text((dashboard_x + 110, bubble_y + 5), 
              "How can I improve corn yield?", 
              font=small_font, fill='white')
    
    # AI response
    bubble_y += 50
    draw.rounded_rectangle([dashboard_x + 20, bubble_y, 
                           dashboard_x + 250, bubble_y + 60],
                          radius=15, fill='#f8f9fa', outline='#ddd')
    draw.text((dashboard_x + 30, bubble_y + 5), 
              "Based on research, key strategies\ninclude soil nutrition, planting\ndensity, and irrigation...", 
              font=small_font, fill='#2c3e50')
    
    # Input area
    input_y = dashboard_y + dashboard_h - 60
    draw.rounded_rectangle([dashboard_x + 20, input_y, 
                           dashboard_x + dashboard_w - 20, input_y + 40],
                          radius=20, fill='#f8f9fa', outline='#ddd')
    
    # Voice button
    draw.ellipse([dashboard_x + 30, input_y + 5, 
                  dashboard_x + 65, input_y + 35], 
                 fill='#2ecc71')
    draw.text((dashboard_x + 47, input_y + 20), '🎙️', 
              font=small_font, fill='white', anchor='mm')
    
    # Input placeholder
    draw.text((dashboard_x + 80, input_y + 20), 
              "Ask about farming, crops, soil...", 
              font=small_font, fill='#7f8c8d', anchor='lm')
    
    return image

def save_social_preview():
    """Generate and save the social preview image"""
    try:
        image = create_social_preview()
        
        # Save to assets directory
        assets_dir = "assets"
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
        
        output_path = os.path.join(assets_dir, "social-preview.png")
        image.save(output_path, "PNG", quality=95, optimize=True)
        
        print(f"✅ Social preview image saved to: {output_path}")
        print(f"📏 Image dimensions: {image.size[0]}x{image.size[1]}")
        print(f"💾 File size: {os.path.getsize(output_path) / 1024:.1f} KB")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error generating social preview: {e}")
        return None

if __name__ == "__main__":
    print("🎨 Generating RootSource AI social preview image...")
    save_social_preview()