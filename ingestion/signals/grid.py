import cv2
import numpy as np

def grid_score(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 50, 150)

    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold = 100,
                            minLineLength=50, maxLineGap=10)
    
    if lines is None:
        return 0.0
    
    horizontal = 0
    vertical = 0

    for line in lines:
        x1, y1, x2, y2 = line[0]

        if abs(y1 - y2) < 5:
            horizontal += 1

        elif abs(x1 - x2) < 5:
            vertical += 1 

    score = min(1.0, (horizontal + vertical)/50.0)

    return score
