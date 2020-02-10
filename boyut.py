# gerekli paketleri import ediyoruz
import tkinter as tk
import turtle
from tkinter import filedialog

import cv2
import imutils
import numpy as np
from imutils import contours
from imutils import perspective
from scipy.spatial import distance as dist


def mainprocess(impath, width):
    root.withdraw()  # hides the window

    def colorchange():
        if r == 1:
            t.color("Cornflower Blue")
        elif r == 2:
            t.color("yellow")
        elif r == 3:
            t.color("maroon")
        elif r == 4:
            t.color("red")
        elif r == 5:
            t.color("Forest Green")
        elif r == 6:
            t.color("Antique White 3")
        elif r == 7:
            t.color("Chartreuse")

    def midpoint(pt_a, pt_b):
        return (pt_a[0] + pt_b[0]) * 0.5, (pt_a[1] + pt_b[1]) * 0.5

    # construct the argument parse and parse the arguments
    """ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
                    help="resmin konumu")
    ap.add_argument("-w", "--width", type=float, required=True,
                    help="soldaki klavuz cisminin capi")
    args = vars(ap.parse_args())"""

    t = turtle.Turtle()
    t.pu()
    t.setpos(-t.screen.screensize()[0] - 50, -t.screen.screensize()[1] / 10)
    t.pd()

    r = 0
    space = 1
    newpos = 0

    # resmi yükleyip siyah beyaza çevirip biraz blur ekliyoruz
    image = cv2.imread(impath)  # args["image"]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)

    # edge detection gerçekleştirip, ardından nesne kenarları arasındaki
    # boşlukları kapatmak için bir dilation + erosion gerçekleştiriyoruz
    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations = 1)
    edged = cv2.erode(edged, None, iterations = 1)

    # edge map üzerinde dış hatları buluyoruz
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # dış hatları soldan sağa dogru sıralıyoruz ve
    # 'pixels per metric' calibrasyonumuzu yapılandırıyoruz
    (cnts, _) = contours.sort_contours(cnts)
    pixelsPerMetric = None

    # dış hatlar üzerinde ayrı ayrı bir döngü kuruyoruz
    for c in cnts:
        # eğer hattımız yeterince büyük değilse görmezden geliyoruz
        if cv2.contourArea(c) < 100:
            continue

        # compute the rotated bounding box of the contour
        # cismin dış hatlarına göre hizalanmış sınır kutusunu hesaplıyoruz
        orig = image.copy()
        box = cv2.minAreaRect(c)
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype = "int")

        # order the points in the contour such that they appear
        # in top-left, top-right, bottom-right, and bottom-left
        # order, then draw the outline of the rotated bounding
        # box
        box = perspective.order_points(box)
        cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

        # loop over the original points and draw them
        for (x, y) in box:
            cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

        # unpack the ordered bounding box, then compute the midpoint
        # between the top-left and top-right coordinates, followed by
        # the midpoint between bottom-left and bottom-right coordinates
        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)

        # compute the midpoint between the top-left and top-right points,
        # followed by the midpoint between the top-righ and bottom-right
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)

        # draw the midpoints on the image
        cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

        # draw lines between the midpoints
        cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (255, 0, 255), 2)
        cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (255, 0, 255), 2)

        # compute the Euclidean distance between the midpoints
        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

        # if the pixels per metric has not been initialized, then
        # compute it as the ratio of pixels to supplied metric
        # (in this case, inches)
        if pixelsPerMetric is None:
            pixelsPerMetric = dB / width  # args["width"]

        # cismin boyutunu hesaplıyoruz
        dimA = dA / pixelsPerMetric
        dimB = dB / pixelsPerMetric

        # cismin boyutunu resmin üzerine çiziyoruz
        cv2.putText(orig, "{:.1f}cm".format(dimA), (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    (255, 255, 255), 2)
        cv2.putText(orig, "{:.1f}cm".format(dimB), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    (255, 255, 255), 2)

        # img = cv2.imread("example_01.png")
        # cropped = img[dA:dimA,dB:dimB]

        # show the output image
        cv2.imshow("Ornek", orig)
        if cv2.waitKey(0) == ord(
                'd'):  # d ye basılırsa çizilecek (draw), başka bir tuşa basılırsa çizilmeden diğerine geçer.

            # cv2.imshow("cropped", cropped)
            # cv2.waitKey(0)

            # turtle ile çizim yapma

            def cizdir(akenar, bkenar):
                t.forward(akenar)  # Cismin a kenarı uzunlugu
                t.left(90)  # 90 derece çeviriyoruz
                t.forward(bkenar)  # cismin b kenarı uzunlugu
                t.left(90)
                t.forward(akenar)
                t.left(90)
                t.forward(bkenar)
                t.left(90)

            colorchange()

            if round(dimA, 1) == round(dimB, 1):
                r += 1
                t.penup()
                t.setpos(t.position()[0], t.position()[1] - 200)
                t.pendown()
                t.circle((dA) / 2)
                t.penup()
                t.setpos(t.position()[0], t.position()[1] + 200)
                t.pendown()
                print(r, ".Cisim bir daire ve çapı=", round(dimA, 1))
            else:
                r += 1
                if space == 1:
                    cizdir(dA, dB)
                    oldpos = dA
                    newpos = oldpos + 30
                    space += 1
                    print(r, ".Cisim köşeli ve kenar uzunlukları=", round(dimA, 1), "cm", round(dimB, 1), "cm")
                else:
                    t.penup()
                    t.setpos(t.position()[0] + newpos, t.position()[1])
                    t.pendown()
                    cizdir(dA, dB)
                    oldpos = newpos + dA
                    newpos = oldpos
                    print(r, ".Cisim köşeli ve kenar uzunlukları=", round(dimA, 1), "cm", round(dimB, 1), "cm")


# Creates a windows application for show 'open file dialog'
root = tk.Tk()

# Gets the requested values of the height and widht.
windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()

# Gets both half the screen width/height and window width/height
positionRight = int(root.winfo_screenwidth() / 2.3 - windowWidth / 2)
positionDown = int(root.winfo_screenheight() / 2.5 - windowHeight / 2)

# Main window name
root.title("Edge Detector")
root.geometry("400x250+{}+{}".format(positionRight, positionDown))

image_path = filedialog.askopenfilename()  # Creates 'open file dialog'

labelspace = tk.Label(root, text = " ")
labelspace.pack()

label = tk.Label(root, text = "Selected path:")
label.pack()

entryText = tk.StringVar()
entry = tk.Entry(root, textvariable = entryText, width = 50)
entryText.set(image_path)
entry.pack()

labelspace = tk.Label(root, text = " ")
labelspace.pack()

label = tk.Label(root, text = "Enter width:")
label.pack()

image_width = tk.Entry(root)
image_width.pack()

labelspace = tk.Label(root, text = " ")
labelspace.pack()


def startpr():
    width = float(image_width.get())
    return mainprocess(entryText.get(), width)


startprocess = tk.Button(root, text = "Start", command = startpr, height = 3, width = 20)
startprocess.pack()

tk.mainloop()
