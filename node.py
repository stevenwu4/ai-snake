import itertools


class Node(object):
    #http://stackoverflow.com/questions/1045344/how-do-you-create-an-incremental-id-in-a-python-class
    new_id = itertools.count().next

    def __init__(
        self, state, action=None, parent_index=None, depth=0
    ):
        """
        The states will be a Board object, see board.py
        The action is the direction that led us from the parent to this node
        """
        node_index = Node.new_id()

        self.state = state
        self.index = node_index
        self.action = action
        self.parent_index = parent_index
        self.depth = depth

    def __cmp__(self, other_node):
        if (not other_node) or (not isinstance(other_node, Node)):
            return False

        return self.state == other_node.state


class AStarNode(Node):
    def __init__(
        self, state, action=None, parent_index=None, depth=0,
        g=0, h=0
    ):
        super(self.__class__, self).__init__(
            state, action, parent_index, depth
        )
        self.g = g
        self.h = h
        self.f = self.g + self.h