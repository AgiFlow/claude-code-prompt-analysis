#!/usr/bin/env python3
"""
Birthday Card GIF for Slack
Creates a festive animated birthday card with cake, candles, and celebration effects
"""

from PIL import Image, ImageDraw, ImageFont
import math
import sys
import os

# Add the skill directory to path
sys.path.insert(0, os.path.dirname(__file__))

from core.gif_builder import GIFBuilder
from core.frame_composer import create_gradient_background, draw_emoji_enhanced
from core.typography import draw_text_with_outline, TYPOGRAPHY_SCALE
from core.visual_effects import ParticleSystem
from core.easing import interpolate
from core.validators import validate_gif, is_slack_ready

def create_birthday_card_gif():
    """
    Creates an animated birthday card GIF optimized for Slack messages

    Animation phases:
    1. Fade in with birthday cake
    2. Candles light up with sparkles
    3. "HAPPY BIRTHDAY!" text appears with bounce
    4. Confetti celebration
    5. Gentle pulse to loop
    """

    # Settings for Slack message GIF (not emoji)
    WIDTH, HEIGHT = 480, 480
    FPS = 20

    builder = GIFBuilder(WIDTH, HEIGHT, FPS)

    # Color palette - festive birthday colors
    bg_gradient_top = (255, 240, 245)  # Light pink
    bg_gradient_bottom = (230, 230, 255)  # Light lavender
    text_color = (255, 68, 68)  # Bright red
    text_outline = (255, 255, 255)  # White outline

    # Particle system for effects
    particles = ParticleSystem()

    # Phase 1: Fade in with cake (frames 0-15)
    for i in range(15):
        frame = create_gradient_background(WIDTH, HEIGHT, bg_gradient_top, bg_gradient_bottom)

        # Fade in effect
        t = i / 14
        opacity = interpolate(0, 1, t, 'ease_out')

        # Draw cake emoji with increasing opacity (simulate by size)
        size = int(120 * opacity)
        if size > 0:
            cake_y = HEIGHT // 2 + 20
            draw_emoji_enhanced(frame, '🎂',
                              position=(WIDTH//2 - size//2, cake_y - size//2),
                              size=size, shadow=True)

        builder.add_frame(frame)

    # Phase 2: Candles light up with sparkles (frames 15-30)
    for i in range(15):
        frame = create_gradient_background(WIDTH, HEIGHT, bg_gradient_top, bg_gradient_bottom)

        # Draw cake at full size
        cake_y = HEIGHT // 2 + 20
        draw_emoji_enhanced(frame, '🎂',
                          position=(WIDTH//2 - 60, cake_y - 60),
                          size=120, shadow=True)

        # Add sparkles appearing around the cake
        if i > 5:
            num_sparkles = min((i - 5) * 2, 20)
            for j in range(num_sparkles):
                angle = (j / 20) * 2 * math.pi + (i * 0.3)
                radius = 100 + math.sin(i * 0.5 + j) * 15
                x = WIDTH // 2 + int(math.cos(angle) * radius)
                y = cake_y + int(math.sin(angle) * radius)

                # Draw small sparkle emoji
                sparkle_size = 20 + int(math.sin(i * 0.5 + j) * 5)
                try:
                    draw_emoji_enhanced(frame, '✨',
                                      position=(x - sparkle_size//2, y - sparkle_size//2),
                                      size=sparkle_size, shadow=False)
                except:
                    pass  # Skip if position is out of bounds

        builder.add_frame(frame)

    # Phase 3: "HAPPY BIRTHDAY!" text bounces in (frames 30-50)
    for i in range(20):
        frame = create_gradient_background(WIDTH, HEIGHT, bg_gradient_top, bg_gradient_bottom)

        # Draw cake
        cake_y = HEIGHT // 2 + 20
        draw_emoji_enhanced(frame, '🎂',
                          position=(WIDTH//2 - 60, cake_y - 60),
                          size=120, shadow=True)

        # Draw sparkles (static now)
        for j in range(20):
            angle = (j / 20) * 2 * math.pi
            radius = 100
            x = WIDTH // 2 + int(math.cos(angle) * radius)
            y = cake_y + int(math.sin(angle) * radius)

            try:
                draw_emoji_enhanced(frame, '✨',
                                  position=(x - 10, y - 10),
                                  size=20, shadow=False)
            except:
                pass

        # Text bounces in from top
        t = i / 19
        text_y = interpolate(-100, 80, t, 'bounce_out')

        if text_y > -50:  # Only draw when visible
            draw_text_with_outline(
                frame, "HAPPY",
                position=(WIDTH//2, int(text_y)),
                font_size=TYPOGRAPHY_SCALE['h1'],
                text_color=text_color,
                outline_color=text_outline,
                outline_width=4,
                centered=True
            )

            draw_text_with_outline(
                frame, "BIRTHDAY!",
                position=(WIDTH//2, int(text_y + 70)),
                font_size=TYPOGRAPHY_SCALE['h1'],
                text_color=text_color,
                outline_color=text_outline,
                outline_width=4,
                centered=True
            )

        builder.add_frame(frame)

    # Phase 4: Confetti explosion (frames 50-80)
    # Initialize confetti particles
    particles.emit_confetti(x=WIDTH//2, y=100, count=50)

    for i in range(30):
        frame = create_gradient_background(WIDTH, HEIGHT, bg_gradient_top, bg_gradient_bottom)

        # Draw cake
        cake_y = HEIGHT // 2 + 20
        draw_emoji_enhanced(frame, '🎂',
                          position=(WIDTH//2 - 60, cake_y - 60),
                          size=120, shadow=True)

        # Draw sparkles
        for j in range(20):
            angle = (j / 20) * 2 * math.pi
            radius = 100
            x = WIDTH // 2 + int(math.cos(angle) * radius)
            y = cake_y + int(math.sin(angle) * radius)

            try:
                draw_emoji_enhanced(frame, '✨',
                                  position=(x - 10, y - 10),
                                  size=20, shadow=False)
            except:
                pass

        # Draw text
        draw_text_with_outline(
            frame, "HAPPY",
            position=(WIDTH//2, 80),
            font_size=TYPOGRAPHY_SCALE['h1'],
            text_color=text_color,
            outline_color=text_outline,
            outline_width=4,
            centered=True
        )

        draw_text_with_outline(
            frame, "BIRTHDAY!",
            position=(WIDTH//2, 150),
            font_size=TYPOGRAPHY_SCALE['h1'],
            text_color=text_color,
            outline_color=text_outline,
            outline_width=4,
            centered=True
        )

        # Update and render particles
        particles.update()
        particles.render(frame)

        # Add some balloon emojis floating up
        if i < 20:
            balloon_y = HEIGHT - (i * 30)
            if balloon_y < HEIGHT:
                draw_emoji_enhanced(frame, '🎈',
                                  position=(WIDTH//4 - 20, balloon_y),
                                  size=40, shadow=False)
                draw_emoji_enhanced(frame, '🎉',
                                  position=(3*WIDTH//4 - 20, balloon_y - 30),
                                  size=40, shadow=False)

        builder.add_frame(frame)

    # Phase 5: Gentle pulse to loop (frames 80-100)
    for i in range(20):
        frame = create_gradient_background(WIDTH, HEIGHT, bg_gradient_top, bg_gradient_bottom)

        # Pulsing cake
        pulse = 1.0 + math.sin(i * 0.3) * 0.1
        cake_size = int(120 * pulse)
        cake_y = HEIGHT // 2 + 20
        draw_emoji_enhanced(frame, '🎂',
                          position=(WIDTH//2 - cake_size//2, cake_y - cake_size//2),
                          size=cake_size, shadow=True)

        # Draw sparkles with gentle twinkle
        for j in range(20):
            angle = (j / 20) * 2 * math.pi + (i * 0.1)
            radius = 100
            x = WIDTH // 2 + int(math.cos(angle) * radius)
            y = cake_y + int(math.sin(angle) * radius)

            sparkle_size = 20 + int(math.sin(i * 0.3 + j * 0.5) * 3)
            try:
                draw_emoji_enhanced(frame, '✨',
                                  position=(x - sparkle_size//2, y - sparkle_size//2),
                                  size=sparkle_size, shadow=False)
            except:
                pass

        # Draw text with slight pulse
        text_scale = 1.0 + math.sin(i * 0.3) * 0.05
        font_size = int(TYPOGRAPHY_SCALE['h1'] * text_scale)

        draw_text_with_outline(
            frame, "HAPPY",
            position=(WIDTH//2, 80),
            font_size=font_size,
            text_color=text_color,
            outline_color=text_outline,
            outline_width=4,
            centered=True
        )

        draw_text_with_outline(
            frame, "BIRTHDAY!",
            position=(WIDTH//2, 150),
            font_size=font_size,
            text_color=text_color,
            outline_color=text_outline,
            outline_width=4,
            centered=True
        )

        # Add static party emojis in corners
        draw_emoji_enhanced(frame, '🎈', position=(30, HEIGHT - 60), size=40, shadow=False)
        draw_emoji_enhanced(frame, '🎉', position=(WIDTH - 70, HEIGHT - 60), size=40, shadow=False)
        draw_emoji_enhanced(frame, '🎁', position=(30, 30), size=40, shadow=False)
        draw_emoji_enhanced(frame, '🎊', position=(WIDTH - 70, 30), size=40, shadow=False)

        builder.add_frame(frame)

    # Save the GIF
    output_path = 'birthday_card.gif'
    info = builder.save(output_path, num_colors=128, optimize_for_emoji=False)

    print(f"\n🎂 Birthday Card GIF Created! 🎂")
    print(f"File: {output_path}")
    print(f"Size: {info['size_kb']:.1f} KB ({info['size_mb']:.2f} MB)")
    print(f"Frames: {info['frame_count']}")
    print(f"Duration: {info['duration_seconds']:.1f}s")

    # Validate for Slack
    print("\n📊 Slack Validation:")
    if is_slack_ready(output_path, is_emoji=False):
        print("✅ Ready to send on Slack!")
    else:
        all_pass, results = validate_gif(output_path, is_emoji=False)
        print("⚠️  Some optimizations may be needed:")
        for check, result in results.items():
            status = "✅" if result['pass'] else "❌"
            print(f"  {status} {check}: {result['message']}")

    return output_path

if __name__ == "__main__":
    create_birthday_card_gif()
