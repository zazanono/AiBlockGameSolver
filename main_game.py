import ai_solver
import random
import time

# --- Constants ---
GRID_WIDTH = 8
GRID_HEIGHT = 8
EMPTY_CELL = '.'
BLOCK_CELL = '■'

# --- Piece Generation ---

# Base shapes are the canonical forms before any rotation.
# These will be used to generate new pieces dynamically.
BASE_SHAPES = [
    # Line Blocks
    [[0, 0], [0, 1]],  # 1x2
    [[0, 0], [0, 1], [0, 2]],  # 1x3
    [[0, 0], [0, 1], [0, 2], [0, 3]],  # 1x4
    [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]],  # 1x5

    # Square Blocks
    [[0, 0], [0, 1], [1, 0], [1, 1]],  # 2x2
    [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]],  # 3x3

    # L-Shaped Blocks
    [[0, 0], [1, 0], [1, 1]],  # 2x2 L-shape (3 blocks)
    [[0, 0], [1, 0], [2, 0], [2, 1]],  # L-shape (4 blocks)
    [[0, 0], [1, 0], [2, 0], [2, 1], [2, 2]],  # L-shape (5 blocks)

    # T-Shaped Blocks
    [[0, 1], [1, 0], [1, 1], [1, 2]],  # T-shape (4 blocks)

    # Rectangle Blocks
    [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]],  # 2x3 solid rectangle

    # S-Shaped Blocks
    [[0, 1], [0, 2], [1, 0], [1, 1]],  # S-shape (4 blocks)
]


def rotate_piece(piece_shape):
    """Rotates a piece 90 degrees clockwise using matrix rotation."""
    return [(c, -r) for r, c in piece_shape]


def normalize_piece(piece_shape):
    """Shifts a piece so its top-leftmost coordinate is at (0,0)."""
    if not piece_shape:
        return []
    min_r = min(r for r, c in piece_shape)
    min_c = min(c for r, c in piece_shape)
    return sorted([(r - min_r, c - min_c) for r, c in piece_shape])


# --- Game Functions ---

def create_grid():
    """Creates an empty 8x8 game grid."""
    return [[EMPTY_CELL for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def get_new_pieces():
    """
    Generates 3 new random pieces for the player.
    Each piece is a randomly chosen base shape with a random rotation,
    created dynamically each time this function is called.
    """
    new_pieces = []
    for _ in range(3):
        # 1. Select a random base shape
        shape = random.choice(BASE_SHAPES)

        # 2. Apply a random number of rotations (0 to 3)
        num_rotations = random.randint(0, 3)
        for _ in range(num_rotations):
            shape = rotate_piece(shape)

        # 3. Normalize the final shape to align it to the top-left
        final_shape = normalize_piece(shape)

        # 4. Add the dynamically generated piece to the list
        new_pieces.append({'shape': final_shape, 'placed': False})

    return new_pieces


def print_available_pieces(pieces):
    """Prints a visual representation of the 3 available pieces."""
    print("--- Available Pieces ---")
    piece_grids, max_lines = [], 0

    for i, p_info in enumerate(pieces):
        text_lines = []
        if p_info['placed']:
            text_lines.append(f"Piece {i + 1}: Placed")
        else:
            shape = p_info['shape']
            max_r = max(r for r, c in shape) if shape else -1
            max_c = max(c for r, c in shape) if shape else -1
            grid = [[' ' for _ in range(max_c + 1)] for _ in range(max_r + 1)]
            for r, c in shape:
                grid[r][c] = BLOCK_CELL
            text_lines.append(f"Piece {i + 1} ({len(shape)} blocks):")
            text_lines.extend([" ".join(row) for row in grid])

        piece_grids.append(text_lines)
        if len(text_lines) > max_lines:
            max_lines = len(text_lines)

    for i in range(max_lines):
        line_to_print = ""
        for grid_lines in piece_grids:
            line = grid_lines[i] if i < len(grid_lines) else ""
            line_to_print += line.ljust(25)
        print(line_to_print)
    print("-" * 75)


def print_board(grid, score):
    """Prints the game board and score."""
    print(f"SCORE: {score}\n")
    header = '   ' + ' '.join(map(str, range(GRID_WIDTH)))
    print(header)
    print('  ' + '-' * (GRID_WIDTH * 2 + 1))

    for i, row in enumerate(grid):
        print(f"{i} | {' '.join(row)} |")
    print('  ' + '-' * (GRID_WIDTH * 2 + 1))


def is_valid_placement(grid, piece_shape, r_start, c_start):
    """Checks if a piece can be placed at the given coordinates."""
    for r_offset, c_offset in piece_shape:
        r, c = r_start + r_offset, c_start + c_offset
        if not (0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH and grid[r][c] == EMPTY_CELL):
            return False
    return True


def place_piece(grid, piece_shape, r_start, c_start):
    """Places a piece on the grid and returns the number of blocks placed."""
    for r_offset, c_offset in piece_shape:
        grid[r_start + r_offset][c_start + c_offset] = BLOCK_CELL
    return len(piece_shape)


def find_and_clear_lines(grid):
    """Checks for and clears completed rows and columns, returning count."""
    rows_to_clear = [r for r in range(GRID_HEIGHT) if all(cell == BLOCK_CELL for cell in grid[r])]
    cols_to_clear = [c for c in range(GRID_WIDTH) if all(grid[r][c] == BLOCK_CELL for r in range(GRID_HEIGHT))]

    for r in rows_to_clear:
        grid[r] = [EMPTY_CELL for _ in range(GRID_WIDTH)]
    for c in cols_to_clear:
        for r in range(GRID_HEIGHT):
            grid[r][c] = EMPTY_CELL

    return len(rows_to_clear) + len(cols_to_clear)


def can_any_piece_be_placed(grid, pieces):
    """Checks if any available piece can fit on the board."""
    for piece_info in pieces:
        if not piece_info['placed']:
            for r in range(GRID_HEIGHT):
                for c in range(GRID_WIDTH):
                    if is_valid_placement(grid, piece_info['shape'], r, c):
                        return True
    return False


def main():
    """The main game loop."""
    grid = create_grid()
    score = 0
    available_pieces = get_new_pieces()

    while True:
        print_board(grid, score)
        print_available_pieces(available_pieces)

        print("\nCalculating best move...")
        suggested_sequence = ai_solver.find_best_move_sequence(grid, available_pieces)

        if suggested_sequence:
            print("AI Suggestion:")
            for piece_idx, r, c in suggested_sequence:
                print(f"  - Place Piece {piece_idx + 1} at (Row: {r}, Col: {c})")
        else:
            print("AI could not find a valid move sequence.")

        if not can_any_piece_be_placed(grid, available_pieces):
            print("\n--- GAME OVER ---")
            print("No more possible moves.")
            print(f"Final Score: {score}")
            break

        try:
            choice_str = input("Enter piece (1-3), row, col (e.g., '1 4 2') or 'q' to quit: ")
            if choice_str.lower() in ['q', 'quit', 'exit']:
                print("Quitting game. Thanks for playing!")
                break

            parts = []
            for char in choice_str:
                if char != ' ':
                    parts.append(int(char))

            # parts = choice_str.split()
            if len(parts) != 3: raise ValueError("Invalid format.")

            piece_idx, row, col = [int(p) for p in parts]
            piece_idx -= 1

            if not (0 <= piece_idx < 3): raise ValueError("Piece choice must be 1, 2, or 3.")
            if available_pieces[piece_idx]['placed']: raise ValueError("That piece is already placed.")

            piece_to_place = available_pieces[piece_idx]['shape']

            if is_valid_placement(grid, piece_to_place, row, col):
                score += place_piece(grid, piece_to_place, row, col)
                available_pieces[piece_idx]['placed'] = True

                lines_cleared = find_and_clear_lines(grid)
                if lines_cleared > 0:
                    score += lines_cleared * 10 * lines_cleared  # Quadratic bonus
                    print_board(grid, score)
                    print(f"\nCleared {lines_cleared} line(s)! Bonus points awarded!")
                    time.sleep(1.5)

                if all(p['placed'] for p in available_pieces):
                    print("\nGenerating new pieces...")
                    time.sleep(1)
                    available_pieces = get_new_pieces()
            else:
                print("\n!!! Invalid placement: Piece is out of bounds or overlaps. !!!")
                time.sleep(1.5)

        except (ValueError, IndexError) as e:
            print(f"\n!!! Invalid input: {e}. Please try again. !!!")
            time.sleep(1.5)


if __name__ == "__main__":
    main()