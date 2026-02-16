"""
Level - Grid management and fair randomized obstacle generation
All obstacles are clearable with a single tap jump. No impossible combos.
"""

import random


class Level:
    """Level grid with scrolling and fair random obstacle generation."""

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.grid_width = width - 1

        # Background decoration
        self.star_positions = []
        self.cloud_positions = []
        self.bg_scroll_counter = 0

        # Random obstacle generation
        self.rng = random.Random()
        self.gap_counter = 0
        self.columns_until_next = 0
        self.double_spike_remaining = 0

        # Fair obstacle pool — all clearable with a single tap jump
        # Weights control how often each appears
        self.obstacle_types = [
            ('spike',         35),   # Most common — single spike
            ('double_spike',  12),   # Two spikes close together
            ('low_block',     25),   # 2 units tall
            ('mid_block',     10),   # 3 units tall (still clearable)
            ('gap',           18),   # Platform gap (3-4 cols)
        ]
        self._build_weighted_pool()

        # Spacing — balanced: not too sparse, not too cramped
        self.min_spacing = 14
        self.max_spacing = 22

        self.reset()

    def _build_weighted_pool(self):
        """Build flat list for weighted random selection."""
        self.pool = []
        for name, weight in self.obstacle_types:
            self.pool.extend([name] * weight)

    def reset(self):
        """Reset level state."""
        self.grid = self._create_empty_grid()
        self.columns_until_next = 20   # Safe start zone
        self.gap_counter = 0
        self.double_spike_remaining = 0
        self.bg_scroll_counter = 0
        self.rng = random.Random()

        self._init_background()

        for _ in range(self.grid_width):
            self._add_column()

    def _init_background(self):
        """Initialize stars and clouds."""
        bg_rng = random.Random(42)

        self.star_positions = []
        for _ in range(15):
            x = bg_rng.randint(0, self.grid_width - 1)
            y = bg_rng.randint(1, self.height // 3)
            self.star_positions.append([x, y])

        self.cloud_positions = []
        for _ in range(5):
            x = bg_rng.randint(0, self.grid_width - 1)
            y = bg_rng.randint(1, self.height // 2)
            width = bg_rng.randint(3, 6)
            self.cloud_positions.append([x, y, width])

    def _create_empty_grid(self):
        """Create empty grid."""
        grid = []
        for y in range(self.height):
            grid.append([' '] * self.grid_width)

        ground_row = self.height - 2
        platform_row = self.height - 3

        for x in range(self.grid_width):
            grid[ground_row][x] = '='
            grid[platform_row][x] = '─'

        return grid

    def scroll(self):
        """Scroll level left and add new column."""
        for y in range(self.height):
            self.grid[y] = self.grid[y][1:] + [' ']

        self.bg_scroll_counter += 1
        if self.bg_scroll_counter % 3 == 0:
            for star in self.star_positions:
                star[0] -= 1
                if star[0] < 0:
                    star[0] = self.grid_width - 1

        if self.bg_scroll_counter % 2 == 0:
            for cloud in self.cloud_positions:
                cloud[0] -= 1
                if cloud[0] < -cloud[2]:
                    cloud[0] = self.grid_width - 1

        self._add_column()

    def _add_column(self):
        """Add new column with fair random obstacles."""
        ground_row = self.height - 2
        platform_row = self.height - 3

        # Handle active gap
        if self.gap_counter > 0:
            self.grid[ground_row][-1] = ' '
            self.grid[platform_row][-1] = ' '
            self.gap_counter -= 1
            return

        # Handle double spike follow-up
        if self.double_spike_remaining > 0:
            self.double_spike_remaining -= 1
            self.grid[ground_row][-1] = '='
            self.grid[platform_row][-1] = '─'
            if self.double_spike_remaining == 0:
                self.grid[platform_row][-1] = '▲'
            return

        # Default: ground + platform
        self.grid[ground_row][-1] = '='
        self.grid[platform_row][-1] = '─'

        self.columns_until_next -= 1

        if self.columns_until_next <= 0:
            element_type = self.rng.choice(self.pool)
            self._place_obstacle(element_type, platform_row, ground_row)
            self.columns_until_next = self.rng.randint(self.min_spacing, self.max_spacing)

    def _place_obstacle(self, element_type, platform_row, ground_row):
        """Place a fair obstacle at the rightmost column."""
        if element_type == 'spike':
            self.grid[platform_row][-1] = '▲'

        elif element_type == 'double_spike':
            self.grid[platform_row][-1] = '▲'
            self.double_spike_remaining = 3  # 3 cols gap then second spike

        elif element_type == 'low_block':
            # 2 units high — easily clearable
            self.grid[platform_row][-1] = '█'
            if platform_row - 1 >= 1:
                self.grid[platform_row - 1][-1] = '█'

        elif element_type == 'mid_block':
            # 3 units high — clearable with tap jump
            self.grid[platform_row][-1] = '█'
            for i in range(1, 3):
                if platform_row - i >= 1:
                    self.grid[platform_row - i][-1] = '█'

        elif element_type == 'gap':
            gap_size = self.rng.randint(3, 4)  # Small gaps only
            self.gap_counter = gap_size
            self.grid[ground_row][-1] = ' '
            self.grid[platform_row][-1] = ' '

    def has_obstacle_at(self, x, y):
        """Check if obstacle exists at position."""
        if x < 0 or x >= self.grid_width:
            return False
        if y < 0 or y >= self.height:
            return False
        return self.grid[y][x] in ['█', '▲', '◆']

    def get_char_at(self, x, y):
        """Get character at grid position."""
        if x < 0 or x >= self.grid_width:
            return ' '
        if y < 0 or y >= self.height:
            return ' '
        return self.grid[y][x]

    def get_background_elements(self):
        """Get background stars and clouds for rendering."""
        return {
            'stars': self.star_positions,
            'clouds': self.cloud_positions
        }
