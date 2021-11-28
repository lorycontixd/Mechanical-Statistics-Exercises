import numpy as np
import ast
from dataclasses import dataclass
import re

@dataclass
class Label:
    id: int
    index: int
    values: list

# A simple class (struct-like) describing the location of an item in a matrix
class Position:
    def __init__(self, r, c):
        self.row = r
        self.column = c

    # For comparison
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.row == other.row and self.column == other.column

    # So that it can go in sets
    def __hash__(self):
        return hash((self.row, self.column))


# An object describing an item in a matrix that contains some helpful methods
class Node:
    def __init__(self, row, column, val):
        self.pos = Position(row, column)
        self.value = val

    # Returns the nodes adjacent (left, right, top, bottom) to self in a given matrix
    def neighbors(self, matrix):
        nodes = []

        y = self.pos.row
        x = self.pos.column

        try: 
            if x - 1 >= 0:
                to_left = matrix[y][x-1].value
                nodes.append(Node(y, x-1, to_left))
        except: pass

        try: 
            if x + 1 <= len(matrix[y]) - 1:
                to_right = matrix[y][x+1].value
                nodes.append(Node(y, x+1, to_right))
        except: pass

        try: 
            if y - 1 >= 0:
                to_top = matrix[y-1][x].value
                nodes.append(Node(y-1, x, to_top))
        except: pass

        try: 
            if y + 1 <= len(matrix) - 1:
                to_bottom = matrix[y+1][x].value
                nodes.append(Node(y+1, x, to_bottom))
        except: pass

        return nodes

    # Returns the nodes with the same value as self of self's neighbors in a given matrix
    def value_neighbors(self, matrix):
        return [node for node in self.neighbors(matrix) if node.value == self.value]

    # Looks prettier when printing
    def __str__(self):
        return f"{self.value}, {(self.pos.column, self.pos.row)}"

    # So that Nodes can go in sets
    def __hash__(self):
        return hash((self.pos, self.value))

    # Turns a matrix into one containing Nodes
    @staticmethod
    def nodify(matrix):
        newmatrix = np.empty(matrix.shape, dtype=Node)
        for y, row in enumerate(matrix):
            for x, item in enumerate(row):
                node = Node(y, x, item)
                newmatrix[y][x] = node
        return newmatrix

    # Takes apart a matrix with Nodes to just contain the values    
    @staticmethod
    def denodify(matrix):
        for y, row in enumerate(matrix):
            for x, node in enumerate(row):
                matrix[y][x] = node.value
        return matrix

    # For comparison
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value and self.pos == other.pos
        return False


# A global set containing nodes already visited so that infinite loops do not occur
already_checked = set()


# A recursive method returning the continuous network of value_neighbors in a matrix starting from a node
def connected_values(node, matrix):
    global already_checked

    already_checked.add(node)

    nodes = []
    for value_neighbor in node.value_neighbors(matrix):
        nodes.append(value_neighbor)
        if value_neighbor not in already_checked:
            nodes += connected_values(value_neighbor, matrix)
    return nodes


# A method that gets all of the connected values networks in a matrix
def all_connected_values(matrix):
    global already_checked

    groups = []

    for row in matrix:
        for node in row:
            already_checked = set()

            values = set(connected_values(node, matrix))
            values.add(node)
            groups.append(values)

    # Formats the networks and prints them out. A set is used so that duplicate networks are not shown
    mystr = '\n'.join({str(group[0].value) + ": " + ', '.join(map(str, sorted([(node.pos.column, node.pos.row) for node in group], key=lambda t:[t[0],t[1]]))) for group in map(list, groups)})
    return mystr

def __parse_string(string:str):
    sets = string.split("\n")
    newsets = list()
    labels = []
    for i,s in enumerate(sets):
        index, values = s.split(":")
        values = "["+values+"]"
        values = [tuple(x.split(',')) for x in re.findall("\((.*?)\)", values)]
        values = [(int(i),int(j)) for (i,j) in values]
        #print(i, " - ", index, " - ",values)
        l = Label(i,index,values)
        labels.append(l)
    return labels
    

def export_labeled_matrix(matrix):
    x = Node.nodify(matrix)
    str = all_connected_values(x)
    labels = __parse_string(str)
    newmatrix = np.empty(matrix.shape)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            for l in labels:
                if (i,j) in l.values:
                    newmatrix[i][j] = int(l.id)
                    break
    return np.transpose(newmatrix)

def get_sizes(matrix):
    x = Node.nodify(matrix)
    str = all_connected_values(x)
    labels = __parse_string(str)
    sizes = list()
    for l in labels:
        sizes.append(len(l.values))
    return sizes 
        

"""
# Example matrix, doesn't necessarily have to be rectangular
example_matrix = np.array([[ 1, -1, -1,  1, -1,  1],
                          [-1, -1, -1,  1, -1,  1],
                          [-1,  1, -1, -1, -1,  1],
                          [-1,  1, -1,  1,  1,  1],
                          [-1,  1, -1, -1,  1, -1],
                          [-1, -1, -1,  1,  1,  1]])
print(example_matrix,"\n")
newmatrix = np.array(export_labeled_matrix(example_matrix))
print(np.transpose(newmatrix))
"""