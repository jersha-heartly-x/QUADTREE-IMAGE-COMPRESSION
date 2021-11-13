from os import error
import numpy as np
import cv2
from PIL import Image, ImageDraw
from numpy.lib.histograms import histogram

MAX = 8
THRESHOLD = 13

def avgclr(img):
    imgArr      = np.asarray(img)

    #getting the average color from the image array
    avg_by_row  = np.average(imgArr, axis=0)
    avg         = np.average(avg_by_row, axis=0)

    # avg (r,g,b)
    return (int(avg[0]), int(avg[1]), int(avg[2]))  

def deviation(histo):

    total = sum(histo) #no of pixels
    value = 0
    error = 0
    if total>0:
        value = sum(x*i for i, x in enumerate(histo))/total;                    #average intensity
        error = (sum(x*(value-i)**2 for i, x in enumerate(histo))/total)**0.5;  #deviation
    
    return error


def get_detail_level(histo):

    #getting the detail_level for each color (r,g,b) from the histogram
    r_detail_level  = deviation(histo[0:256])
    g_detail_level  = deviation(histo[256:512])
    b_detail_level  = deviation(histo[512:768])

    #getting the overall detail_level in terms of grayscale using the below formula
    detail_level = r_detail_level*0.2989 + g_detail_level*0.5870 + b_detail_level*0.1140   

    return detail_level


# node in the quadtree
class Quadrant():

    def __init__(self, img, borderbox, depth): 
        self.borderbox  = borderbox
        self.depth      = depth
        self.children   = None
        self.isLeaf       = False
        image = img.crop(borderbox)
        histo = image.histogram()
        self.detail_level = get_detail_level(histo)
        self.colour       = avgclr(image)
    
    def split(self, img):
        left, top, right, bottom = self.borderbox

        mid_x = left + (right -left)/2
        mid_y = top  + (bottom-top )/2

        # split root quadrant into 4 new quadrants
        upper_left      = Quadrant(img, (left, top, mid_x, mid_y), self.depth+1)
        upper_right     = Quadrant(img, (mid_x, top, right, mid_y), self.depth+1)
        bottom_left     = Quadrant(img, (left, mid_y, mid_x, bottom), self.depth+1)
        bottom_right    = Quadrant(img, (mid_x, mid_y, right, bottom), self.depth+1)

        #add the new quadrants as children to the root
        self.children = [upper_left, upper_right, bottom_left, bottom_right]

class QuadTree():
    def __init__(self, img):
        self.width, self.height = img.size

        self.depth = 0    #max depth from the root

        self.root = Quadrant(img, img.getbbox(), 0)

        self.buildTree(self.root, img)   #build the quadtree

    def buildTree(self, root, img):
        if root.depth >= MAX or root.detail_level <= THRESHOLD:
            if root.depth > self.depth:
                self.depth = root.depth
            root.isLeaf = True   #attained a leaf stop recursing
            return
        
        root.split(img)

        for x in root.children:
            self.buildTree(x, img)
    
    def getLeaves(self, depth):
        if depth > self.depth:
            raise ValueError('Depth too large')
        quadrants = []

        self.search(self, self.root, depth, quadrants.append)               #searching the tree for leaves

        return quadrants                                                    #list of leaf quadrants
    
    def search(self, tree, quad, max_depth, appendQuad):

        if quad.isLeaf or quad.depth == max_depth:
            appendQuad(quad)
        
        elif quad.children != None:
            for x in quad.children:
                self.search(tree, x, max_depth, appendQuad)
    
    def createImg(self, customDepth):

        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        draw.rectangle((0, 0, self.width, self.height), (0,0,0))    # creating a black image to begin with

        leafQuadrants = self.getLeaves(customDepth)

        for x in leafQuadrants:
            draw.rectangle(x.borderbox, x.colour)                   # colouring the particular Quadrant

        return img


    def processGIF(self, file_name):

        imgarr = []

        finalImg = self.createImg(self.depth)

        for i in range(self.depth):
            img = self.createImg(i)
            imgarr.append(img)

        for i in range(5):
            imgarr.append(finalImg)
        
        imgarr[0].save(file_name, save_all = True, append_images = imgarr[1:], duration = 1000, loop = 0)
        

if __name__ == '__main__':
    

    img = Image.open("turtle.jpg")  #load an image

    qTree = QuadTree(img)           #create a quadtree for that image

    img = qTree.createImg(8)        #create a compressed image from the quadtree

    img.save("compressed.jpg")      #save the compressed image

    img.show()

    qTree.processGIF("compressedGif.gif")    #create the stages as gif and save