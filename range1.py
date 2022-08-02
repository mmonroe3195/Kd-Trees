"""
    File:        range.py
    Author:      Madison Monroe
    Course:      CS 307 - Computational Geometry
    Assignment:  Problem Set 5 - Range Searching
    Description: Methods to construct a kd-tree, perform
    range queries, test and time the range query.
"""
from typing import List, Tuple
import datetime
import math

NUM_ITERATIONS = 3

#note to self: do we want nodes = to know their parents?
#not necessary for building tree but necessary later on?
class Node:
    def __init__(self, val, depth, left = None, right = None):
        """ The Constructor for a Node."""
        self._value = val
        self._left = left
        self._right = right
        self._depth = depth

    def __str__(self):
        return 'My value is {}.'.format(self._value)

    def get_value(self):
        """ Returns the value of the Node."""
        return self._value

    def get_right(self):
        """ Returns the right child of this Node. """
        return self._right

    def get_left(self):
        """ Returns the left child of this Node. """
        return self._left

def orient(p, q, r):
    """Determines whether point r is on the left, right, or collinear with p and
       q. Returns 1 if the point is to the left, -1 if it is to the right,
       and 0 if the point is collinear"""
    #splits tuple of points to get x and y coordinates
    px, py = p
    qx, qy = q
    rx, ry = r

    #finds the determinate as was done in class
    determinate = qx * ry + px * qy + rx * py - qx * py - rx * qy - ry * px

    if determinate > 0:
        return 1

    elif determinate < 0:
        return -1

    return 0

def create_kdtree(points: List[Tuple[int,int]], sorted_y = None, depth = 0):
    """
    Construct a kd-tree from a list of 2D points
    and return its root.

        Keyword arguments:
        points -- the list of 2d points

    Return the root of the kd-tree
    """
    #only sorts the first time the algorithm is run
    if sorted_y == None:
        sorted_y = points[:]
        sorted_y.sort(key = lambda y: y[1])
        points.sort()

    if len(points) != len(sorted_y):
        print("issue")

    if len(points) == 0 or len(sorted_y) == 0:
        return None

    if len(points) == 1 or len(sorted_y) == 0:
        return Node(points[0], depth)

    #make vertical line
    elif depth % 2 == 0:
        #ensures the [n/2]th /2 smallest number is taken
        median_index = math.ceil(len(points) / 2) - 1
        left_sorted_x = points[:median_index + 1]
        right_sorted_x = points[median_index + 1:]
        #calculate new sorted-y list
        left_sorted_y = []
        right_sorted_y = []
        parent = None

        #sorting by y coorinate
        for point in sorted_y:
            x_coordinate, y_coordinate = points[median_index]
            if orient(points[median_index], (x_coordinate, y_coordinate + 1), \
               point) != -1:
                left_sorted_y.append(point)
            else:
                right_sorted_y.append(point)

        x_coordinate, _ = points[median_index]
        node_left = create_kdtree(left_sorted_x, left_sorted_y,depth + 1)
        node_right = create_kdtree(right_sorted_x, right_sorted_y, depth + 1)
        parent = Node(x_coordinate, depth, node_left, node_right)

    #make horizonal line
    else:
        bottom_sorted_x = []
        top_sorted_x = []
        median_index = math.ceil(len(sorted_y) / 2) - 1
        bottom_sorted_y = sorted_y[:median_index + 1]
        top_sorted_y = sorted_y[median_index + 1:]

        for point in points:
            x_coordinate, y_coordinate = sorted_y[median_index]
            if orient(sorted_y[median_index], (x_coordinate + 1, y_coordinate), \
               point) != 1:
                bottom_sorted_x.append(point)
            else:
                top_sorted_x.append(point)

        _, y_coordinate = sorted_y[median_index]
        node_left = create_kdtree(bottom_sorted_x, bottom_sorted_y, depth + 1)
        node_right = create_kdtree(top_sorted_x, top_sorted_y, depth + 1)
        parent = Node(y_coordinate, depth, node_left, node_right)

    return parent

def range_query(kd_tree, query_range: Tuple[Tuple[int,int],Tuple[int,int]]) -> List[Tuple[int,int]]:
    """
    Perform a 2D range reporting query using kd_tree and the given query range
    and return the list of points.

        Keyword arguments:
        kd_tree: the root node of the kd-tree to query
        query_range: a rectangular range to query

    Return the points in the query range as a list of tuples.
    """
    #place holder
    return [(0,0)]

def print_tree(root):
    """Prints the tree when given a root using an inorder traversal"""
    if not root:
        return

    if root.get_left():
        print("left")
    print_tree(root.get_left())
    if not root.get_left() and not root.get_right():
        print(root.get_value())
        print("a leaf was just printed")


    if root.get_right():
        print("right")
    print_tree(root.get_right())

def generate_points(num_points, num_points_reported):
    points = []

    for index in range(num_points):
        points.append((index, index))

    range_query = ((0, 0), (num_points_reported - 1, num_points_reported - 1))

    return (points, range_query)

def average_time(the_algorithm, kd_tree, query_range):
    """call the_algorithm on endpoints repeatedly and return average time"""
    time_diff = None

    for iteration in range(0, NUM_ITERATIONS):
        start = datetime.datetime.now()
        the_algorithm(kd_tree, query_range)
        end = datetime.datetime.now()
        if time_diff == None:
            time_diff = end - start
        else:
            time_diff = time_diff + end - start

    time_ms = time_diff.microseconds // 1000
    time_ms = time_ms + time_diff.seconds * 1000
    time_ms = time_ms + time_diff.days * 24 * 60 * 60 * 1000

    return time_ms

def get_table_entry(num_points, num_points_reported, item):
    """get the appropriate table entry, which is either a number of segments,
       a number of intersections, or a running time"""
    points, query_range = generate_points(num_points, num_points_reported)
    kd_tree = create_kdtree(points)
    if item == "n":
        return num_points
    elif item == "k":
        return num_points_reported
    elif item == "range":
        return average_time(range_query, kd_tree, query_range)

    return -1

def build_header_and_legend():
    """construct the header entries, which are also used to fill table entries"""
    # always print n (number of vertices)
    header = ["n", "k", "range"]

    print("Legend:")
    print("    n      : the number points")
    print("    k      : the number points reported")
    print("    range  : the running time of range_query (in ms)")

    return header

#update it for range!!!!!!!!!
def run_experiment(option):
    """run the timing experiement according to the user-supplied option"""
    header = build_header_and_legend()

    for item in header:
        print("{:>15} ".format(item), end="")
    print("")

    for i in range(2,35):
        size = 2**i
        num_reported_points = size
        max_reported_points = size
        separate = False
        if option == "vary":
            num_reported_points = 4
            max_reported_points = (size ** 2) // 4
            separate = True

        while num_reported_points <= max_reported_points:
            for item in header:
                print("{:>15} ".format(get_table_entry(size, num_reported_points, item)), end="")
            num_reported_points = 2 * num_reported_points
            print("")
        if separate:
            print("")

def time_experiment():
    """
    Custom experiment to show that kd-tree has query time O(sqrt(n) + k).
    """
    print("Welcome to Range Timer! Press Ctrl+C at any time to end...")

    option = input("Which test would you like to run (same,vary)? ")
    while option not in ["same", "vary"]:
        print("Unrecognized option '", option, "'")
        option = input("Which test would you like to run? (same,vary)?")

    if option == "same":
        print("Running algorithm with n segments and I=n intersections.")
        print("To vary the number of intersections, run test 'vary'.")
    elif option == "vary":
        print("Running algorithm with n points and k (variable) points to be reported.")
    else:
        print("This shouldn't happen...")

    run_experiment(option)

def test():
    """
    Test range_query.
    """
    #root = create_kdtree([(0,5),(3,-2),(-4,5.5),(-2,3),(2,5.5),(2.7,4),(-4,1),(-1.5, 0),(1.5,1),(4,-1)])
    root = create_kdtree([(0,5),(2.2,-2),(-4,5.5),(-2,2.5),(-3.5,3.5),(5,5.5),(2.7,4),(-4,1),(-2.5,0),(1.5,-.5),(4,0)])
    print(print_tree(root))
    #time_experiment()

if __name__ == "__main__":
    #(0,5),\ (3,-2),(-4,5.5),\ (-2,3),\ (2,5.5),(2.7,4),\ (-4,1),\ (-1.5,\ 0),\ (1.5,1),\ (4,-1)
    test() # use for testing, comment when done
    #time_experiment()
