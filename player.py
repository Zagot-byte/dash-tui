"""
Player - Tap-based jump with stamina system
Each SPACE tap = fixed upward impulse. Stamina limits consecutive jumps.
Stamina recharges while on the ground.
"""

import time


class Player:
    """Player with tap jump and stamina system."""

    def __init__(self, screen_height):
        self.screen_height = screen_height
        self.x = 5  # Fixed horizontal position
        self.reset(screen_height)

    def reset(self, screen_height):
        """Reset player state."""
        self.screen_height = screen_height
        self.ground_y = screen_height - 3  # Platform layer
        self.y = float(self.ground_y)

        # Physics
        self.velocity_y = 0.0
        self.gravity = 0.8               # Gravity (user-tuned)
        self.jump_impulse = -3.5         # Fixed upward impulse per tap
        self.max_height = 3              # Hard ceiling row

        # Jump state
        self.on_ground = True

        # Stamina system
        self.max_stamina = 5
        self.stamina = self.max_stamina

        # Air-push particles (visual only)
        # Each particle: [x, y, lifetime]  (lifetime counts down)
        self.air_particles = []

        # Jump cooldown (prevent accidental double-tap)
        self.last_jump_time = 0.0
        self.jump_cooldown = 0.03

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def tap_jump(self):
        """SPACE tapped — apply fixed upward impulse if stamina available.
        Works on ground AND mid-air (costs stamina either way)."""
        # Must have stamina
        if self.stamina <= 0:
            return False

        # Enforce cooldown
        now = time.time()
        if now - self.last_jump_time < self.jump_cooldown:
            return False

        # Detect mid-air jump for particles
        was_airborne = not self.on_ground

        # Jump! (resets velocity — not additive)
        self.velocity_y = self.jump_impulse
        self.on_ground = False
        self.stamina -= 1
        self.last_jump_time = now

        # Spawn air-push particles on mid-air jumps
        if was_airborne:
            py = int(self.y)
            # Burst of particles below the player
            self.air_particles.append([self.x, py + 1, 4])     # ↓ right below
            self.air_particles.append([self.x - 1, py + 1, 3]) # left
            self.air_particles.append([self.x + 1, py + 1, 3]) # right
            self.air_particles.append([self.x, py + 2, 2])     # further below

        return True

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def update(self):
        """Update position with gravity. Tick air particles."""
        # Tick particles
        self.air_particles = [
            [x, y, life - 1] for x, y, life in self.air_particles if life > 1
        ]

        if not self.on_ground:
            # Apply gravity
            self.velocity_y += self.gravity

            # Update position
            self.y += self.velocity_y

            # Hard ceiling cap
            if self.y < self.max_height:
                self.y = float(self.max_height)
                self.velocity_y = 0.0

            # Ground landing — full stamina recharge
            if self.y >= self.ground_y:
                self.y = float(self.ground_y)
                self.velocity_y = 0.0
                self.on_ground = True
                self.stamina = self.max_stamina  # Full recharge on touch

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def get_char(self):
        """Return character to display for player."""
        if not self.on_ground:
            return '◉'  # Airborne
        if self.stamina <= 0:
            return '○'  # Exhausted (no stamina)
        return '●'      # Grounded

    def get_stamina_display(self):
        """Return stamina bar string for HUD."""
        filled = '■' * self.stamina
        empty = '□' * (self.max_stamina - self.stamina)
        return f"[{filled}{empty}]"
