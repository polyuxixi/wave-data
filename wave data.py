import pygame
import cv2
import numpy as np
import csv
from datetime import datetime

# --- CONFIG ---
WIDTH, HEIGHT = 1920, 1920
FPS = 30
CSV_FILE = 'open-meteo-54.54N10.21E0m.csv'

# --- DATA LOADING ---
def load_wave_data(csv_file):
    data = []
    with open(csv_file, newline='') as f:
        lines = [line for line in f if line.strip() and not line.startswith('latitude') and not line.startswith('time,')]
        reader = csv.DictReader(lines, fieldnames=["time","wave_height (m)","wave_direction (°)","wave_period (s)","ocean_current_velocity (m/s)"])
        for row in reader:
            if row['time'] == 'time':
                continue
            try:
                data.append({
                    'time': row['time'],
                    'wave_height': float(row['wave_height (m)']),
                    'wave_direction': float(row['wave_direction (°)']),
                    'wave_period': float(row['wave_period (s)']),
                    'current_speed': float(row['ocean_current_velocity (m/s)'])
                })
            except Exception:
                continue
    return data

# --- BACKGROUND FUNCTIONS ---
def draw_deep_sea_background(surface, params, t):
    """Draw animated wave-shaped deep sea background with depth gradient"""
    wave_height, wave_direction, wave_period, current_speed = params
    width, height = surface.get_size()
    
    # Create gradient from extremely dark deep blue (bottom) to very dark blue-green (top)
    for y in range(height):
        depth_factor = y / height  # 0 at top, 1 at bottom
        # Ultra dark ocean colors: nearly black at bottom, very minimal blue toward surface
        r = int(1 + depth_factor * 4)       # Almost no red component
        g = int(3 + depth_factor * 8)       # Minimal dark blue-green
        b = int(8 + depth_factor * 20)      # Very dark blue base
        
        # Add minimal wave-influenced color variation
        wave_influence = 0.02 * np.sin(y * 0.01 + t / (50 / max(0.5, wave_period)))
        r = max(0, min(255, int(r + wave_influence * 2)))
        g = max(0, min(255, int(g + wave_influence * 3)))
        b = max(0, min(255, int(b + wave_influence * 5)))
        
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    
    # Draw multiple wave layers for depth effect - extremely subtle
    wave_layers = [
        {'amplitude': 15 + wave_height * 8, 'frequency': 0.003, 'speed': 0.8, 'alpha': 15, 'y_offset': height * 0.7},
        {'amplitude': 12 + wave_height * 6, 'frequency': 0.005, 'speed': 1.2, 'alpha': 10, 'y_offset': height * 0.8},
        {'amplitude': 8 + wave_height * 4, 'frequency': 0.008, 'speed': 1.6, 'alpha': 8, 'y_offset': height * 0.9}
    ]
    
    for layer in wave_layers:
        wave_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        points = []
        
        # Generate wave points
        for x in range(0, width + 10, 5):
            wave_y = layer['y_offset'] + layer['amplitude'] * np.sin(
                x * layer['frequency'] + t * layer['speed'] / (30 / max(0.5, wave_period))
            )
            # Add some secondary harmonics for more natural waves
            wave_y += layer['amplitude'] * 0.3 * np.sin(
                x * layer['frequency'] * 2.3 + t * layer['speed'] * 0.7 / (30 / max(0.5, wave_period))
            )
            points.append((x, int(wave_y)))
        
        # Draw wave as filled polygon
        if len(points) > 2:
            # Complete the polygon to bottom of screen
            wave_points = points + [(width, height), (0, height)]
            
            # Wave color - barely perceptible difference from background
            wave_color = (r + 3, g + 5, b + 8, layer['alpha'])
            
            # Create a temporary surface to draw the wave with alpha
            temp_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surf, wave_color, wave_points)
            surface.blit(temp_surf, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # Add deep sea atmospheric details
    add_deep_sea_details(surface, params, t)

def add_deep_sea_details(surface, params, t):
    """Add atmospheric details like particles, distant lights, and subtle textures"""
    wave_height, wave_direction, wave_period, current_speed = params
    width, height = surface.get_size()
    
    # Marine snow (small particles falling slowly) - MAXIMUM INTENSITY
    np.random.seed(int(t) % 1000)  # Deterministic but changing particles
    for i in range(250 + int(wave_height * 80)):  # Much more particles
        x = np.random.randint(0, width)
        y_base = np.random.randint(0, height)
        # Particle drift with current and time
        drift = current_speed * 40 * np.sin(t * 0.02 + i * 0.1)  # Much stronger drift
        y = (y_base + t * (1.2 + current_speed * 0.8) + drift) % height  # Faster fall
        
        # Particle size and brightness vary - MUCH BRIGHTER
        size = np.random.choice([1, 1, 2, 3, 4, 5], p=[0.4, 0.2, 0.15, 0.1, 0.1, 0.05])
        brightness = int(40 + np.random.randint(0, 60))  # Much increased brightness
        alpha = int(80 + np.random.randint(0, 80))  # Much more visible
        
        # Brighter blue-white particles
        color = (brightness, brightness + 12, brightness + 20, alpha)
        if size == 1:
            surface.set_at((int(x), int(y)), color[:3])
        else:
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, color, (size, size), size)
            surface.blit(temp_surf, (int(x)-size, int(y)-size), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # Distant bioluminescent points (like distant creatures) - MAXIMUM INTENSITY
    np.random.seed(42)  # Fixed positions but varying intensity
    for i in range(75):  # Many more bioluminescent points
        x = np.random.randint(width//8, 7*width//8)  # Wider spread
        y = np.random.randint(height//6, height)  # More coverage
        
        # Pulsing intensity based on time - MUCH STRONGER
        pulse = 0.4 + 0.8 * np.sin(t * 0.12 + i * 0.8)  # More dramatic pulsing
        intensity = int(pulse * (50 + np.random.randint(0, 40)))  # Much brighter
        
        # Different colors for variety - MUCH MORE VIVID
        colors = [
            (intensity, intensity + 15, intensity + 35),   # Very bright blue
            (intensity + 15, intensity, intensity + 30),   # Bright purple
            (intensity + 10, intensity + 25, intensity + 12), # Bright green
            (intensity + 20, intensity + 8, intensity + 8), # Bright red (rare deep sea creature)
            (intensity + 8, intensity + 18, intensity + 25), # Cyan
            (intensity + 15, intensity + 12, intensity), # Magenta
        ]
        color = colors[i % len(colors)]
        
        # Soft glow effect - MUCH LARGER
        glow_size = 6 + int(pulse * 5)
        temp_surf = pygame.Surface((glow_size*8, glow_size*8), pygame.SRCALPHA)
        for r in range(glow_size, 0, -1):
            alpha = int(intensity * (r / glow_size) * 0.8)  # Much stronger glow
            # Ensure color values are valid (0-255)
            final_color = (
                max(0, min(255, color[0])),
                max(0, min(255, color[1])),
                max(0, min(255, color[2])),
                max(0, min(255, alpha))
            )
            pygame.draw.circle(temp_surf, final_color, (glow_size*4, glow_size*4), r)
        surface.blit(temp_surf, (x-glow_size*4, y-glow_size*4), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # Subtle light rays from above (like filtered sunlight) - MAXIMUM INTENSITY
    for i in range(15):  # Many more rays
        ray_x = width * (0.05 + i * 0.07) + 80 * np.sin(t * 0.02 + i)  # Much more movement
        ray_width = 5 + int(wave_height * 2.5)  # Much wider rays
        ray_alpha = int(25 + 15 * np.sin(t * 0.06 + i * 0.5))  # Much brighter
        
        # Vertical gradient ray
        for y in range(0, 2*height//3):  # Extend deeper
            fade = 1 - (y / (2*height//3))
            alpha = int(ray_alpha * fade * fade)  # Quadratic fade
            if alpha > 0:
                ray_color = (alpha//2 + 5, alpha//2 + 8, alpha + 15, alpha)
                temp_surf = pygame.Surface((ray_width*2, 1), pygame.SRCALPHA)
                pygame.draw.rect(temp_surf, ray_color, (0, 0, ray_width*2, 1))
                surface.blit(temp_surf, (int(ray_x)-ray_width, y), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # KELP FOREST SHADOWS - NEW FEATURE
    add_kelp_shadows(surface, t, width, height)
    
    # HYDROTHERMAL VENTS - NEW FEATURE
    add_hydrothermal_vents(surface, params, t, width, height)
    
    # Ocean floor suggestions (very bottom) - ENHANCED INTENSITY
    if height > 100:
        floor_y = height - 30
        for x in range(0, width, 4):  # More frequent sediment
            floor_variation = 8 * np.sin(x * 0.02 + t * 0.01)  # More variation
            y_pos = floor_y + floor_variation
            
            # Enhanced sediment particles
            sediment_alpha = int(25 + 15 * np.sin(x * 0.05 + t * 0.02))  # Brighter
            color = (sediment_alpha//2, sediment_alpha//1.5, sediment_alpha + 5, sediment_alpha)
            
            temp_surf = pygame.Surface((6, 3), pygame.SRCALPHA)  # Larger particles
            pygame.draw.rect(temp_surf, color, (0, 0, 6, 3))
            surface.blit(temp_surf, (x, int(y_pos)), special_flags=pygame.BLEND_ALPHA_SDL2)
            
            # Add occasional larger debris
            if x % 40 == 0:
                debris_size = np.random.randint(3, 8)
                debris_alpha = int(20 + np.random.randint(0, 20))
                debris_color = (debris_alpha//3, debris_alpha//2, debris_alpha//1.5, debris_alpha)
                temp_surf = pygame.Surface((debris_size*2, debris_size), pygame.SRCALPHA)
                pygame.draw.ellipse(temp_surf, debris_color, (0, 0, debris_size*2, debris_size))
                surface.blit(temp_surf, (x, int(y_pos)-debris_size//2), special_flags=pygame.BLEND_ALPHA_SDL2)

def add_kelp_shadows(surface, t, width, height):
    """Add towering kelp forest shadows in the distance"""
    np.random.seed(123)  # Fixed kelp positions
    
    for i in range(20):  # Many more kelp fronds
        # Kelp base position
        base_x = np.random.randint(width//10, 9*width//10)
        base_y = height - np.random.randint(10, 80)
        
        # Kelp height and sway - MUCH MORE DRAMATIC
        kelp_height = np.random.randint(height//2, 4*height//5)  # Taller kelp
        sway_amplitude = 25 + np.random.randint(0, 20)  # More sway
        sway_freq = 0.015 + np.random.random() * 0.02  # More varied movement
        
        # Draw kelp frond as series of segments
        segments = 35  # More detailed segments
        for seg in range(segments):
            seg_frac = seg / segments
            
            # Calculate position with sway
            sway_x = sway_amplitude * np.sin(t * sway_freq + seg_frac * 4 + i * 0.7)
            x = base_x + sway_x * seg_frac * seg_frac  # Quadratic sway increase
            y = base_y - kelp_height * seg_frac
            
            # Kelp shadow properties - MORE VISIBLE
            segment_width = int(4 + 3 * (1 - seg_frac))  # Wider kelp
            alpha = int(40 + 25 * (1 - seg_frac))  # Much more opaque
            
            # Dark green-brown kelp color - MORE INTENSE
            kelp_color = (alpha//3, alpha//1.5, alpha//4, alpha)
            
            # Draw kelp segment
            if seg > 0:
                prev_x = base_x + sway_amplitude * np.sin(t * sway_freq + (seg-1)/segments * 4 + i * 0.7) * ((seg-1)/segments)**2
                prev_y = base_y - kelp_height * (seg-1)/segments
                
                # Draw connecting line with more presence
                line_length = int(np.sqrt((x-prev_x)**2 + (y-prev_y)**2))
                if line_length > 0:
                    temp_surf = pygame.Surface((line_length + segment_width*2, segment_width*2), pygame.SRCALPHA)
                    pygame.draw.line(temp_surf, kelp_color, (segment_width, segment_width), 
                                   (int(x-prev_x)+segment_width, int(y-prev_y)+segment_width), segment_width)
                    surface.blit(temp_surf, (min(int(prev_x), int(x))-segment_width, 
                                           min(int(prev_y), int(y))-segment_width), special_flags=pygame.BLEND_ALPHA_SDL2)

def add_hydrothermal_vents(surface, params, t, width, height):
    """Add hydrothermal vents with heat shimmer and mineral particles"""
    wave_height, wave_direction, wave_period, current_speed = params
    np.random.seed(456)  # Fixed vent positions
    
    # Multiple hydrothermal vents along the bottom - MORE VENTS
    for vent_id in range(5):  # More vents
        vent_x = width * (0.1 + vent_id * 0.2) + 30 * np.sin(t * 0.015 + vent_id)
        vent_y = height - 15
        
        # Vent activity level (pulsing) - MORE DRAMATIC
        activity = 0.7 + 0.5 * np.sin(t * 0.08 + vent_id * 1.5)
        
        # Heat plume particles - MANY MORE PARTICLES
        for particle in range(int(30 + activity * 40)):
            # Particle rise with turbulence
            particle_age = (t + particle * 8 + vent_id * 100) % 300  # Longer lived particles
            rise_height = particle_age * (3 + activity * 1.5)  # Rise higher
            
            # Turbulent horizontal drift - MORE TURBULENT
            drift_x = 15 * np.sin(particle_age * 0.15 + particle * 0.4)
            drift_x += current_speed * 20 * np.sin(particle_age * 0.08)
            
            px = vent_x + drift_x
            py = vent_y - rise_height
            
            if py > height//3:  # Show more particles (upper third instead of half)
                # Particle properties based on age and activity - LARGER, BRIGHTER
                size = max(1, int(5 * activity * (1 - particle_age/300)))
                heat_intensity = int(activity * 70 * (1 - particle_age/300))  # Much brighter
                
                # Heat colors: red-orange at source, fading to blue - MORE VIVID
                age_factor = particle_age / 300
                if age_factor < 0.3:
                    # Hot: bright red-orange
                    color = (heat_intensity + 40, heat_intensity//1.5 + 20, heat_intensity//3, heat_intensity)
                elif age_factor < 0.7:
                    # Warm: bright orange-yellow
                    color = (heat_intensity + 20, heat_intensity + 10, heat_intensity//2, heat_intensity)
                else:
                    # Cool: bright blue-white (minerals)
                    color = (heat_intensity//2, heat_intensity//1.5, heat_intensity + 15, heat_intensity)
                
                # Draw heat particle with enhanced visibility
                if size > 1:
                    temp_surf = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surf, color, (size*3//2, size*3//2), size)
                    # Add glow effect for larger particles
                    if size > 2:
                        glow_color = (color[0]//2, color[1]//2, color[2]//2, color[3]//2)
                        pygame.draw.circle(temp_surf, glow_color, (size*3//2, size*3//2), size*2)
                    surface.blit(temp_surf, (int(px)-size*3//2, int(py)-size*3//2), special_flags=pygame.BLEND_ALPHA_SDL2)
                else:
                    surface.set_at((int(px), int(py)), color[:3])
        
        # Vent glow at base - MUCH MORE DRAMATIC
        glow_intensity = int(activity * 100)  # Much brighter base glow
        glow_size = int(12 + activity * 8)  # Larger glow
        for r in range(glow_size, 0, -1):
            alpha = int(glow_intensity * (r / glow_size) * 0.6)
            glow_color = (alpha + 25, alpha//1.5, alpha//3, alpha)
            temp_surf = pygame.Surface((r*6, r*3), pygame.SRCALPHA)  # Wider glow
            pygame.draw.ellipse(temp_surf, glow_color, (0, 0, r*6, r*3))
            surface.blit(temp_surf, (int(vent_x)-r*3, int(vent_y)-r), special_flags=pygame.BLEND_ALPHA_SDL2)

# --- VISUALIZATION ---
def draw_creature(surface, center, params, t):
    # Draw deep sea background first
    draw_deep_sea_background(surface, params, t)
    
    # Extract params for creature animation
    wave_height, wave_direction, wave_period, current_speed = params
    # Wave-influenced motion parameters
    # Normalize current_speed into a moderate [0.5, 2.0] scale for animation speed adjustments
    speed_factor = 0.5 + min(1.5, max(0.0, current_speed * 1.2))  # tune multiplier as needed
    # Direction lean vector (unit) derived from wave_direction (degrees, assume 0° = east, 90° = north?)
    # Adjust orientation if different; here we assume mathematical orientation with cos for x, sin for y.
    wave_rad = np.deg2rad(wave_direction)
    dir_vx = np.cos(wave_rad)
    dir_vy = np.sin(wave_rad)
    # Lean magnitudes: trunk subtle, tentacles more pronounced
    trunk_lean_amp = 25 * (0.3 + min(1.0, current_speed * 2.0))
    tentacle_lean_amp = 60 * (0.3 + min(1.0, current_speed * 2.0))
    
    # Umbrella parameters (centered, smaller, with margin)
    margin_x = int(surface.get_width() * 0.23)
    margin_y = int(surface.get_height() * 0.19)
    # Move jellyfish lower in the image
    # Make the jellyfish float up/down and left/right (swimming motion)
    swim_amp_x = int(surface.get_width() * 0.025)
    swim_amp_y = int(surface.get_height() * 0.025)
    swim_x = int(swim_amp_x * np.sin(t/90.0))
    swim_y = int(swim_amp_y * np.cos(t/120.0))
    bell_center = (surface.get_width()//2 + swim_x, margin_y + int(surface.get_height()*0.23) + swim_y)
    bell_radius_x = int(surface.get_width() * 0.12)
    bell_radius_y = int(surface.get_height() * 0.06)
    # Add glowing white radial lines to the umbrella for a luminous effect
    n_spokes = 18
    glow_layers = 3
    dot_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for g in range(glow_layers):
        glow_alpha = int(120 / (g+1))
        glow_width = 6 - 2*g
        for s in range(n_spokes):
            spoke_angle = -np.pi * (s / n_spokes)
            # Spoke length: from center to edge, modulated by breathing
            spoke_rx = bell_radius_x * (1.0 - 0.08*g)
            spoke_ry = bell_radius_y * (1.0 - 0.08*g)
            x1 = bell_center[0]
            y1 = bell_center[1]
            x2 = bell_center[0] + spoke_rx * np.cos(spoke_angle)
            y2 = bell_center[1] + spoke_ry * np.sin(spoke_angle)
            # Only draw upper hemisphere (umbrella)
            if y2 < bell_center[1]:
                pygame.draw.aaline(dot_surf, (255,255,255,glow_alpha), (x1, y1), (x2, y2))
    # Params: wave_height, wave_direction, wave_period, current_speed
    wave_height, wave_direction, wave_period, current_speed = params
    # --- Jellyfish body ---
    # --- Dot cloud jellyfish ---
    dot_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    # Umbrella parameters (centered, smaller, with margin)
    margin_x = int(surface.get_width() * 0.23)
    margin_y = int(surface.get_height() * 0.19)
    # Move jellyfish lower in the image
    bell_center = (surface.get_width()//2, margin_y + int(surface.get_height()*0.23))
    bell_radius_x = int(surface.get_width() * 0.12)
    bell_radius_y = int(surface.get_height() * 0.06)
    n_layers = 56  # More layers for richer body
    n_edge = 420
    # Draw umbrella as concentric dot contours, denser/brighter at edge
    for layer in range(n_layers):
        frac = layer / (n_layers-1)
        r_x = bell_radius_x * (1 - 0.18*frac)
        r_y = bell_radius_y * (1 - 0.18*frac)
        n_dots = int(n_edge * (1 - 0.7*frac) + 40)
        # Adjusted gradient: overall bluer (deeper blue core, less white)
        blue = int(200 + 55*(1-frac))          # 255 near top, ~200 near inner layers
        white = int(220 - 110*frac)            # Less white influence overall
        cyan = int(200 + 40*np.sin(frac*3 + t/220))  # Slight cyan shimmer, reduced amplitude
        alpha = int(100 - 55*frac)
        for i in range(n_dots):
            # Flip umbrella: theta from 0 to -pi (downward arch)
            theta = -np.pi * (i / n_dots) * (1.08 - 0.12*frac) - 0.08*np.sin(t/80 + layer*0.2)
            # Dome arch, slightly forward at bottom
            x = bell_center[0] + r_x * np.cos(theta) + 18*np.sin(frac*2.5 + t/120)
            y = bell_center[1] + r_y * np.sin(theta) + 18*frac + 12*np.sin(theta*2 + t/90)
            # Ripple effect on inner wall
            if 0.2 < frac < 0.8:
                y -= 18*np.sin(4*theta + t/60 + frac*6)
            size = int(2 + 2.5*(1-frac) + 1.5*np.sin(theta*2 + t/100))
            # Color: edge is white-blue, inside is blue-cyan-white, much more white for brightness
            if frac < 0.18:
                # Edge highlight now icy pale blue instead of pure white
                color = (210, 230, 255, min(255, alpha+50))
            elif frac > 0.7:
                # Inner darker rim, stronger blue bias
                color = (80, 150, min(255, blue+80), alpha)
            else:
                # Main body dots: suppress red/green, amplify blue
                r_comp = int(white*0.4 + cyan*0.1 + blue*0.05)
                g_comp = int(150 + 25*np.cos(theta+t/300) + cyan*0.15)
                b_comp = min(255, int(blue*0.9 + cyan*0.25 + 40))
                color = (r_comp, g_comp, b_comp, min(255, alpha+25))
            # Occasional white sparkle override (rarer deeper inside)
            sparkle_prob = 0.04 if frac < 0.25 else (0.02 if frac < 0.6 else 0.01)
            if np.random.rand() < sparkle_prob:
                # Bright white core with slightly higher alpha
                color = (245, 245, 255, min(255, color[3] + 70))
            # Draw dot and its mirror for symmetry
            pygame.draw.circle(dot_surf, color, (int(x), int(y)), size)
            mx = 2*bell_center[0] - x
            pygame.draw.circle(dot_surf, color, (int(mx), int(y)), size)
        # Add internal detail lines (radial and concentric, now arc upward, more transparent, deeper blue)
        if layer % 7 == 0 and layer > 0 and layer < n_layers-1:
            # Radial lines
            for j in range(0, 12):
                phi = np.pi - j * np.pi/6
                x1 = bell_center[0] + r_x * np.cos(phi)
                y1 = bell_center[1] + r_y * np.sin(phi)
                x2 = bell_center[0] + (r_x*0.7) * np.cos(phi)
                y2 = bell_center[1] + (r_y*0.7) * np.sin(phi)
                detail_col = (80, 180, 255, int(alpha*0.32))
                pygame.draw.aaline(dot_surf, detail_col, (x1, y1), (x2, y2))
            # Flipped concentric arcs (now arc upward)
            for j in range(0, 8):
                phi0 = np.pi*0.98 - j * np.pi*1.96/8
                phi1 = phi0 - np.pi*1.96/8
                r_detail = r_x * 0.7
                # Arc upward: y = center - abs(sin)
                y_detail = bell_center[1] - abs((r_y*0.7) * np.sin((phi0+phi1)/2))
                color2 = (30, 100, 255, int(alpha*0.18))
                pygame.draw.aaline(dot_surf, color2,
                    (bell_center[0] + r_detail * np.cos(phi0), y_detail),
                    (bell_center[0] + r_detail * np.cos(phi1), y_detail))
    # --- Trunk and tentacles: S-curve, misty dots/segments ---
    trunk_len = int(surface.get_height() * 0.32)
    n_trunk = 90
    trunk_points = []
    for i in range(n_trunk):
        frac = i / (n_trunk-1)
        # S-curve trunk from center bottom of bell
        base_x = bell_center[0]
        base_y = bell_center[1] + bell_radius_y * 0.98
        dx = 0 + 60*np.sin(frac*2.5 + t/60)
        dy = trunk_len * frac * 0.92 + 80*np.sin(frac*2.5 + t/80)
        x = base_x + dx + 40*np.sin(frac*4 + t/90)
        y = base_y + dy + 30*np.sin(frac*5 + t/100)
        trunk_points.append((x, y))
        # Blue-purple gradient trunk (reduced white, dynamic purple shimmer)
        size = int(4 - 2.5*frac + 1.5*np.sin(i*0.7 + t/80))
        blue = int(210 + 40*(1-frac))
        white = int(160 - 50*frac)
        purple = int(140 + 80*np.sin(frac*3 + t/70 + i*0.05))
        alpha = int(180 - 150*frac)
        r_comp = int(white*0.25 + purple*0.50 + blue*0.25)
        g_comp = int(white*0.20 + purple*0.35 + blue*0.25)
        b_comp = int(blue*0.85 + purple*0.15)
        color = (min(255, r_comp), min(255, g_comp), min(255, b_comp), alpha)
        # Trunk sparkle: higher chance near top, fading downward
        trunk_sparkle_prob = 0.05 * (1 - frac) + 0.01
        if np.random.rand() < trunk_sparkle_prob:
            color = (250, 250, 255, min(255, alpha + 40))
        pygame.draw.circle(dot_surf, color, (int(x), int(y)), size)
        mx = 2*bell_center[0] - x
        pygame.draw.circle(dot_surf, color, (int(mx), int(y)), size)
        # Misty afterimage
        if i > 0 and np.random.rand() < 0.7:
            fade = int(80 - 70*frac)
            pygame.draw.line(dot_surf, color[:3]+(fade,), (int(trunk_points[i-1][0]),int(trunk_points[i-1][1])), (int(x),int(y)), 1)
            pygame.draw.line(dot_surf, color[:3]+(fade,), (int(2*bell_center[0]-trunk_points[i-1][0]),int(trunk_points[i-1][1])), (int(mx),int(y)), 1)
    # Tentacle mist: many short, fading dotted trails
    n_tentacles = int(24 + wave_height * 90)
    for k in range(n_tentacles):
        frac = k / (n_tentacles-1) if n_tentacles > 1 else 0.5
        # Tentacle base: distributed along lower edge of bell, symmetrical
        theta = np.pi * (0.12 + 0.76*frac)
        base_x = bell_center[0] + bell_radius_x * 0.82 * np.cos(theta)
        base_y = bell_center[1] + bell_radius_y * 0.82 * np.sin(theta)
        # Each tentacle: S-curve, misty, dotted
        n_seg = np.random.randint(12, 22)
        px, py = base_x, base_y
        mpx, mpy = 2*bell_center[0] - base_x, base_y
        for j in range(n_seg):
            seg_frac = j / (n_seg-1)
            angle = 1.2*np.pi + 0.7*np.pi*frac + 0.5*np.sin(t/60 + k*0.3 + j*0.2)
            length = 60 + 32*seg_frac + 18*np.sin(j*0.7 + t/80)
            nx = px + length * np.cos(angle + 0.5*np.sin(j*0.5 + t/100))
            ny = py + length * np.sin(angle + 0.5*np.sin(j*0.5 + t/100))
            mnx = 2*bell_center[0] - nx
            # Blue-purple gradient tentacles (cool luminous filaments)
            size = int(2 + 2.5*(1-seg_frac) + 1.5*np.sin(j*0.7 + t/90))
            blue = int(190 + 50*(1-seg_frac))
            white = int(180 - 90*seg_frac)
            purple = int(150 + 90*np.sin(seg_frac*5 + t/60 + k*0.4 + j*0.15))
            alpha = int(120 - 110*seg_frac)
            r_comp = int(white*0.20 + purple*0.55 + blue*0.25)
            g_comp = int(white*0.15 + purple*0.40 + blue*0.25)
            b_comp = int(blue*0.80 + purple*0.20)
            color = (min(255, r_comp), min(255, g_comp), min(255, b_comp), alpha)
            # Tentacle sparkle: more near base, rarer near tip
            tentacle_sparkle_prob = 0.035 * (1 - seg_frac) + 0.006
            if np.random.rand() < tentacle_sparkle_prob:
                color = (240, 240, 255, min(255, alpha + 50))
            pygame.draw.circle(dot_surf, color, (int(nx), int(ny)), size)
            pygame.draw.circle(dot_surf, color, (int(mnx), int(ny)), size)
            # Occasional short segment for afterimage
            if np.random.rand() < 0.5:
                fade = int(60 - 55*seg_frac)
                pygame.draw.line(dot_surf, color[:3]+(fade,), (int(px),int(py)), (int(nx),int(ny)), 1)
                pygame.draw.line(dot_surf, color[:3]+(fade,), (int(mpx),int(mpy)), (int(mnx),int(ny)), 1)
            px, py = nx, ny
            mpx, mpy = mnx, ny
    # Blit dot cloud jellyfish onto the deep sea background
    surface.blit(dot_surf, (0,0))
    # --- Draw real-time data as text ---
    font = pygame.font.SysFont('consolas', 18)
    text_color = (120, 180, 255)
    wave_height, wave_direction, wave_period, current_speed = params
    lines = [
        f"Wave Height: {wave_height:.2f} m",
        f"Wave Dir: {wave_direction:.0f}°",
        f"Wave Period: {wave_period:.2f} s",
        f"Current Speed: {current_speed:.2f} m/s"
    ]
    # Slightly larger line spacing and shifted downward for clearer separation
    line_height = int(font.get_linesize() * 1.18)
    base_ty = bell_center[1] - bell_radius_y + 80  # further shift text block downward
    for i, line in enumerate(lines):
        text_surf = font.render(line, True, text_color)
        tx = bell_center[0] + bell_radius_x + margin_x//2
        ty = base_ty + i * line_height
        surface.blit(text_surf, (tx, ty))
    # Tentacles: number ~ wave_height
    n_tentacles = int(18 + wave_height * 40)
    for k in range(n_tentacles):
    # (Removed old centipede code: base_idx, spine_points, angle0)
        spread = 1.2 + 0.7 * (k/(n_tentacles-1))
    # (Removed old centipede tentacle code: tentacle_angle, length, points, etc.)

# --- MAIN LOOP ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Marine Creature Visualization')
    clock = pygame.time.Clock()
    data = load_wave_data(CSV_FILE)
    t = 0
    idx = 0
    # For natural movement, interpolate between data points
    interp_steps = 60  # Smoother, slower interpolation
    running = True
    prev_params = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((10, 20, 30))
        # Get current and next data
        if idx >= len(data):
            idx = 0
        d = data[idx]
        d_next = data[(idx+1)%len(data)]
        # Interpolate for smoothness
        frac = (t % interp_steps) / interp_steps
        params = tuple(
            d[k] * (1-frac) + d_next[k] * frac
            if isinstance(d[k], float) else d[k]
            for k in ['wave_height','wave_direction','wave_period','current_speed']
        )
        # Move center based on wave_direction (smoothed)
        angle = np.deg2rad(params[1])
        cx = WIDTH//2 + int(np.cos(angle) * 60)
        cy = HEIGHT//2 + int(np.sin(angle) * 60)
        draw_creature(screen, (cx, cy), params, t)
        # To OpenCV for postprocessing (optional)
        arr = pygame.surfarray.array3d(screen)
        arr = np.transpose(arr, (1,0,2))
        arr = cv2.GaussianBlur(arr, (0,0), 2.5)
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        cv2.imshow('Marine Creature', arr)
        # Step
        pygame.display.flip()
        t += 1
        if t % interp_steps == 0:
            idx = (idx + 1) % len(data)
        if cv2.waitKey(1000//FPS) & 0xFF == 27:
            running = False
        clock.tick(FPS)
    pygame.quit()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
