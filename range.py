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

    def get_depth(self):
        """ Returns the left child of this Node. """
        return self._depth

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

def get_region(root, node_side, current_region):
    """Determines the region given a node and a node_side"""
    #if the parent depth is 0 then a vertical line was made at this node
    #if the parent depth is 1 then a horizonal line was made at this node
    depth = root.get_depth()
    x, y = current_region
    x1, x2 = x
    y1, y2 = y

    if node_side == "left":
        if depth % 2 == 0:
            return ((x1, root.get_value()), (y1, y2))
        else:
            return ((x1, x2), (y1, root.get_value()))

    else:
        if depth % 2 == 0:
            return ((root.get_value(), x2), (y1, y2))

        else:
            return ((x1, x2), (root.get_value(), y2))

def compare_regions(region, query_range):
    """Checking if the given region is completely contained in the range query
       or if the region overlaps the query range. Returns 'no overlap', 'overlap',
       or 'contained' accordingly """

    x, y = region
    region_x1, region_x2 = x
    region_y1, region_y2 = y

    x, y = query_range
    query_x1, query_x2 = x
    query_y1, query_y2 = y

    if query_x1 <= region_x1 and query_x2 >= region_x2 and \
       query_y1 <= region_y1 and query_y2 >= region_x2:
       return 'contained'

    #occurs when one region is completely to the left of another
    if region_x1 > query_x2 or query_x1 > region_x2:
        return 'no overlap'

    #occurs when one region is completely above the other
    if region_y1 > query_y2 or query_y1 > region_y2:
      return 'no overlap'

    return 'overlap'

def pt_in_query_range(point, query_range):
    """Given a point and a query range, checks if the point in in the query
    range and returns true or false accordingly"""
    point_x, point_y = point

    x, y = query_range
    query_x1, query_x2 = x
    query_y1, query_y2 = y

    if point_x >= query_x1 and point_x <= query_x2 and \
       point_y >= query_y1 and point_y <= query_y2:
       return True

    return False

def range_query(kd_tree, query_range: Tuple[Tuple[int,int],Tuple[int,int]], current_region = ((-math.inf, math.inf),(-math.inf, math.inf)), points = []) -> List[Tuple[int,int]]:
    """Perform a 2D range reporting query using kd_tree and the given query range
       and return the list of points.

        Keyword arguments:
        kd_tree: the root node of the kd-tree to query
        query_range: a rectangular range to query

    Return the points in the query range as a list of tuples."""

    if kd_tree.get_right() == None and kd_tree.get_left() == None:
        if pt_in_query_range(kd_tree.get_value(), query_range):
            points.append(kd_tree.get_value())

    else:
        left_region = get_region(kd_tree, "left", current_region)
        right_region = get_region(kd_tree, "right", current_region)
        region_comparison = compare_regions(left_region, query_range)

        if region_comparison == 'contained':
            report_points(kd_tree.get_left(), points)

        elif region_comparison == 'overlap':
            range_query(kd_tree.get_left(), query_range, left_region, points)

        region_comparison = compare_regions(right_region, query_range)

        if region_comparison == 'contained':
            report_points(kd_tree.get_right(), points)

        elif region_comparison == 'overlap':
            range_query(kd_tree.get_right(), query_range, right_region, points)

    return points

def report_points(root, lst):
    """Traverses a tree given a root using an inorder traversal and adds points
       to the list."""
    if not root:
        return

    report_points(root.get_left(), lst)

    if not root.get_left() and not root.get_right():
        lst.append(root.get_value())

    report_points(root.get_right(), lst)

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
    """Given a number of points and number of points to be reported, returns
        a list of points and a query range"""
    points = []

    for index in range(num_points):
        points.append((index, index))

    query_range = ((0, num_points_reported - 1), (0, num_points_reported - 1))

    return (points, query_range)

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

    time_ms = time_diff.microseconds / 1000
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
    print("    n      : the number of points")
    print("    k      : the number points reported")
    print("    range  : the running time of range_query (in ms)")

    return header

def run_experiment(option):
    """run the timing experiement according to the user-supplied option"""
    header = build_header_and_legend()

    for item in header:
        print("{:>15} ".format(item), end="")
    print("")

    for i in range(2,35):
        size = 2**i

        num_reported_points = 4
        max_reported_points = 4
        separate = False
        if option == "vary":
            num_reported_points = 4
            max_reported_points = size
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
    This experiment has the same and vary option. The vary option is used to show
    the +k in the run time because in the vary experiment, as k doubles, the
    run time doubles. The vary option varys the size of k throught the experiment.

    The same experiment shows that the kd-tree has a query time of approximately
    O(lgn + k) in the best case. When we use my generate_points function, this query
    region and point list is close to ideal so the run time_experiment for same
    shows very little growth. This experiment has n and double and keeps the number
    of points reported the same throught.
    Note: change line 288 to 'time_ms = time_diff.microseconds / 1000'
    to not do floor division to see the runtime better.
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

def sqrt_experiment():
    """Experiment to determine how much sqrt n grows by as n doubles.
       Next value is approximately 1.4x bigger than the previous value.
    """
    last = 1
    for index in range(2, 35):
        curr = math.sqrt(2**index)
        print("N: " + str(2 **index) + " " + "" + str(round(curr)))
        print("Difference: ",  end ="")
        print(round((curr + index) / (last + index - 1), 3))
        last = curr

def num_nodes(root):
    """Determines the number of nodes in the tree"""
    if root == None:
        return 0

    return 1 + num_nodes(root.get_left()) + num_nodes(root.get_right())

def test():
    """
    Test range_query.
    """
    root = create_kdtree([(0,0), (5,2), (3,-2)])
    root = create_kdtree([(0,5),(3,-2),(-4,5.5),(-2,3),(2,5.5),(2.7,4),(-4,1),(-1.5, 0),(1.5,1),(4,-1)])
    root = create_kdtree([(0,5),(2.2,-2),(-4,5.5),(-2,2.5),(-3.5,3.5),(5,5.5),(2.7,4),(-4,1),(-2.5,0),(1.5,-.5),(4,0)])
    print_tree(root)
    #print(range_query(root, [[0,6],[-1,6]]))
    #print(range_query(root, [[-5,2],[-1,7]]))
    print(range_query(root, [[-1,6],[-1,6]]))

    time_experiment()
    #sqrt_experiment()

if __name__ == "__main__":
    #test() # use for testing, comment when done
    #time_experiment()
