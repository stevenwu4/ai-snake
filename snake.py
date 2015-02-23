INITIAL_LENGTH = 4
FINAL_LENGTH = 7
DIRECTION_UP = 'up'
DIRECTION_RIGHT = 'right'
DIRECTION_DOWN = 'down'
DIRECTION_LEFT = 'left'


class Snake():
    def __init__(self):
        self.current_length = INITIAL_LENGTH
        self.final_length = FINAL_LENGTH
        self.num_food_eaten = 0
        self.goal_reached = False
        self.coords = None


    def update_coords(self, new_coords):
        self.coords = new_coords


    def update_self_after_eating(self):
        self.goal_reached = False
        self.num_food_eaten += 1


    def get_head_coords(self):
        return self.coords[0]


    def get_legal_coords_within_boundaries(self, dim, x, y):
        """
        Returns a list of possible coordinate destinations from the passed in
        coordinates based on the dimensions specified
        This is just considering the boundaries of the dimension, not w.r.t the snake's body
        """
        direction_coordinates_map = {}
        #Up
        if y-1 >= 0:
            up_coord = (x, y-1)
            direction_coordinates_map[DIRECTION_UP] = up_coord
        #Right
        if x+1 < dim:
            right_coord = (x+1, y)
            direction_coordinates_map[DIRECTION_RIGHT] = right_coord
        #Down
        if y+1 < dim:
            down_coord = (x, y+1)
            direction_coordinates_map[DIRECTION_DOWN] = down_coord
        #Left
        if x-1 >= 0:
            left_coord = (x-1, y)
            direction_coordinates_map[DIRECTION_LEFT] = left_coord

        return direction_coordinates_map

