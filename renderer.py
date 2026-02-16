"""
Renderer - Display logic
Handles all screen drawing operations without mutating game state.
"""

class Renderer:
    """Handles all rendering to screen."""
    
    def __init__(self, stdscr, height, width):
        self.stdscr = stdscr
        self.height = height
        self.width = width
    
    def clear(self):
        """Clear screen buffer."""
        self.stdscr.clear()
    
    def refresh(self):
        """Refresh screen display."""
        try:
            self.stdscr.refresh()
        except:
            pass  # Ignore refresh errors
    
    def draw_hud(self, score, best_score, speed, game_over, stamina_display=""):
        """Draw HUD at top of screen."""
        try:
            hud_left = f"Score: {score}  Best: {best_score}  Speed: {speed:.1f}x"
            hud_right = f"Stamina {stamina_display}"
            self.stdscr.addstr(0, 1, hud_left)
            # Right-align stamina
            right_x = max(len(hud_left) + 4, self.width - len(hud_right) - 2)
            if right_x < self.width - 1:
                self.stdscr.addstr(0, right_x, hud_right)
        except:
            pass
    
    def draw_game_over(self):
        """Draw game over text LAST so nothing overlaps it."""
        try:
            game_over_text = "GAME OVER - Press R to restart, Q to quit"
            x_pos = max(0, (self.width - len(game_over_text)) // 2)
            row = self.height // 2
            # Clear the row first so no background bleeds through
            self.stdscr.addstr(row, 0, ' ' * (self.width - 1))
            self.stdscr.addstr(row, x_pos, game_over_text)
        except:
            pass
    
    def draw_level(self, level):
        """Draw level grid with background."""
        # Draw background first
        bg_elements = level.get_background_elements()
        
        # Draw stars
        for star_x, star_y in bg_elements['stars']:
            if 0 <= star_x < level.grid_width and 1 <= star_y < self.height:
                try:
                    self.stdscr.addstr(star_y, star_x, '·')
                except:
                    pass
        
        # Draw clouds
        for cloud_x, cloud_y, cloud_width in bg_elements['clouds']:
            cloud_chars = ['~', '≈', '~']
            for i in range(cloud_width):
                x = cloud_x + i
                if 0 <= x < level.grid_width and 1 <= cloud_y < self.height:
                    try:
                        char = cloud_chars[i % len(cloud_chars)]
                        self.stdscr.addstr(cloud_y, x, char)
                    except:
                        pass
        
        # Draw foreground obstacles and platforms
        for y in range(1, self.height):  # Skip HUD row
            for x in range(level.grid_width):
                char = level.get_char_at(x, y)
                if char not in [' ', '·', '~', '≈']:  # Don't overwrite background
                    try:
                        self.stdscr.addstr(y, x, char)
                    except:
                        pass
    
    def draw_player(self, player):
        """Draw player character and air-push particles."""
        try:
            y_pos = int(player.y)
            self.stdscr.addstr(y_pos, player.x, player.get_char())
        except:
            pass

        # Draw air-push particles
        particle_chars = {4: '↓', 3: '∵', 2: '·', 1: '˙'}
        for px, py, life in player.air_particles:
            if 1 <= py < self.height - 1 and 0 <= px < self.width - 1:
                ch = particle_chars.get(life, '·')
                try:
                    self.stdscr.addstr(py, px, ch)
                except:
                    pass
