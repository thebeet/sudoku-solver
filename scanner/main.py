import cv2
import numpy as np

import imutils
import torch
from torch import nn

class Model(nn.Module):
    def __init__(self, inchannel, output_size):
        super().__init__()
        self.conv1 = nn.Conv2d(inchannel,32,3)
        self.conv1_bn = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32,64,3)
        self.conv2_bn = nn.BatchNorm2d(64)
        self.max_pool = nn.MaxPool2d(2)
        self.relu = nn.ReLU()
        self.linear = nn.Linear(64*6*6, output_size)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x):
        x = self.relu(self.conv1(x))
        # print(x.size())
        x = self.conv1_bn(x)
        x = self.max_pool(x)
        x = self.relu(self.conv2(x))
        x = self.conv2_bn(x)
        x = self.max_pool(x)
        x = torch.flatten(x, start_dim=1)
        x = self.linear(x)
        x = self.softmax(x)

        return x

input_size = 32

img = cv2.imread('./images/a.png')
model = Model(1,10)
model.load_state_dict(torch.load("model.pt", map_location = torch.device("cuda")))

#cv2.imshow("Input image", img)

def get_perspective(img, location, height = 900, width = 900):
    """Takes an image and location of an interesting region.
    And return the only selected region with a perspective transformation"""
    pts1 = np.float32([location[0], location[3], location[1], location[2]])
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    # Apply Perspective Transform Algorithm
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(img, matrix, (width, height))
    return result

def find_board(img):
    """Takes an image as input and finds a sudoku board inside of the image"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bfilter = cv2.bilateralFilter(gray, 13, 20, 20)
    edged = cv2.Canny(bfilter, 30, 180)
    keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(keypoints)
    newimg = cv2.drawContours(img.copy(), contours, -1, (0, 255, 0), 3)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
    location = None
    # Finds rectangular contour
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 15, True)
        if len(approx) == 4:
            location = approx
            break
    result = get_perspective(img, location)
    return result, location

def split_boxes(board):
    """Takes a sudoku board and split it into 81 cells.
    each cell contains an element of that board either given or an empty cell."""
    rows = np.vsplit(board,9)
    labels = np.zeros((9,9), dtype = int)
    image_count = -1
    threshold = 20
    border = 15
    for r in rows:
        cols = np.hsplit(r,9)
        for box in cols:
            image_count = image_count + 1

            box = box[border:-border, border:-border]
            flat_box = np.ndarray.flatten(box)
            #count number of black pixels i.e. numbers
            count = 0
            for pixel in flat_box:
                if pixel < 127:
                    count = count + 1

            if count < threshold:
                continue

            box = cv2.resize(box, (input_size, input_size))/255.0
            box = torch.tensor(box, dtype = torch.float)
            box = box.unsqueeze(0)
            box = box.unsqueeze(1)
            number = np.argmax(model(box).detach().numpy(), axis=-1)
            labels[image_count//9, image_count%9] = number
    return labels

board, location = find_board(img)
gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
boardNums = split_boxes(gray)
print(boardNums)
