from cmu_112_graphics import *
import random
from dataclasses import make_dataclass

def appStarted(app):
    app.cols = 28
    app.rows = 28
    app.margin = 20
    app.row = -1
    app.col = -1
    app.mouseMovedDelay = 10
    app.centers = []

def getCellBounds(app, row, col):
    cellW = (app.width - 2*app.margin)//app.cols
    cellH = (app.height - 2*app.margin)//app.rows
    x0 = app.margin + col*cellW
    x1 = x0 + cellW
    y0 = app.margin + row*cellH
    y1 = y0 + cellH
    #print("H,W: ", cellH,cellW)
    return (x0,y0,x1,y1)

def getCell(app, x,y):
    cellW = (app.width - 2*app.margin)//app.cols
    cellH = (app.height - 2*app.margin)//app.rows
    col = (x-app.margin)//cellW
    row = (y-app.margin)//cellH
    return (row, col)

def mousePressed(app, event):
    (app.row, app.col) = getCell(app, event.x, event.y)

def mouseDragged(app, event):
    app.centers.append((event.x, event.y))

def redrawAll(app, canvas):
    for col in range(app.cols):
        for row in range(app.rows):
            (x0,y0,x1,y1) = getCellBounds(app,row, col)
            x = (x0+x1)//2
            y = (y0+y1)//2
            cellIsDark = False
            for (xc,yc) in app.centers:
                if (xc-x)**2 +(yc-y)**2 < 16**2:
                    cellIsDark = True
            if cellIsDark:
                canvas.create_rectangle(x0,y0,x1,y1, fill = "gray")
            else:
                canvas.create_rectangle(x0,y0,x1,y1, fill = None)

runApp(width= 500, height = 500)