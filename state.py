import random
import pdb

from snake import Snake

FOOD = 'food'
OBSTACLE = 'obstacle'

ITEM_MAP = {
    FOOD: 'f',
    OBSTACLE: 'o'
}

class State():
    def __init__(self, dim, num_obstacles, grid=None, snake=None):
        self.dim = dim
        self.num_obstacles = num_obstacles
        # We either want to initialize a new state
        if not grid:
            self.grid = [[None for i in range(dim)] for _ in range(self.dim)]
            self.snake = Snake()
            self.place_snake()
            
            self.obst_coords = []
            for i in range(num_obstacles):
                obst_x, obst_y = self.randomly_place_item_on_grid(item=OBSTACLE)
                self.obst_coords.append((obst_x, obst_y))

            food_x, food_y = self.randomly_place_item_on_grid(item='food')
            self.food_coords = (food_x, food_y)
        # or we want a copied state, where we'd want to maintain
        # the state of the snake, food, and obstacles
        else:
            self.grid = grid
            self.snake = snake

            self.food_coords = self.get_item_coords(item=FOOD)
            self.obst_coords = self.get_obst_coords()


    def __cmp__(self, other_state):
        if (not other_state) or (not isinstance(other_state, State)):
            return False

        return (
            (self.snake.get_head_coords() == other_state.snake.get_head_coords()) and
            (self.food_coords == other_state.food_coords) and
            (self.obst_coords == other_state.obst_coords)
        )


    def throwaway_place_item(self, x, y, item):
        self.set_x_y_value_on_grid(x, y, ITEM_MAP[item])
        return x, y

    
    def randomly_place_item_on_grid(self, item):
        empty_loc_found = False
        seq = range(self.dim)
        rand_x = random.choice(seq)
        rand_y = random.choice(seq)
        while not empty_loc_found:
            cell = self.get_x_y_value_from_grid(rand_x, rand_y)
            if cell == None:
                self.set_x_y_value_on_grid(rand_x, rand_y, ITEM_MAP[item])
                empty_loc_found = True
            else:
                rand_x = random.choice(seq)
                rand_y = random.choice(seq)

        if not empty_loc_found:
            raise Exception("This should never happen!")
        
        return rand_x, rand_y


    def place_snake(self):
        mid_point_x = int(float(self.dim)/float(2))
        mid_point_y = int(float(self.dim)/float(2))-3

        #mid_point_x = 0
        #mid_point_y = 0
        snake_coords = []
        for i in range(self.snake.current_length):
            value = 'b'
            if i == 0:
                value = 'h'
            elif i == self.snake.current_length-1:
                value = 't'
            self.set_x_y_value_on_grid(mid_point_x, mid_point_y+i, value)
            snake_coords.append((mid_point_x, mid_point_y+i))

        self.snake.update_coords(new_coords=snake_coords)
        """
        self.set_x_y_value_on_grid(mid_point_x, mid_point_y+3, 't')
        self.set_x_y_value_on_grid(mid_point_x, mid_point_y+2, 'b')
        self.set_x_y_value_on_grid(mid_point_x, mid_point_y+1, 'b')
        self.set_x_y_value_on_grid(mid_point_x, mid_point_y, 'h')
        
        self.snake.update_coords(
            [
                (mid_point_x, mid_point_y),
                (mid_point_x, mid_point_y+1),
                (mid_point_x, mid_point_y+2),
                (mid_point_x, mid_point_y+3)
            ]
        )
        """
        return mid_point_x, mid_point_y
    

    def get_item_coords(self, item):
        item_coords = (None, None)
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell == ITEM_MAP[item]:
                    item_coords = (j, i)
        
        return item_coords


    def get_obst_coords(self):
        list_of_obst_coords = []
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell == 'o':
                    obst_coords = (j, i)
                    list_of_obst_coords.append(obst_coords)

        return list_of_obst_coords


    def get_legal_snake_movement_coords(self):
        """
        Returns a list of possible legal coordinates for a snake's head to move
        """
        snake_head_x, snake_head_y = self.snake.coords[0]
        direction_coordinates_map = self.snake.get_legal_coords_within_boundaries(
            dim=self.dim, x=snake_head_x, y=snake_head_y
        )

        for direction, legal_coord in direction_coordinates_map.items():
            legal_x, legal_y = legal_coord
            value = self.get_x_y_value_from_grid(x=legal_x, y=legal_y)
            if value in ('b', 't', 'o'):
                direction_coordinates_map.pop(direction)
        
        return direction_coordinates_map


    def get_x_y_value_from_grid(self, x, y):
        """
        How the grid is implemented is a list of lists
        We intuitively think of coordinates as (x, y)
        Yet to access items from our grid we have to do self.grid[y][x]
        Which is unintuitive
        """
        return self.grid[y][x]


    def set_x_y_value_on_grid(self, x, y, value):
        """
        """
        self.grid[y][x] = value


    def update_state_after_movement(self, new_head_coords):
        """
        This will take the current state's grid and a specified move_direction
        (either up, right, down, left) and move the snake in that direction
        Moves are filtered before hand, so no need to verify here whether a move_direction
        is valid for the snake
        Find the new head for the snake, and the first of the body's coords will take
        the old head's coords, the second of the body's coords will take the first body's coords, etc...
        Cleanup: delete the old tail from the state
        This will edit the state's grid, so only call this function after instantiating
        a new State
        """
        new_snake_coords = []

        curr_snake_coords = self.snake.coords
        curr_snake_tail_x, curr_snake_tail_y = curr_snake_coords[-1]

        new_snake_coords.append(new_head_coords)
        new_snake_coords.extend(curr_snake_coords[:-1])

        #food_x, food_y = self.food_coords
        #obst_x, obst_y = self.obst_coords

        for i, coord in enumerate(new_snake_coords):
            x, y = coord
            value = 'b'
            if i == 0:
                value = 'h'
            elif i == len(new_snake_coords)-1:
                value = 't'
            self.set_x_y_value_on_grid(x, y, value)

        self.set_x_y_value_on_grid(curr_snake_tail_x, curr_snake_tail_y, None)
        self.snake.coords = new_snake_coords

        if self.food_coords == new_head_coords:
            self.snake.goal_reached = True

        return


    def goal_state_reached(self):
        return self.snake.goal_reached


    def print_grid(self):
        for i, row in enumerate(self.grid):
            row_str = ''
            for j, cell in enumerate(row):
                if cell == None:
                    row_str += '_'
                else:
                    row_str += cell
                if j != self.dim - 1:
                    row_str += '|'
            print row_str
