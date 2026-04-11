import math
import os
import pygame


class VueTerminalRobot:
    def dessiner_robot(self, robot):
        print(f"Robot -> x={robot.x:.2f}, y={robot.y:.2f}, orientation={robot.orientation:.2f}")


class VuePygame:
    def __init__(self, largeur=800, hauteur=600, scale=50,
                 robot_image_path="robot.png", belt_image_path="fil.png"):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Simulation Robot Mobile")

        self.largeur = int(largeur)
        self.hauteur = int(hauteur)
        self.scale = float(scale)
        self.clock = pygame.time.Clock()

        self.zone_w_m = 10.0
        self.zone_h_m = 10.0

        self.show_lidar = True

        self.robot_image_original = None
        self.belt_image_original = None

        self.font = pygame.font.SysFont("arial", 18)
        self.font_small = pygame.font.SysFont("arial", 15)

        self._charger_images(robot_image_path, belt_image_path)

    def _find_asset_path(self, filename):
        possible_paths = [
            filename,
            os.path.join(os.getcwd(), filename),
            os.path.join(os.getcwd(), "assets", filename),
        ]

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        possible_paths.extend([
            os.path.join(project_root, filename),
            os.path.join(project_root, "assets", filename),
        ])

        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def _charger_images(self, robot_image_path, belt_image_path):
        robot_path = self._find_asset_path(robot_image_path)
        if robot_path is not None:
            try:
                self.robot_image_original = pygame.image.load(robot_path).convert_alpha()
            except Exception:
                self.robot_image_original = None

        belt_path = self._find_asset_path(belt_image_path)
        if belt_path is not None:
            try:
                self.belt_image_original = pygame.image.load(belt_path).convert_alpha()
            except Exception:
                self.belt_image_original = None

    def set_zone(self, largeur_m, hauteur_m):
        self.zone_w_m = float(largeur_m)
        self.zone_h_m = float(hauteur_m)

    # -------------------------------------------------
    # Conversions coordonnées
    # -------------------------------------------------
    def convertir_coordonnees(self, x, y):
        px = int(self.largeur / 2 + float(x) * self.scale)
        py = int(self.hauteur / 2 - float(y) * self.scale)
        return px, py

    def rect_m_to_rect_px(self, x_m, y_m, w_m, h_m):
        cx, cy = self.convertir_coordonnees(x_m, y_m)
        w_px = max(1, int(float(w_m) * self.scale))
        h_px = max(1, int(float(h_m) * self.scale))
        left = cx - w_px // 2
        top = cy - h_px // 2
        return pygame.Rect(left, top, w_px, h_px)

    # -------------------------------------------------
    # Dessins
    # -------------------------------------------------
    def dessiner_zone_contour(self):
        zone_rect = self.rect_m_to_rect_px(0.0, 0.0, self.zone_w_m, self.zone_h_m)
        pygame.draw.rect(self.screen, (0, 0, 0), zone_rect, 2)

    def dessiner_colis(self, colis):
        x, y = self.convertir_coordonnees(colis.x, colis.y)
        size = 12

        if colis.couleur.upper() == "RED":
            color = (220, 60, 60)
        else:
            color = (60, 180, 60)

        rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (25, 25, 25), rect, 1)

    def dessiner_file_attente(self, file_attente):
        if file_attente is None:
            return

        bx, by, bw, bh = file_attente.rect_world
        belt_rect = self.rect_m_to_rect_px(bx, by, bw, bh)

        # image du fil
        if self.belt_image_original is not None:
            belt_img = pygame.transform.smoothscale(
                self.belt_image_original,
                (belt_rect.width, belt_rect.height)
            )
            self.screen.blit(belt_img, belt_rect)
        else:
            pygame.draw.rect(self.screen, (40, 40, 40), belt_rect)
            pygame.draw.rect(self.screen, (230, 230, 230), belt_rect, 2)

        # label
        txt = self.font_small.render("File d'attente colis", True, (20, 20, 20))
        self.screen.blit(txt, (belt_rect.x, belt_rect.y - 22))

        # colis SUR la route
        for colis in file_attente.colis:
            self.dessiner_colis(colis)

    def dessiner_robot(self, robot):
        x, y = self.convertir_coordonnees(robot.x, robot.y)

        if hasattr(robot, "rayon"):
            r = max(6, int(float(robot.rayon) * self.scale))
        else:
            r = 15

        if self.robot_image_original is not None:
            diameter_px = max(24, int(2.6 * r))
            image_scaled = pygame.transform.smoothscale(
                self.robot_image_original,
                (diameter_px, diameter_px)
            )

            # image tournée vers le haut
            angle_deg = math.degrees(robot.orientation) - 90.0
            image_rotated = pygame.transform.rotate(image_scaled, angle_deg)
            rect = image_rotated.get_rect(center=(x, y))
            self.screen.blit(image_rotated, rect)
        else:
            pygame.draw.circle(self.screen, (0, 120, 255), (x, y), r)

        x_dir = x + int((r + 10) * math.cos(robot.orientation))
        y_dir = y - int((r + 10) * math.sin(robot.orientation))
        pygame.draw.line(self.screen, (40, 40, 40), (x, y), (x_dir, y_dir), 2)


    def _dessiner_zone_charge(self, zone, env):
        """Dessin enrichi de la zone de charge : contour animé + icône éclair."""
        r = self.rect_m_to_rect_px(zone.x, zone.y, zone.largeur, zone.hauteur)

        # Contour jaune épais (orange si robot en charge)
        r1_state = getattr(env, "_r1_state", "WORKING")
        border_color = (255, 160, 0) if r1_state == "CHARGING" else (200, 180, 0)
        pygame.draw.rect(self.screen, border_color, r, 3)

        # Éclair ⚡ centré
        font_big = pygame.font.SysFont("arial", 22, bold=True)
        surf = font_big.render("⚡", True, (180, 140, 0))
        txt_rect = surf.get_rect(center=r.center)
        self.screen.blit(surf, txt_rect)

        # Label
        font_s = pygame.font.SysFont("arial", 11)
        surf2  = font_s.render("CHARGE", True, (120, 90, 0))
        self.screen.blit(surf2, (r.x, r.y - 14))

    def dessiner_robot2(self, robot2):
        """Dessine le robot 2 avec teinte violette + colis transportés visibles."""
        r_obj = robot2.robot
        x, y  = self.convertir_coordonnees(r_obj.x, r_obj.y)
        r_px  = max(6, int(float(r_obj.rayon) * self.scale))

        # ── Corps du robot ──
        if self.robot_image_original is not None:
            diameter_px   = max(24, int(2.6 * r_px))
            image_scaled  = pygame.transform.smoothscale(
                self.robot_image_original, (diameter_px, diameter_px)
            )
            tint = pygame.Surface((diameter_px, diameter_px), pygame.SRCALPHA)
            tint.fill((140, 60, 220, 90))
            image_scaled.blit(tint, (0, 0))
            angle_deg     = math.degrees(r_obj.orientation) - 90.0
            image_rotated = pygame.transform.rotate(image_scaled, angle_deg)
            rect = image_rotated.get_rect(center=(x, y))
            self.screen.blit(image_rotated, rect)
        else:
            pygame.draw.circle(self.screen, (130, 60, 200), (x, y), r_px)
            pygame.draw.circle(self.screen, (60, 20, 120), (x, y), r_px, 2)

        # Flèche direction
        x_dir = x + int((r_px + 10) * math.cos(r_obj.orientation))
        y_dir = y - int((r_px + 10) * math.sin(r_obj.orientation))
        pygame.draw.line(self.screen, (60, 0, 140), (x, y), (x_dir, y_dir), 2)

        # ── Colis transportés visibles (empilés derrière le robot) ──
        if robot2.carry > 0:
            offset  = r_px + 6
            c_size  = 7
            spacing = c_size + 2
            for i in range(min(robot2.carry, 5)):   # max 5 affichés
                angle_back = r_obj.orientation + math.pi
                cx = x + int((offset + i * spacing) * math.cos(angle_back))
                cy = y - int((offset + i * spacing) * math.sin(angle_back))
                pygame.draw.rect(self.screen, (180, 100, 230),
                                 pygame.Rect(cx - c_size//2, cy - c_size//2, c_size, c_size))
                pygame.draw.rect(self.screen, (80, 0, 140),
                                 pygame.Rect(cx - c_size//2, cy - c_size//2, c_size, c_size), 1)
            if robot2.carry > 5:
                font_s = pygame.font.SysFont("arial", 11)
                surf   = font_s.render(f"+{robot2.carry - 5}", True, (80, 0, 140))
                self.screen.blit(surf, (x - 8, y - r_px - 16))

        # ── Label état ──
        font  = pygame.font.SysFont("arial", 12, bold=True)
        label = f"R2:{robot2.state}"
        surf  = font.render(label, True, (60, 0, 120))
        self.screen.blit(surf, (x - 24, y + r_px + 3))

    def _hud_rect(self, x, y, w, h, color, alpha=200):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((*color, alpha))
        self.screen.blit(s, (x, y))

    def dessiner_hud(self, env):
        file_attente = getattr(env, "file_attente", None)
        n_attente    = file_attente.count() if file_attente is not None else 0
        n_livres     = int(getattr(env, "nb_livres", 0))
        robot2       = getattr(env, "robot2", None)
        batterie     = getattr(env, "batterie", None)
        paused       = getattr(env, "paused", False)
        r1_state     = getattr(env, "_r1_state", "WORKING")
        v1           = abs(getattr(env, "_r1_vitesse", 0.0))
        carrying     = getattr(env, "colis_transporte", None) is not None
        warmup       = getattr(file_attente, "_in_warmup", False)
        next_s       = file_attente.time_until_next() if file_attente and not warmup else 0

        font_t = pygame.font.SysFont("arial", 13, bold=True)
        font_n = pygame.font.SysFont("arial", 13)
        font_s = pygame.font.SysFont("arial", 11)
        LINE   = 17   # espacement standard entre lignes
        PAD    = 12   # marge gauche

        hud_w = 215
        # Fond sera dessiné après calcul exact de la hauteur

        # Fond semi-transparent (hauteur estimée, sera correcte dans 99% des cas)
        hud_h_est = 14 * LINE + 40
        self._hud_rect(5, 5, hud_w, hud_h_est, (245, 245, 245), alpha=220)
        pygame.draw.rect(self.screen, (160, 160, 180), pygame.Rect(5, 5, hud_w, hud_h_est), 1)

        y = 11

        # ── Titre ──
        surf = font_t.render("SIMULATION ROBOT", True, (30, 30, 110))
        self.screen.blit(surf, (PAD + 3, y)); y += LINE + 3
        pygame.draw.line(self.screen, (180, 180, 200), (8, y), (8 + hud_w - 6, y), 1); y += 5

        # ── PAUSE ──
        if paused:
            surf = font_t.render("⏸  PAUSE", True, (200, 80, 0))
            self.screen.blit(surf, (PAD + 40, y)); y += LINE + 2

        # ── Convoyeur ──
        conv_color = (0, 130, 0) if n_attente > 0 else (150, 60, 0)
        surf = font_n.render(f"Convoyeur : {n_attente} colis", True, conv_color)
        self.screen.blit(surf, (PAD, y)); y += LINE
        if warmup:
            surf = font_s.render("  warmup actif", True, (0, 150, 70))
        else:
            surf = font_s.render(f"  prochain : {next_s:.1f}s", True, (110, 110, 110))
        self.screen.blit(surf, (PAD, y)); y += LINE

        # ── Livraisons ──
        surf = font_n.render(f"Livraisons : {n_livres}", True, (20, 20, 20))
        self.screen.blit(surf, (PAD, y)); y += LINE + 2
        pygame.draw.line(self.screen, (180, 180, 200), (8, y), (8 + hud_w - 6, y), 1); y += 4

        # ── Zones stockage ──
        for z in getattr(env, "zones", []):
            if z.capacity <= 0 or not z.name.startswith("STORAGE"):
                continue
            is_green  = "GREEN" in z.name
            label     = "Vert" if is_green else "Rouge"
            bar_color = (60, 180, 60) if is_green else (210, 60, 60)
            if z.is_full():
                bar_color = (200, 0, 0); label += " ⚠"

            surf = font_s.render(f"Zone {label} : {z.count}/{z.capacity}", True, bar_color)
            self.screen.blit(surf, (PAD, y)); y += 13

            bar_w = hud_w - 22; bar_h = 6
            pygame.draw.rect(self.screen, (210, 210, 210), pygame.Rect(PAD, y, bar_w, bar_h))
            fill = int(bar_w * z.count / z.capacity) if z.capacity > 0 else 0
            pygame.draw.rect(self.screen, bar_color, pygame.Rect(PAD, y, fill, bar_h))
            pygame.draw.rect(self.screen, (150, 150, 150), pygame.Rect(PAD, y, bar_w, bar_h), 1)
            y += bar_h + 5

        pygame.draw.line(self.screen, (180, 180, 200), (8, y), (8 + hud_w - 6, y), 1); y += 4

        # ── Robot 1 ──
        if r1_state == "CHARGING":
            r1_color = (200, 130, 0)
            r1_label = "Robot 1 : EN CHARGE ⚡"
        elif carrying:
            r1_color = (0, 130, 50)
            r1_label = "Robot 1 : transporte"
        else:
            r1_color = (0, 80, 200)
            r1_label = "Robot 1 : libre"

        surf = font_n.render(r1_label, True, r1_color)
        self.screen.blit(surf, (PAD, y)); y += LINE

        # Barre batterie
        if batterie is not None:
            pct       = batterie.pct()
            bat_color = batterie.color()
            bar_w     = hud_w - 22; bar_h = 9
            pygame.draw.rect(self.screen, (210, 210, 210), pygame.Rect(PAD, y, bar_w, bar_h))
            fill = int(bar_w * pct / 100)
            pygame.draw.rect(self.screen, bat_color, pygame.Rect(PAD, y, fill, bar_h))
            pygame.draw.rect(self.screen, (100, 100, 100), pygame.Rect(PAD, y, bar_w, bar_h), 1)
            # % centré sur la barre
            font_b = pygame.font.SysFont("arial", 9, bold=True)
            surf_b = font_b.render(f"{pct}%", True, (30, 30, 30))
            self.screen.blit(surf_b, (PAD + bar_w // 2 - 8, y + 1))
            y += bar_h + 3
            surf = font_s.render(f"  vitesse : {v1:.2f} m/s", True, (100, 100, 100))
            self.screen.blit(surf, (PAD, y)); y += LINE

        pygame.draw.line(self.screen, (180, 180, 200), (8, y), (8 + hud_w - 6, y), 1); y += 4

        # ── Robot 2 ──
        if robot2 is not None:
            state_colors = {
                "IDLE": (120, 120, 120), "GO_ZONE": (180, 80, 0),
                "PICK": (0, 160, 0), "GO_EXPORT": (100, 0, 180), "DROP": (0, 120, 180)
            }
            r2_color = state_colors.get(robot2.state, (60, 60, 60))
            surf = font_n.render(f"Robot 2 : {robot2.state}", True, r2_color)
            self.screen.blit(surf, (PAD, y)); y += LINE
            surf2 = font_s.render(
                f"  {robot2.vitesse:.2f} m/s  |  carry : {robot2.carry}  |  exp : {robot2.total_exported}",
                True, (90, 90, 90))
            self.screen.blit(surf2, (PAD, y)); y += LINE + 2

        pygame.draw.line(self.screen, (180, 180, 200), (8, y), (8 + hud_w - 6, y), 1); y += 4

        # ── Raccourcis ──
        surf = font_s.render("H : lidar    P : pause", True, (150, 150, 150))
        self.screen.blit(surf, (PAD, y)); y += LINE

        # Fond dessiné en dernier (par-dessus rien, les textes sont déjà tracés)
        # → On dessine le fond AVANT les textes via un Surface alpha séparé
        # (déjà fait en début de frame dans dessiner_environnement via fill blanc)

    def dessiner_environnement(self, env):
        self.screen.fill((255, 255, 255))

        # 1) contour monde
        self.dessiner_zone_contour()

        # 2) obstacles
        for obs in getattr(env, "obstacles", []):
            if hasattr(obs, "dessiner"):
                obs.dessiner(self)

        # 3) zones
        for z in getattr(env, "zones", []):
            if hasattr(z, "dessiner"):
                z.dessiner(self)
            # Dessin spécial zone CHARGE : éclair + contour jaune animé
            if getattr(z, "name", "") == "CHARGE":
                self._dessiner_zone_charge(z, env)

        # 4) fil + file
        self.dessiner_file_attente(getattr(env, "file_attente", None))

        # 5) lidar
        if self.show_lidar and getattr(env, "lidar_data", None) is not None and hasattr(env, "lidar_sensor"):
            env.lidar_sensor.draw(self, env.robot, env.lidar_data)

        # 6) colis transporté
        if getattr(env, "colis_transporte", None) is not None:
            self.dessiner_colis(env.colis_transporte)

        # 7) robot 1
        if getattr(env, "robot", None) is not None:
            self.dessiner_robot(env.robot)

        # 8) robot 2
        if getattr(env, "robot2", None) is not None:
            self.dessiner_robot2(env.robot2)

        # 9) HUD
        self.dessiner_hud(env)

        pygame.display.flip()

    def tick(self, fps=60):
        self.clock.tick(int(fps))