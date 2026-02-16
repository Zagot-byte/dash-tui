"""
Game - Core game state and update logic
Manages the main game loop, timing, scoring, and state transitions.
"""

import time
from player import Player
from level import Level
from renderer import Renderer

class Game:
    """Core game state and update logic."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.running = True
        self.game_over = False
        
        # Timing constants
        self.base_tick_interval = 0.050  # ~20 ticks per second (deliberate pace)
        self.tick_interval = self.base_tick_interval
        self.tick_counter = 0
        
        # Speed progression (very gradual)
        self.speed_multiplier = 1.0
        self.speed_increase_interval = 400  # Ticks between speed increases
        self.speed_increase_amount = 0.05
        self.max_speed_multiplier = 1.6
        
        # Score
        self.distance_score = 0
        self.best_score = 0
        
        # Get screen dimensions
        self.height, self.width = stdscr.getmaxyx()
        
        # Initialize components
        self.player = Player(self.height)
        self.level = Level(self.height, self.width)
        self.renderer = Renderer(stdscr, self.height, self.width)
        
    def run(self):
        """Main game loop with fixed tick timing."""
        while self.running:
            tick_start = time.time()
            
            self.handle_input()
            self.update()
            self.render()
            
            # Maintain constant tick rate
            elapsed = time.time() - tick_start
            sleep_time = self.tick_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def handle_input(self):
        """Non-blocking input — SPACE taps to jump, R restarts, Q quits."""
        try:
            key = self.stdscr.getch()
            
            if key == ord(' '):
                if not self.game_over:
                    self.player.tap_jump()

            elif key == ord('r') or key == ord('R'):
                if self.game_over:
                    self.reset()
                    
            elif key == ord('q') or key == ord('Q'):
                self.running = False
        except:
            pass
    
    def update(self):
        """Update game state."""
        if self.game_over:
            return
        
        # Update player
        self.player.update()
        
        # Scroll level
        self.level.scroll()
        
        # Check collision
        if self.check_collision():
            self.game_over = True
            if self.distance_score > self.best_score:
                self.best_score = self.distance_score
            return
        
        # Update score and speed
        self.tick_counter += 1
        self.distance_score = self.tick_counter // 10
        
        # Increase speed gradually
        if self.tick_counter % self.speed_increase_interval == 0:
            self.speed_multiplier = min(
                self.speed_multiplier + self.speed_increase_amount,
                self.max_speed_multiplier
            )
            self.tick_interval = self.base_tick_interval / self.speed_multiplier
    
    def check_collision(self):
        """Check if player collides with obstacle."""
        player_x = self.player.x
        player_y = int(self.player.y)  # Round to nearest grid position
        platform_row = self.height - 3
        
        # Check if player position has obstacle
        if self.level.has_obstacle_at(player_x, player_y):
            return True
        
        # Check if player fell into a gap (no platform below when on ground)
        if player_y >= platform_row:  # Player is at or below platform level
            # Check if there's actually a platform
            platform_char = self.level.get_char_at(player_x, platform_row)
            if platform_char == ' ':
                # Player is over a gap with no platform
                return True
        
        return False
    
    def render(self):
        """Render current game state."""
        self.renderer.clear()
        self.renderer.draw_hud(
            self.distance_score,
            self.best_score,
            self.speed_multiplier,
            self.game_over,
            self.player.get_stamina_display()
        )
        self.renderer.draw_level(self.level)
        self.renderer.draw_player(self.player)
        # Draw game over LAST so nothing overlaps it
        if self.game_over:
            self.renderer.draw_game_over()
        self.renderer.refresh()
    
    def reset(self):
        """Reset game state for new run."""
        self.game_over = False
        self.tick_counter = 0
        self.distance_score = 0
        self.speed_multiplier = 1.0
        self.tick_interval = self.base_tick_interval
        
        # Reset components
        self.player.reset(self.height)
        self.level.reset()
