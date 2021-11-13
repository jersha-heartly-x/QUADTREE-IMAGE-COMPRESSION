import matplotlib
import random
import matplotlib.pyplot as plt

MIN_LIM = 0
MAX_LIM = 20

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Node:
    def __init__(self, x, y, w, h, points):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.points = points
        self.children = []

    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def get_points(self):
        return self.points

class quadTree:
    def __init__(self, k, n):
        self.max = k
        self.points = [Point(random.uniform(0, 20), random.uniform(0, 20)) for x in range(n)]
        self.root = Node(MIN_LIM, MIN_LIM, MAX_LIM, MAX_LIM, self.points)
        self.split()

    def add_point(self, x, y):
        if x >= MIN_LIM and x <= MAX_LIM and y >= MIN_LIM and y <= MAX_LIM:
            p = Point(x, y)
            self.points.append(p)
            self.root.points.append(p)
            self.insert(self.root, p)
    
    def insert(self, node, pt):
        if len(node.points) <= self.max:
            return

        if node.children == []:
            recursive_split(node, self.max)
            return
        
        if pt.x >= node.children[0].x and pt.x <= node.children[0].width and pt.y >= node.children[0].y and pt.y <= node.children[0].height:
            node.children[0].points.append(pt)
            self.insert(node.children[0], pt)
        
        elif pt.x >= node.children[1].x and pt.x <= node.children[1].width and pt.y >= node.children[1].y and pt.y <= node.children[1].height:
            node.children[1].points.append(pt)
            self.insert(node.children[1], pt)

        elif pt.x >= node.children[2].x and pt.x <= node.children[2].width and pt.y >= node.children[2].y and pt.y <= node.children[2].height:
            node.children[2].points.append(pt)
            self.insert(node.children[2], pt)
        
        else:
            node.children[3].points.append(pt)
            self.insert(node.children[3], pt)

    def get_points(self):
        return self.points
    
    def split(self):
        recursive_split(self.root, self.max)
    
    def graph(self):
        fig = plt.figure(figsize=(12, 12))
        plt.title("Quadtree")
        ax = fig.add_subplot(111)
        c = find_children(self.root)
        # areas = set()
        # for i in c:
        #     areas.add(i.width*i.height)

        for n in c:
            ax.add_patch(matplotlib.patches.Rectangle((n.x, n.y), n.width, n.height, fill=False))

        x = [point.x for point in self.points]
        y = [point.y for point in self.points]
        plt.plot(x, y, 'ro')
        plt.show()
        return

def recursive_split(node, k):
   if len(node.points)<=k:
       return
   
   midW = float(node.width/2)
   midH = float(node.height/2)

   p = contains(node.x, node.y, midW, midH, node.points)
   x1 = Node(node.x, node.y, midW, midH, p)
   recursive_split(x1, k)

   p = contains(node.x, node.y+midH, midW, midH, node.points)
   x2 = Node(node.x, node.y+midH, midW, midH, p)
   recursive_split(x2, k)

   p = contains(node.x+midW, node.y, midW, midH, node.points)
   x3 = Node(node.x + midW, node.y, midW, midH, p)
   recursive_split(x3, k)

   p = contains(node.x+midW, node.y+midH, midW, midH, node.points)
   x4 = Node(node.x+midW, node.y+midH, midW, midH, p)
   recursive_split(x4, k)

   node.children = [x1, x2, x3, x4]
   
   
def contains(x, y, w, h, points):
   pts = []
   for point in points:
       if point.x >= x and point.x <= x+w and point.y>=y and point.y<=y+h:
           pts.append(point)
   return pts


def find_children(node):
   if not node.children:
       return [node]
   else:
       children = []
       for child in node.children:
           children += (find_children(child))
   return children

def main():

    Q = quadTree(4, 80)
    Q.graph()

    Q.add_point(2, 3)
    Q.add_point(8, 4)
    Q.graph()

main()