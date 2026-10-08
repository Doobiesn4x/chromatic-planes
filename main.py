import pygame
import numpy as np
import random
import json
import os
import time
import math
from core.generator import generate_mandala
from core.solver import check_k_colorability

os.makedirs("data/thumbnails", exist_ok=True)
os.makedirs("data/exports", exist_ok=True)
os.makedirs("data/screenshots", exist_ok=True)

def save_solution(seed, nodes_count, par, colors_used, coloring_array):
    filepath = "data/gallery_archive.json"
    history = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            pass
            
    if not any(entry["seed"] == seed for entry in history):
        history.append({
            "seed": seed, "nodes": nodes_count, "par": par,
            "colors_used": colors_used, "coloring": coloring_array,
            "is_masterpiece": colors_used <= par
        })
        history.sort(key=lambda x: (1 if x["is_masterpiece"] else 0, x["nodes"]), reverse=True)
        with open(filepath, "w") as f:
            json.dump(history, f, indent=4)
    return history

def load_highscores():
    filepath = "data/gallery_archive.json"
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f: return json.load(f)
        except json.JSONDecodeError: pass
    return []

thumbnail_cache = {}
def get_thumbnail(seed):
    if seed not in thumbnail_cache:
        path = f"data/thumbnails/thumb_{seed}.png"
        if os.path.exists(path):
            thumbnail_cache[seed] = pygame.image.load(path)
        else:
            thumbnail_cache[seed] = None
    return thumbnail_cache[seed]

def export_dimacs(seed, nodes, edges):
    filepath = f"data/exports/mandala_{seed}.col"
    with open(filepath, 'w') as f:
        f.write(f"c Hadwiger-Nelson Procedural Graph Seed {seed}\n")
        f.write(f"p edge {len(nodes)} {len(edges)}\n")
        for u, v in edges: f.write(f"e {u+1} {v+1}\n")
    return filepath

def spawn_confetti(num_particles, width, height, colors):
    particles = []
    for _ in range(num_particles):
        particles.append({
            'x': width // 2 + random.uniform(-50, 50),
            'y': height // 2 + 50,
            'vx': random.uniform(-10, 10),
            'vy': random.uniform(-15, -5),
            'color': random.choice(colors),
            'size': random.randint(6, 14),
            'life': 255.0,
            'rotation': random.uniform(0, 360),
            'rot_speed': random.uniform(-10, 10)
        })
    return particles

def get_depth_for_level(level):
    return level + 1  

def main():
    pygame.init()
    width, height = 1024, 768
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Chromatic Art Gallery: Citizen Science")
    
    font = pygame.font.SysFont(None, 28)
    small_font = pygame.font.SysFont(None, 22)
    large_font = pygame.font.SysFont(None, 40)
    title_font = pygame.font.SysFont(None, 72)
    giant_font = pygame.font.SysFont(None, 90)

    PALETTE = [
        (60, 60, 60),      # 0: Uncolored
        (220, 50, 50),     # 1: Red
        (50, 150, 255),    # 2: Blue
        (230, 200, 50),    # 3: Yellow
        (50, 220, 50),     # 4: Green
        (180, 50, 220),    # 5: Purple
        (255, 120, 50),    # 6: Orange
        (50, 220, 220)     # 7: Cyan
    ]

    STATE_MENU, STATE_PLAY, STATE_HIGHSCORES, STATE_INSTRUCTIONS = 0, 1, 2, 3
    current_state = STATE_MENU

    active_color = 1
    current_level = 1
    current_seed = random.randint(1000, 9999)
    
    hud_message = ""
    hud_timer = 0
    gallery_hud_message = ""
    gallery_hud_timer = 0
    particles = []

    def load_procedural_level(seed, level):
        depth = get_depth_for_level(level)
        print(f"\nGenerating Level {level} (Seed: {seed}, Depth: {depth})...")
        coords, edges = generate_mandala(seed, depth)
        nodes = [{"pos": np.array(c), "color": 0} for c in coords]
        
        is_3, _ = check_k_colorability(len(nodes), edges, 3)
        if is_3:
            par = 3
        else:
            is_4, _ = check_k_colorability(len(nodes), edges, 4)
            if is_4:
                par = 4
            else:
                par = 5 

        min_x, max_x = min(c[0] for c in coords), max(c[0] for c in coords)
        min_y, max_y = min(c[1] for c in coords), max(c[1] for c in coords)
        center_x, center_y = (min_x + max_x) / 2, (min_y + max_y) / 2
        span = max(max_x - min_x, max_y - min_y)
        scale = min(150, 500 / (span if span > 0 else 1))
        
        return nodes, edges, par, center_x, center_y, scale

    nodes, edges, par, camera_x, camera_y, zoom = load_procedural_level(current_seed, current_level)

    TOP_BAR_H = 80
    BOT_BAR_H = 120
    canvas_rect = pygame.Rect(0, TOP_BAR_H, width, height - TOP_BAR_H - BOT_BAR_H)

    def world_to_screen(wx, wy):
        sx = (wx - camera_x) * zoom + (width / 2)
        sy = -(wy - camera_y) * zoom + (TOP_BAR_H + canvas_rect.height / 2)
        return int(sx), int(sy)

    def screen_to_world(sx, sy):
        wx = camera_x + (sx - width / 2) / zoom
        wy = camera_y - (sy - (TOP_BAR_H + canvas_rect.height / 2)) / zoom
        return wx, wy

    running = True
    level_complete = False
    solution_saved = False
    highscores_data = []
    is_panning = False
    pan_start_pos = (0, 0)

    btn_start = pygame.Rect(width//2 - 150, 280, 300, 60)
    btn_instructions = pygame.Rect(width//2 - 150, 360, 300, 60)
    btn_highscores = pygame.Rect(width//2 - 150, 440, 300, 60)
    btn_quit = pygame.Rect(width//2 - 150, 520, 300, 60)

    clock = pygame.time.Clock()

    while running:
        dt = clock.tick(60)
        screen.fill((15, 18, 22))

        # ---------------- MENU STATE ----------------
        if current_state == STATE_MENU:
            title = title_font.render("CHROMATIC PLANES", True, (200, 220, 255))
            screen.blit(title, (width//2 - title.get_width()//2, 120))
            
            mx, my = pygame.mouse.get_pos()
            for btn, text in [(btn_start, "START PAINTING"), (btn_instructions, "THE SCIENCE (HOW TO)"), (btn_highscores, "VISUAL GALLERY"), (btn_quit, "QUIT")]:
                color = (70, 80, 100) if btn.collidepoint((mx, my)) else (50, 60, 70)
                pygame.draw.rect(screen, color, btn, border_radius=5)
                label = font.render(text, True, (255, 255, 255))
                screen.blit(label, (btn.x + btn.width//2 - label.get_width()//2, btn.y + btn.height//2 - label.get_height()//2))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_start.collidepoint(event.pos): current_state = STATE_PLAY
                    elif btn_instructions.collidepoint(event.pos): current_state = STATE_INSTRUCTIONS
                    elif btn_highscores.collidepoint(event.pos):
                        highscores_data = load_highscores()
                        current_state = STATE_HIGHSCORES
                    elif btn_quit.collidepoint(event.pos): running = False
            pygame.display.flip()
            continue

        # ---------------- INSTRUCTIONS STATE ----------------
        if current_state == STATE_INSTRUCTIONS:
            title = large_font.render("THE HADWIGER-NELSON PROBLEM", True, (255, 200, 100))
            screen.blit(title, (width//2 - title.get_width()//2, 50))
            
            instructions = [
                "THE GOAL: Color the geometric nodes so that no connected dots share the same color.",
                "",
                "THE RULE: Every grey line connecting the dots represents a distance of exactly 1.0.",
                "",
                "THE MYSTERY: Mathematicians know it takes at least 5 colors to paint the infinite",
                "Euclidean plane, and at most 7. In 2018, the first 5-color graph was found, but it",
                "was massive (1,581 nodes). The exact chromatic number is still unknown.",
                "",
                "YOUR MISSION: Explore procedurally generated 'Mandalas'. The AI background",
                "solver calculates the absolute minimum colors needed (The Par).",
                "",
                "If you match the Par, you log a Masterpiece. If you ever generate a Mandala",
                "that requires 6 colors, you will have solved an 80-year-old math problem."
            ]
            
            y = 150
            for line in instructions:
                color = (200, 255, 200) if "YOUR MISSION" in line else (200, 200, 200)
                txt = font.render(line, True, color)
                screen.blit(txt, (width//2 - txt.get_width()//2, y))
                y += 35
                
            sub = font.render("Press ESC to return to Menu", True, (100, 150, 255))
            screen.blit(sub, (width//2 - sub.get_width()//2, height - 100))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: current_state = STATE_MENU
            pygame.display.flip()
            continue

        # ---------------- HIGHSCORES STATE (VISUAL GALLERY) ----------------
        if current_state == STATE_HIGHSCORES:
            if gallery_hud_timer > 0: gallery_hud_timer -= dt
            
            title = large_font.render("VISUAL GALLERY ARCHIVE", True, (255, 200, 100))
            screen.blit(title, (width//2 - title.get_width()//2, 40))
            
            export_buttons = []
            mx, my = pygame.mouse.get_pos()
            
            if not highscores_data:
                msg = font.render("No puzzles solved yet. Go paint!", True, (200, 200, 200))
                screen.blit(msg, (width//2 - msg.get_width()//2, 250))
            else:
                y_off = 110
                for i, r in enumerate(highscores_data[:4]): # Top 4 to fit the screen nicely
                    color = (100, 255, 100) if r["is_masterpiece"] else (200, 200, 200)
                    rating = "MASTERPIECE" if r["is_masterpiece"] else "SOLVED"

                    # 1. Rank Number
                    rank_txt = giant_font.render(f"#{i+1}", True, (60, 70, 80))
                    screen.blit(rank_txt, (50, y_off + 25))

                    # 2. Thumbnail
                    thumb = get_thumbnail(r['seed'])
                    if thumb:
                        screen.blit(thumb, (150, y_off))
                        pygame.draw.rect(screen, (100, 110, 120), (150, y_off, thumb.get_width(), thumb.get_height()), 2)
                    else:
                        pygame.draw.rect(screen, (50, 50, 50), (150, y_off, 200, 110))
                        pygame.draw.rect(screen, (100, 110, 120), (150, y_off, 200, 110), 2)

                    # 3. Text Info
                    row1 = large_font.render(f"Seed #{r['seed']}  |  {rating}", True, color)
                    screen.blit(row1, (380, y_off + 15))
                    
                    row2 = font.render(f"Nodes: {r['nodes']}   |   Par: {r['par']}   |   Colors Used: {r['colors_used']}", True, (180, 180, 180))
                    screen.blit(row2, (380, y_off + 60))

                    # 4. Export Image Button
                    btn_rect = pygame.Rect(width - 180, y_off + 35, 130, 40)
                    export_buttons.append((btn_rect, r['seed']))
                    
                    b_color = (70, 150, 100) if btn_rect.collidepoint((mx, my)) else (40, 110, 70)
                    pygame.draw.rect(screen, b_color, btn_rect, border_radius=5)
                    btn_lbl = small_font.render("SAVE IMAGE", True, (255, 255, 255))
                    screen.blit(btn_lbl, (btn_rect.centerx - btn_lbl.get_width()//2, btn_rect.centery - btn_lbl.get_height()//2))

                    y_off += 125
                    
            esc_txt = font.render("Press ESC to return to Menu", True, (150, 150, 150))
            screen.blit(esc_txt, (width//2 - esc_txt.get_width()//2, height - 50))
            
            # Temporary Success Popup
            if gallery_hud_timer > 0:
                notify_bg = pygame.Rect(width//2 - 250, height - 120, 500, 40)
                pygame.draw.rect(screen, (40, 150, 80), notify_bg, border_radius=5)
                notif_text = font.render(gallery_hud_message, True, (255, 255, 255))
                screen.blit(notif_text, (notify_bg.centerx - notif_text.get_width()//2, notify_bg.centery - notif_text.get_height()//2))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: current_state = STATE_MENU
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn_rect, seed in export_buttons:
                        if btn_rect.collidepoint(event.pos):
                            thumb_img = get_thumbnail(seed)
                            if thumb_img:
                                export_path = f"data/exports/favorite_mandala_{seed}.png"
                                pygame.image.save(thumb_img, export_path)
                                gallery_hud_message = f"Saved to {export_path}!"
                                gallery_hud_timer = 3000
                                
            pygame.display.flip()
            continue

        # ---------------- PLAY STATE ----------------
        if hud_timer > 0: hud_timer -= dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:
                    if my > height - BOT_BAR_H and not level_complete:
                        start_x = (width - (7 * 55 + 6 * 15)) / 2
                        for i in range(1, 8):
                            if start_x + (i - 1) * 70 <= mx <= start_x + (i - 1) * 70 + 55: active_color = i
                    elif canvas_rect.collidepoint(mx, my) and not level_complete:
                        for node in nodes:
                            nx, ny = world_to_screen(node["pos"][0], node["pos"][1])
                            if (nx - mx)**2 + (ny - my)**2 <= 16**2:
                                node["color"] = active_color
                                break
                elif event.button in (2, 3) and canvas_rect.collidepoint(mx, my) and not level_complete:
                    is_panning, pan_start_pos = True, event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button in (2, 3): is_panning = False
            elif event.type == pygame.MOUSEMOTION and is_panning:
                camera_x -= (event.pos[0] - pan_start_pos[0]) / zoom
                camera_y += (event.pos[1] - pan_start_pos[1]) / zoom
                pan_start_pos = event.pos
            elif event.type == pygame.MOUSEWHEEL and not level_complete:
                mx, my = pygame.mouse.get_pos()
                if canvas_rect.collidepoint(mx, my):
                    wx, wy = screen_to_world(mx, my)
                    zoom = max(10, min(zoom * (1.1 ** event.y), 3000))
                    camera_x = wx - (mx - width / 2) / zoom
                    camera_y = wy + (my - (TOP_BAR_H + canvas_rect.height / 2)) / zoom
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: current_state = STATE_MENU
                elif event.key == pygame.K_c and not level_complete:
                    for n in nodes: n["color"] = 0
                elif event.key == pygame.K_F12:
                    filepath = f"data/screenshots/level{current_level}_seed{current_seed}_{int(time.time())}.png"
                    pygame.image.save(screen, filepath)
                    hud_message, hud_timer = f"Saved: {filepath}", 3000
                elif event.key == pygame.K_e:
                    hud_message, hud_timer = f"Math Exported: {export_dimacs(current_seed, nodes, edges)}", 3000
                elif event.key == pygame.K_SPACE and level_complete:
                    current_level += 1
                    current_seed = random.randint(1000, 9999)
                    nodes, edges, par, camera_x, camera_y, zoom = load_procedural_level(current_seed, current_level)
                    level_complete, solution_saved, active_color, particles = False, False, 1, []
                elif event.key == pygame.K_r:
                    current_seed = random.randint(1000, 9999)
                    nodes, edges, par, camera_x, camera_y, zoom = load_procedural_level(current_seed, current_level)
                    level_complete, solution_saved, particles = False, False, []

        conflicts, uncolored, colors_used = 0, 0, set()
        for n in nodes:
            if n["color"] == 0: uncolored += 1
            else: colors_used.add(n["color"])

        # DRAW CANVAS FIRST (So the thumbnail looks correct)
        screen.set_clip(canvas_rect)
        screen.fill((15, 18, 22))
        
        for u, v in edges:
            p1 = world_to_screen(nodes[u]["pos"][0], nodes[u]["pos"][1])
            p2 = world_to_screen(nodes[v]["pos"][0], nodes[v]["pos"][1])
            c1, c2 = nodes[u]["color"], nodes[v]["color"]
            if (c1 == c2) and (c1 != 0):
                pygame.draw.line(screen, (255, 40, 40), p1, p2, 6)
                conflicts += 1
            else:
                pygame.draw.line(screen, (50, 60, 70), p1, p2, 2)

        for node in nodes:
            pos = world_to_screen(node["pos"][0], node["pos"][1])
            pygame.draw.circle(screen, PALETTE[node["color"]], pos, 12)
            pygame.draw.circle(screen, (200, 200, 200), pos, 12, 2)
            
        screen.set_clip(None)

        # CHECK VICTORY LOGIC (Triggered AFTER canvas draw, BEFORE overlay)
        if uncolored == 0 and conflicts == 0 and not level_complete:
            level_complete = True
            
            # --- Capture Automatic Thumbnail ---
            thumb_surf = screen.subsurface(canvas_rect).copy()
            thumb_w = 200
            thumb_h = int(200 * canvas_rect.height / canvas_rect.width)
            thumb_surf = pygame.transform.smoothscale(thumb_surf, (thumb_w, thumb_h))
            pygame.image.save(thumb_surf, f"data/thumbnails/thumb_{current_seed}.png")
            
            # --- Trigger Confetti ---
            if len(colors_used) <= par:
                particles = spawn_confetti(250, width, height, [PALETTE[c] for c in colors_used] if colors_used else PALETTE[1:])
            else:
                particles = spawn_confetti(50, width, height, [(200, 200, 200)])

        # DRAW EFFECTS OVER THE CANVAS
        if level_complete:
            overlay = pygame.Surface((width, canvas_rect.height), pygame.SRCALPHA)
            overlay_color = (40, 50, 10, 200) if len(colors_used) <= par else (20, 25, 30, 200)
            overlay.fill(overlay_color)
            screen.blit(overlay, (0, TOP_BAR_H))
            
            for p in particles:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] += 0.4
                p['life'] -= 1.5
                p['rotation'] += p['rot_speed']
                if p['life'] > 0:
                    surf = pygame.Surface((p['size'], p['size']), pygame.SRCALPHA)
                    surf.fill((*p['color'], max(0, min(255, int(p['life'])))))
                    surf = pygame.transform.rotate(surf, p['rotation'])
                    screen.blit(surf, (int(p['x']), int(p['y'])))
            particles = [p for p in particles if p['life'] > 0]

            pulse_offset = math.sin(time.time() * 5) * 10
            msg = "MASTERPIECE!" if len(colors_used) <= par else "SOLVED"
            color = (100, 255, 100) if len(colors_used) <= par else (200, 200, 200)
            
            win_text = giant_font.render(msg, True, color)
            stat_text = large_font.render(f"Painted {len(nodes)} nodes with {len(colors_used)} colors", True, (255, 255, 255))
            sub_text = font.render("Press SPACE for next level, R to reroll, ESC for Menu", True, (150, 200, 255))
            
            screen.blit(win_text, (width//2 - win_text.get_width()//2, TOP_BAR_H + canvas_rect.height//2 - 80 + pulse_offset))
            screen.blit(stat_text, (width//2 - stat_text.get_width()//2, TOP_BAR_H + canvas_rect.height//2 + 10))
            screen.blit(sub_text, (width//2 - sub_text.get_width()//2, TOP_BAR_H + canvas_rect.height//2 + 70))
            
            if not solution_saved:
                save_solution(current_seed, len(nodes), par, len(colors_used), [n["color"] for n in nodes])
                solution_saved = True

        screen.set_clip(None)

        # ---------------- FIXED TOP HUD ----------------
        pygame.draw.rect(screen, (25, 30, 35), (0, 0, width, TOP_BAR_H))
        pygame.draw.line(screen, (100, 150, 255), (0, TOP_BAR_H-1), (width, TOP_BAR_H-1), 2)
        
        title_surf = large_font.render(f"Level {current_level}  |  Seed #{current_seed}", True, (255, 255, 255))
        screen.blit(title_surf, (20, 12))
        nodes_surf = small_font.render(f"Nodes: {len(nodes)}   |   Edges: {len(edges)}", True, (150, 160, 170))
        screen.blit(nodes_surf, (20, 52))
        
        par_txt = "PAR: 5 (WORLD RECORD!)" if par == 5 else f"AI Par: {par}"
        par_color = (255, 100, 255) if par == 5 else (100, 200, 255)
        par_surf = large_font.render(par_txt, True, par_color)
        screen.blit(par_surf, (width//2 - par_surf.get_width()//2, TOP_BAR_H//2 - par_surf.get_height()//2))
        
        c_color = (255, 80, 80) if len(colors_used) > par else ((100, 255, 100) if len(colors_used) == par and len(colors_used) > 0 else (180, 180, 180))
        colors_surf = large_font.render(f"Colors Used: {len(colors_used)}", True, c_color)
        screen.blit(colors_surf, (width - colors_surf.get_width() - 30, TOP_BAR_H//2 - colors_surf.get_height()//2))

        # ---------------- BOTTOM TOOLBAR ----------------
        pygame.draw.rect(screen, (25, 30, 35), (0, height - BOT_BAR_H, width, BOT_BAR_H))
        pygame.draw.line(screen, (100, 150, 255), (0, height - BOT_BAR_H), (width, height - BOT_BAR_H), 2)
        
        start_x = (width - (7 * 55 + 6 * 15)) / 2
        for i in range(1, 8):
            bx, by = start_x + (i - 1) * 70, height - 90
            if i == active_color and not level_complete:
                pygame.draw.rect(screen, (255, 255, 255), (bx-4, by-4, 63, 63), 2, border_radius=8)
            pygame.draw.rect(screen, PALETTE[i], (bx, by, 55, 55), border_radius=6)

        ctrl_txt = "L-Click: Paint | R-Click: Pan | Scroll: Zoom | C: Clear | F12: Screenshot | E: Export Math | ESC: Menu"
        screen.blit(small_font.render(ctrl_txt, True, (120, 130, 140)), (width//2 - small_font.size(ctrl_txt)[0]//2, height - 25))

        if hud_timer > 0:
            pygame.draw.rect(screen, (40, 150, 80), (width//2 - 200, TOP_BAR_H + 20, 400, 40), border_radius=5)
            screen.blit(font.render(hud_message, True, (255, 255, 255)), (width//2 - font.size(hud_message)[0]//2, TOP_BAR_H + 30))

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
