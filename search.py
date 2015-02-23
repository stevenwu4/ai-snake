import pdb
import collections
import copy
import sys
import math
import heapq

from node import Node, AStarNode
from state import State

"""
Uninformed searches
"""

def generate_children_nodes(
    curr_node, list_of_processed_nodes,
    running_count_of_children_dups, a_star_search=False
):
    """
    1. Look at current node's state
    2. Analyze the legal moves; up, down, left, right
    3. For each legal move,
    build a new node that contains the new state, linking the parent of the new node
    to be the current node
    4. Add built node to a list to return
    5. Return the list
    """
    children_nodes_to_return = []
    direction_coordinates_map = curr_node.state.get_legal_snake_movement_coords()
    
    for direction, legal_coords in direction_coordinates_map.iteritems():
        curr_state_copy = copy.deepcopy(curr_node.state)
        new_state = State(
            dim=curr_state_copy.dim, num_obstacles=curr_state_copy.num_obstacles,
            grid=curr_state_copy.grid, snake=curr_state_copy.snake
        )
        #pdb.set_trace()#
        new_state.update_state_after_movement(new_head_coords=legal_coords)

        new_node_state = new_state
        new_node_action = direction
        new_node_parent_index = curr_node.index
        new_node_depth = curr_node.depth + 1

        new_node = Node(
            state=new_node_state, action=new_node_action,
            parent_index=new_node_parent_index, depth=new_node_depth
        )

        if not a_star_search:
            if new_node in list_of_processed_nodes:
                running_count_of_children_dups += 1
                continue

        children_nodes_to_return.append(new_node)

    return children_nodes_to_return, running_count_of_children_dups


def breadth_first_search(initial_state):
    """
    Fringe of tree is a FIFO queue (new successors go to the end)
    """
    list_of_processed_nodes = []
    num_unprocessed_nodes = 0#
    num_unconsidered_children = 0#

    initial_node = Node(state=initial_state)
    node_deque = collections.deque()
    node_deque.append(initial_node)
    goal_state_found = False
    goal_node = None

    while len(node_deque) > 0 and not goal_state_found:
        e = node_deque.popleft()
        #pdb.set_trace()
        if e in list_of_processed_nodes:
            num_unprocessed_nodes += 1
            continue
        else:
            list_of_processed_nodes.append(e)

        list_of_children_nodes, num_unconsidered_children = generate_children_nodes(
            curr_node=e, list_of_processed_nodes=list_of_processed_nodes,
            running_count_of_children_dups=num_unconsidered_children#
        )
        
        for child_node in list_of_children_nodes:
            #print 'Node {0} with goal status {1}'.format(child_node.index, child_node.state.snake_ate_food)
            if child_node.state.goal_state_reached():
                #print "Goal state reached with node index {0}".format(child_node.index)
                goal_state_found = True
                goal_node = child_node
                break
            else:
                #print "Adding to deque node index {0}".format(child_node.index)
                node_deque.append(child_node)

    if len(node_deque) == 0 and not goal_state_found:
        print '*'*40
        print 'NO SOLUTION PATH FOUND'
        print '*'*40
        sys.exit(0)

    #pdb.set_trace()#
    # Summary & results
    #print '{0} nodes processed!'.format(len(list_of_processed_nodes))
    #print '{0} nodes already visited, skipped!'.format(num_unprocessed_nodes)
    #print '{0} node children skipped!'.format(num_unconsidered_children)
    #os.system('say -v "Victoria" "done"')

    return goal_node, list_of_processed_nodes


def depth_first_search(initial_state):
    list_of_processed_nodes = []
    num_unprocessed_nodes = 0#
    num_unconsidered_children = 0#

    initial_node = Node(state=initial_state)
    node_deque = collections.deque()
    node_deque.append(initial_node)
    goal_state_found = False
    goal_node = None

    while len(node_deque) > 0 and not goal_state_found:
        e = node_deque.popleft()
        #print "Popped node, index: {0}".format(e.index)
        #pdb.set_trace()
        if e in list_of_processed_nodes:
            num_unprocessed_nodes += 1
            continue
        else:
            list_of_processed_nodes.append(e)
        
        list_of_children_nodes, num_unconsidered_children = generate_children_nodes(
            curr_node=e, list_of_processed_nodes=list_of_processed_nodes,
            running_count_of_children_dups=num_unconsidered_children#
        )
        
        for child_node in list_of_children_nodes:
            #print 'Node {0} with goal status {1}'.format(child_node.index, child_node.state.snake_ate_food)
            if child_node.state.goal_state_reached():
                #print "Goal state reached with node index {0}".format(child_node.index)
                goal_state_found = True
                goal_node = child_node
                break
            else:
                #print "Adding to deque node index {0}".format(child_node.index)
                node_deque.appendleft(child_node)

    if len(node_deque) == 0 and not goal_state_found:
        print '*'*40
        print 'NO SOLUTION PATH FOUND'
        print '*'*40
        sys.exit(0)

    #pdb.set_trace()#
    # Summary & results
    #print '{0} nodes processed!'.format(len(list_of_processed_nodes))
    #print '{0} nodes already visited, skipped!'.format(num_unprocessed_nodes)
    #print '{0} node children skipped!'.format(num_unconsidered_children)
    #os.system('say -v "Victoria" "done"')

    return goal_node, list_of_processed_nodes

"""
A* searches
"""        
def return_manhattan_distance(coord1, coord2):
    """
    Manhattan distance is appropriate when
    n+1 movements in the x axis, n-1 movements in the y axis
    is the same as 
    n movements in the x axis, n movements in the y axis
    """
    x1, y1 = coord1
    x2, y2 = coord2

    return float(abs(x2-x1) + abs(y2-y1))


def return_euclidean_distance(coord1, coord2):
    """
    The most intuitive heuristic: take the hypotenuse, or straight line
    distance, between the two points
    """
    x1, y1 = coord1
    x2, y2 = coord2

    x_dist_sq = math.pow((x2-x1), 2)
    y_dist_sq = math.pow((y2-y1), 2)

    return math.sqrt(x_dist_sq + y_dist_sq)


def return_average_of_distance_heuristics(
    coord1, coord2, heuristic1=return_manhattan_distance,
    heuristic2=return_euclidean_distance
):
    heur1 = heuristic1(coord1, coord2)
    heur2 = heuristic2(coord1, coord2)

    return (heur1 + heur2)/2


def a_star_search(initial_state, heuristic_function):
    """
    We use the heapq module to treat the list, open_list, as a
    priority queue
    """
    open_priorityqueue = []
    open_list = []
    list_of_processed_nodes = []
    num_unprocessed_nodes = 0
    num_unconsidered_children = 0

    initial_node = AStarNode(state=initial_state)
    heapq.heappush(open_priorityqueue, (initial_node.f, initial_node))
    open_list.append(initial_node)
    goal_state_found = False
    goal_node = None

    while len(open_list) > 0 and not goal_state_found:
        best_node_cost, best_node = heapq.heappop(open_priorityqueue)
        open_list.remove(best_node)
        list_of_processed_nodes.append(best_node)

        if best_node.state.goal_state_reached():
            print "Goal state reached with node index {0}".format(best_node.index)
            goal_state_found = True
            goal_node = best_node
            break

        list_of_children_nodes, num_unconsidered_children = generate_children_nodes(
            curr_node=best_node, list_of_processed_nodes=list_of_processed_nodes,
            running_count_of_children_dups=num_unconsidered_children, a_star_search=True
        )
        
        for i, child_node in enumerate(list_of_children_nodes):
            evaluate_child_node(
                parent_node=best_node, child_node=child_node,
                heuristic_function=heuristic_function
            )
            if (child_node not in open_list) and (child_node not in list_of_processed_nodes):
                heapq.heappush(open_priorityqueue, (child_node.f, child_node))
                open_list.append(child_node)
            else:
                open_matches = [n for n in open_list if child_node == n]
                closed_matches = [n for n in list_of_processed_nodes if child_node == n]
                matches = open_matches + closed_matches
                seen_node = matches[0]
                #If it's in open or closed, check if new path is better than prev path
                if (child_node.f < seen_node.f):
                    seen_node.parent_index = child_node.parent_index
                    seen_node.g = child_node.g
                    seen_node.h = child_node.h
                    seen_node.f = child_node.f
                    children_nodes_of_child = get_all_nodes_children(
                        node=child_node,
                        list_of_potential_children_nodes=open_list+list_of_processed_nodes
                    )
                    #print len(children_nodes_of_child)
                    #pdb.set_trace()
                    for c in children_nodes_of_child:
                        c_old_f = c.f
                        evaluate_child_node(
                            parent_node=child_node,
                            child_node=c,
                            heuristic_function=heuristic_function
                        )
                        if c in open_list:
                            open_priorityqueue.remove((c_old_f, c))
                            open_list.remove(c)
                            heapq.heappush(open_priorityqueue, (c.f, c))
                            open_list.append(c)
                        else:
                            list_of_processed_nodes.remove(c)
                            list_of_processed_nodes.append(c)

    if len(open_list) == 0 and not goal_state_found:
        print '*'*40
        print 'NO SOLUTION PATH FOUND'
        print '*'*40
        sys.exit(0)

    return goal_node, list_of_processed_nodes


def evaluate_child_node(parent_node, child_node, heuristic_function):
    h_n = heuristic_function(
        coord1=child_node.state.snake.get_head_coords(),
        coord2=child_node.state.food_coords
    )
    child_node.g = parent_node.g + 1
    child_node.h = h_n
    child_node.f = child_node.g + child_node.h

    return
    

def get_all_nodes_children(node, list_of_potential_children_nodes):
    return [n for n in list_of_potential_children_nodes if n.parent_index == node.index]
