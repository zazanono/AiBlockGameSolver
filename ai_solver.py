import main_game
import copy
import itertools

from main_game import EMPTY_CELL, BLOCK_CELL

# Weights:
WEIGHT_LINES_CLEARED = 2000     # Primary objective
WEIGHT_FILLED_CELLS = -10       # Keep the board as empty as possible
WEIGHT_CLUSTERING = 20          # Penalize fragmented unusable space
BONUS_ALL_CLEAR = 10000         # All clear board is ideal


def find_best_outcome_recursive(current_grid, all_pieces, piece_order, depth):
    if depth == len(piece_order):
        return evaluate_board(current_grid, 0), []
    if depth < len(piece_order):

        best_score_step = -float('inf')
        best_sub_sequence = []
        piece_index = (piece_order[depth])
        piece_info = all_pieces[piece_index]
        piece_shape = piece_info['shape']

        possible_placements = find_all_possible_placements(current_grid, piece_shape)

        for r, c in possible_placements:
            temp_grid = copy.deepcopy(current_grid)
            main_game.place_piece(temp_grid, piece_shape, r, c)

            lines_cleared = main_game.find_and_clear_lines(temp_grid)
            move_score = (lines_cleared ** 2) * WEIGHT_LINES_CLEARED

            score_future_moves, future_sequence = find_best_outcome_recursive(temp_grid, all_pieces,
                                                                              piece_order, depth + 1)

            total_score = move_score + score_future_moves

            if total_score > best_score_step:
                best_score_step = total_score
                best_sub_sequence = [(piece_index, r, c)] + future_sequence

        return best_score_step, best_sub_sequence


def find_best_move_sequence(grid, pieces):
    best_overall_sequence = None
    best_overall_score = -float('inf')

    available_piece_indices = []
    for i, piece_data in enumerate(pieces):
        if not piece_data['placed']:
            available_piece_indices.append(i)

    for pieces_order in itertools.permutations(available_piece_indices):
        current_score, current_sequence = find_best_outcome_recursive(grid, pieces, pieces_order, 0)

        if current_score > best_overall_score:
            best_overall_score = current_score
            best_overall_sequence = current_sequence

    return best_overall_sequence


def count_filled_cells(grid):
    filled_cells = 0
    for col in range(main_game.GRID_HEIGHT):
        for row in range(main_game.GRID_WIDTH):
            if grid[row][col] == BLOCK_CELL:
                filled_cells += 1

    return filled_cells


def check_surrounding_cells(grid, row, col):
    """Checks the 4 direct neighbors (up, down, left, right) of a cell."""
    num_of_blocks = 0
    positions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # (row_offset, col_offset)

    for r_offset, c_offset in positions:
        check_row, check_col = row + r_offset, col + c_offset
        is_in_bounds = (0 <= check_row < main_game.GRID_HEIGHT) and \
                       (0 <= check_col < main_game.GRID_WIDTH)

        if is_in_bounds and grid[check_row][check_col] == main_game.BLOCK_CELL:
            num_of_blocks += 1

    return num_of_blocks

def check_block_clusters(grid):
    """
    Calculates a score based on how tightly packed the blocks are.
    A higher score means more blocks are adjacent to each other.
    """
    cluster_score = 0
    for row in range(main_game.GRID_HEIGHT):
        for col in range(main_game.GRID_WIDTH):
            if grid[row][col] == main_game.BLOCK_CELL:
                cluster_score += check_surrounding_cells(grid, row, col)
    return cluster_score

def evaluate_board(grid, lines_cleared):
    score = 0

    # All clear
    filled_cells = count_filled_cells(grid)
    if filled_cells == 0:
        return BONUS_ALL_CLEAR

    # Clearing lines
    score += WEIGHT_LINES_CLEARED * (lines_cleared ** 2)

    # Penalty for remaining blocks
    score += WEIGHT_FILLED_CELLS * filled_cells

    # Block clustering
    score += WEIGHT_CLUSTERING * check_block_clusters(grid)

    return score


def find_all_possible_placements(grid, piece_shape):
    """
    Scans the entire grid and returns a list of (row, col) tuples
    where the given piece can be legally placed.
    """
    valid_placements = []

    if not piece_shape:
        return []
    piece_height = max(r for r, c in piece_shape) + 1
    piece_width = max(c for r, c in piece_shape) + 1

    for row in range(main_game.GRID_HEIGHT - piece_height + 1):
        for col in range(main_game.GRID_WIDTH - piece_width + 1):
            if main_game.is_valid_placement(grid, piece_shape, row, col):
                valid_placements.append((row, col))

    return valid_placements