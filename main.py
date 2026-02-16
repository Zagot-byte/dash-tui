# main.py
import curses
import sys
from game import Game

def main(stdscr):
    """Main entry point - initializes curses and runs game loop."""
    # Curses setup
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Non-blocking input
    stdscr.timeout(0)   # No input delay
    
    # Initialize game
    game = Game(stdscr)
    
    # Run game loop
    try:
        game.run()
    except KeyboardInterrupt:
        pass  # Clean exit on Ctrl+C

if __name__ == "__main__":
    curses.wrapper(main)
