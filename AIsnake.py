"""
Usage:
    AIsnake.py [--board_dim=<d>] [--search=<s>] [--num_obstacles=<n>] [--goal_target=<g>] [--fps=<fps>]

Options:
    --board_dim=<d>      Integer n that specifies the nxn board size [default: 20].
    --search=<s>         Search type; must be one of 'bfs', 'dfs', 'manhattan', 'euclidean', 'avg' [default: bfs].
    --num_obstacles=<n>  Number of impassable obstacles to randomly place on the map [default: 2].
    --goal_target=<g>    Integer that specifies the number of food to be eaten before simulation ends [default: 5].
    --fps=<fps>          Wait time in between prints of path to goal state [default: 0.8].
"""

import pdb
import copy
import time
import os
from docopt import docopt

from state import (
    State, FOOD
)
from search import (
    breadth_first_search, depth_first_search, a_star_search,
    return_manhattan_distance, return_euclidean_distance,
    return_average_of_distance_heuristics
)

KEYWORD_SEARCHTYPE_MAP = {
    'dfs': (depth_first_search, None),
    'bfs': (breadth_first_search, None),
    'manhattan': (a_star_search, return_manhattan_distance),
    'euclidean': (a_star_search, return_euclidean_distance),
    'avg': (a_star_search, return_average_of_distance_heuristics)
}


def print_benchmark_results(stats_mapping):
    # We subtract 2 because the mapping contains search_type, board_dim, num_obstacles as keys
    num_iterations = len(stats_mapping.keys()) - 3
    total_nodes_processed = 0
    total_time = 0
    total_failures = 0

    for i in range(num_iterations):
        if stats_mapping[i]['failed']:
            total_failures += 1
            continue
        else:
            total_nodes_processed += stats_mapping[i]['num_nodes_processed']
            total_time += stats_mapping[i]['time']

    average_nodes_processed = float(total_nodes_processed)/(num_iterations-total_failures)
    average_time = float(total_time)/(num_iterations-total_failures)

    return_str = 'For search type {0} {1} iterations\n'.format(
        stats_mapping['search_type'], num_iterations
    )
    return_str += 'On dimension {0}x{0} grid with {1} obstacles\n'.format(
        stats_mapping['board_dim'], stats_mapping['num_obstacles']
    )
    return_str += 'Averaged {0} nodes processed per iteration\n'.format(average_nodes_processed)
    return_str += 'with an average of {0} seconds per iteration\n'.format(average_time)
    return_str += 'with {0} failures\n\n'.format(total_failures)

    print return_str
    return return_str


def print_successful_path(goal_node, list_of_processed_nodes, fps):
    """
    Once the goal node is found, we can traverse back up the tree using the node's parent attribute
    to print the path that leads the snake from the initial state to the goal state
    """
    list_of_nodes_to_print = []
    done_traversing = False
    curr_node = goal_node

    while not done_traversing:
        list_of_nodes_to_print.append(curr_node)
        if curr_node.parent_index == None:
            break
        else:
            parent_of_curr_node = None
            for node in list_of_processed_nodes:
                if curr_node.parent_index == node.index:
                    parent_of_curr_node = node
        curr_node = parent_of_curr_node

    print '-'*40
    for node in reversed(list_of_nodes_to_print):
        print '-'*40
        node.state.print_grid()
        print '-'*40
        time.sleep(fps)
    print '-'*40


def main(board_dim, search_args, num_obstacles, target, fps):
    search_type, heuristic_fn = search_args
    # Initialize metrics map
    iteration_stats_map = {
        'search_type': search_args,
        'board_dim': board_dim,
        'num_obstacles': num_obstacles
    }
    for i in range(target):
        iteration_stats_map[i] = {}

    curr_state = State(dim=board_dim, num_obstacles=num_obstacles)
    # Run the search
    food_eaten = 0
    while food_eaten < target:
        time_taken = 0
        iteration_stats_map[food_eaten]['failed'] = False
        curr_state.print_grid()
        try:
            start_time = time.time()
            if heuristic_fn:
                goal_node, list_of_processed_nodes = search_type(initial_state=curr_state, heuristic_function=heuristic_fn)
            else:
                goal_node, list_of_processed_nodes = search_type(initial_state=curr_state)
            end_time = time.time()
        # If we fail, all we have to do is record the failure (so that we can track it in our stats)
        # , and reinstiate a new board
        except SystemExit:
            iteration_stats_map[food_eaten]['failed'] = True
            curr_state = State(dim=board_dim, num_obstacles=num_obstacles)
            #fail_food_x, fail_food_y = curr_state.food_coords
            #curr_state.set_x_y_value_on_grid(x=fail_food_x, y=fail_food_y, value=None)
            #new_food_x, new_food_y = curr_state.randomly_place_item_on_grid(item='food')
            #curr_state.food_coords = (new_food_x, new_food_y)
            continue

        print_successful_path(
            goal_node=goal_node, list_of_processed_nodes=list_of_processed_nodes, fps=fps
        )
        # Record metrics
        iteration_stats_map[food_eaten]['time'] = end_time - start_time
        iteration_stats_map[food_eaten]['num_nodes_processed'] = len(list_of_processed_nodes)
        # Update state, point curr node pointer to the goal node, place new food
        goal_node.state.snake.update_self_after_eating()
        food_eaten += 1
        curr_state = copy.deepcopy(goal_node.state)
        curr_state.randomly_place_item_on_grid(item=FOOD)

    results = print_benchmark_results(stats_mapping=iteration_stats_map)

    return results


def run_all_searches_and_record_results(board_dim, num_obstacles, target):
    """
    Can't access this through the command line
    Must open up Python shell and call it
    """
    
    for key in ('bfs', 'dfs', 'manhattan', 'euclidean', 'avg'):
        search_args = KEYWORD_SEARCHTYPE_MAP[key]
        with open('results_new.txt', 'a') as f:
            results = main(
                board_dim=board_dim, search_args=search_args,
                num_obstacles=num_obstacles, target=target, fps=0
            )
            f.write(results)
    os.system('say -v "Victoria" "done"')


if __name__ == '__main__':
    args = docopt(__doc__)
    board_dim = int(args['--board_dim'])
    search = args['--search']
    num_obstacles = int(args['--num_obstacles'])
    goal_target = int(args['--goal_target'])
    fps = float(args['--fps'])

    if search not in ('bfs', 'dfs', 'manhattan', 'euclidean', 'avg'):
        print 'Search parameter must be one of: bfs, dfs, manhattan, euclidean, avg'
        os._exit(0)

    search_params = KEYWORD_SEARCHTYPE_MAP[search]

    main(
        board_dim=board_dim, search_args=search_params,
        num_obstacles=num_obstacles, target=goal_target, fps=fps
    )
