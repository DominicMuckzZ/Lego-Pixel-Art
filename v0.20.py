import tkinter as tk
from tkinter import filedialog
import random
from PIL import Image,ImageTk
import threading
import math

filetypes = (("PNG File","*.png"),
             ("All Types","*.*"))

pieces = {}

def getBrickColours():
    colours = []
    with open("LegoColours.csv","r") as f_:
        reading = True
        while reading:
            data = f_.readline().replace("ï»¿","").replace("Â ","").replace("\n","")
            if data:
                dataSplit = data.split(",")
                colours.append((dataSplit[0],dataSplit[1]))
            else:
                reading = False            

    for colour in colours:
        pieces[colour] = Piece(colour[0],colour[1])
    return colours

class Piece():
    def __init__(self,name,colour):
        self.name = name
        self.colour = colour
        self.count = 0

    def addPiece(self):
        self.count += 1

class CanvasTooltip():
    def __init__(self,tag_or_id,label,canvas):
        self.widget = canvas.master
        self.canvas = canvas
        self.waittime = 500
        self.pixelSize = 14.928

        if "#" not in tag_or_id:
            tag_or_id = "#" + tag_or_id

        self.canvas.tag_bind(tag_or_id, "<Motion>", self.show)
        self.canvas.tag_bind(tag_or_id, "<Leave>", self.hide)
        self.label = label
        self.tipWindow = None
        
    def show(self,event):
        self.piece = self.label.piece
        
        text = f"{self.piece.name}"
        if self.tipWindow or not self.piece:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = event.x + x + self.widget.winfo_rootx() + 10
        y = event.y + y + cy + self.widget.winfo_rooty() + 5
        self.tipWindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x,y))
        label = tk.Label(tw, text=text,justify=tk.LEFT, background="#ffffe0",relief=tk.SOLID, borderwidth=1,font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
        

    def hide(self,event):
        tw = self.tipWindow
        self.tipWindow = None
        if tw:
            tw.destroy()
        
        
class Application():
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("760x508")
        self.root.title("Lego Art")

        self.palette = {}
        self.paletteLabels = []
        self.colourLookup = {}

        self.canvasFrame = tk.Frame(self.root)
        self.canvasFrame.place(x=260,y=58,width=495,height=445)

        self.canvas = tk.Canvas(self.canvasFrame)
        self.canvas.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        
        self.detailsFrame = tk.Frame(self.root,relief=tk.GROOVE,borderwidth=1)
        self.detailsFrame.place(x=260,y=13,width=495,height=40)

        self.sizeLabel = tk.Label(self.detailsFrame,text="Size:")
        self.sizeLabel.place(x=5,y=5,width=30,height=25)

        self.sizeData = tk.Label(self.detailsFrame,text="Width: \nHeight: ")
        self.sizeData.place(x=35,y=0,width=80)

        self.costLabel = tk.Label(self.detailsFrame,text="Estimated\nCost:")
        self.costLabel.place(x=115,y=0,width=60)

        self.costData = tk.Label(self.detailsFrame,text="£000.00")
        self.costData.place(x=175,y=5,width=45,height=25)
        
        self.piecesFrame = tk.LabelFrame(self.root,text="Pieces: ")
        self.piecesFrame.place(x=5,y=5,width=250,height=500)

        self.loadButton = tk.Button(self.root,text="Load File",command=self.loadFile)
        self.loadButton.place(x=150,y=5,width=80,height=20)

        self.showGridValue = tk.IntVar()
        self.showGridButton = tk.Checkbutton(self.detailsFrame,text="Show Grid: ",variable=self.showGridValue,onvalue=1,offvalue=0,command=self.updateGrid)
        self.showGridButton.place(x=400,y=10,width=80,height=20)

        self.root.mainloop()

    def loadFile(self):
        imagePath = self.getImagePath()

        if imagePath:
            self.sizeData.config(text="Width: \nHeight: ")
            self.costData.config(text="£000.00")
            
            if self.palette:
                for item in self.paletteLabels:
                    item.destroy()
            self.colourLookup = {}
            self.palette = {}
            self.paletteLabels = []
            self.canvas.delete("all")

            im = Image.open(imagePath)
            rgb_im = im.convert("RGBA")

            imageWidth = im.width
            imageHeight = im.height

            mmWidth = (imageWidth * 8)
            mmHeight = (imageHeight * 8)

            inchesWidth = mmWidth / 25.4
            feetWidth = math.floor(inchesWidth / 12)
            inchesWidth = math.ceil(inchesWidth - (12 * feetWidth))
            
            inchesHeight = mmHeight / 25.4
            feetHeight = math.floor(inchesHeight / 12)
            inchesHeight = math.ceil(inchesHeight - (12 * feetHeight))
            
            displayWidth = f"{feetWidth}'{inchesWidth}\""
            displayHeight = f"{feetHeight}'{inchesHeight}\""
            self.sizeData.config(text=f"Width: {displayWidth}\nHeight: {displayHeight}")

            brickColours = getBrickColours()
            width = self.showGridValue.get()
            pixelSize = max([min([(self.canvas.winfo_width()-10)/imageWidth,(self.canvas.winfo_height()-10)/imageHeight]),6])

            for y in range(imageHeight):
                for x in range(imageWidth):
                    r,g,b,a = rgb_im.getpixel((x,y))

                    if a != 0:
                        startX = 5+(x*pixelSize)
                        startY = 5+(y*pixelSize)
        
                        if (r,g,b) in self.colourLookup:
                            colourData = self.colourLookup[(r,g,b)]

                            colourData.addPiece()
            
                            self.canvas.create_rectangle(startX,startY,startX+pixelSize,startY+pixelSize,fill="#"+colourData.colour,width=width,tag=("piece",str("#"+colourData.colour)))
                            
                        else:
                            colourCode = self.rgbtohex(r,g,b)
                            colourData = self.findClosestColour(colourCode,brickColours)
                            
                            try:
                                self.palette[colourData].addPiece()
                            except:
                                self.palette[colourData] = pieces[colourData]
                                self.palette[colourData].addPiece()
                                self.colourLookup[(r,g,b)] = pieces[colourData]

                            self.canvas.create_rectangle(startX,startY,startX+pixelSize,startY+pixelSize,fill="#"+self.palette[colourData].colour,width=width,tag=("piece",str("#"+self.palette[colourData].colour)))
            
            self.createPaletteLabels()
            hbar = tk.Scrollbar(self.canvasFrame,orient=tk.HORIZONTAL)
            hbar.pack(side=tk.BOTTOM,fill=tk.X)
            hbar.config(command=self.canvas.xview)

            vbar = tk.Scrollbar(self.canvasFrame,orient=tk.VERTICAL)
            vbar.pack(side=tk.RIGHT,fill=tk.Y)
            vbar.config(command=self.canvas.yview)

            self.canvas.config(width=490,height=220)
            self.canvas.config(scrollregion=(0,0,startX+5,startY+5))
            self.canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
            self.canvas.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)

    def updateGrid(self):
        if self.showGridValue.get() == 0:
            self.canvas.itemconfigure('piece', width=0)
        else:
            self.canvas.itemconfigure('piece', width=1)

    def hexToDecimal(self,code):
        small = [8,4,2,1]
        big = [128,64,32,16,8,4,2,1]
        values = {"0":0,
                  "1":1,
                  "2":2,
                  "3":3,
                  "4":4,
                  "5":5,
                  "6":6,
                  "7":7,
                  "8":8,
                  "9":9,
                  "A":10,
                  "B":11,
                  "C":12,
                  "D":13,
                  "E":14,
                  "F":15}

        binaryValue = []
        codeValue = 0

        for letter in code:
            value = values[letter.upper()]
            for point in small:
                if value >= point:
                    value -= point
                    binaryValue.append(1)
                else:
                    binaryValue.append(0)

        for point in range(len(big)):
            if binaryValue[point] == 1:
                codeValue += big[point]
        return codeValue

    def findClosestColour(self,original,listOfColours):
        originalRGB = [self.hexToDecimal(original[0:2]),
               self.hexToDecimal(original[2:4]),
               self.hexToDecimal(original[4:6])] 
        colourLab = {}
        for colour in listOfColours:
            distance = 0
            newRGB = [self.hexToDecimal(colour[1][0:2]),
                   self.hexToDecimal(colour[1][2:4]),
                   self.hexToDecimal(colour[1][4:6])]

            distance = abs(originalRGB[0]-newRGB[0]) + abs(originalRGB[1]-newRGB[1]) + abs(originalRGB[2]-newRGB[2])
            colourLab[distance] = colour
            
        return colourLab[min(colourLab)]
        
    def rgbtohex(self,r,g,b):
        return f'{r:02x}{g:02x}{b:02x}'

    def createPaletteLabels(self):
        x = 0
        y = 0
        for piece in self.palette:
            piece = self.palette[piece]
            text = f"{piece.name}"
            self.paletteLabels.append(ColourLabel(piece,self.piecesFrame,x,y,self))
            x += 1
            if x == 2:
                x = 0
                y += 1
        
    def getImagePath(self):
        imagePath = filedialog.askopenfilename(filetypes=filetypes)
        return imagePath
    
    def updatePrice(self):
        totalCost = 0
        for colour in self.paletteLabels:
            if colour.checked.get() == 1:
                totalCost += 0.06 * colour.piece.count

        self.costData.config(text=f"£{round(totalCost,2)}")

class ColourTip():
    def __init__(self, widget):
        self.widget = widget
        self.tipWindow = None
        self.x = 0
        self.y = 0

    def showTip(self, text):
        self.text = text
        if self.tipWindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() +10
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipWindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x,y))
        label = tk.Label(tw, text=self.text,justify=tk.LEFT, background="#ffffe0",relief=tk.SOLID, borderwidth=1,font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hideTip(self):
        tw = self.tipWindow
        self.tipWindow = None
        if tw:
            tw.destroy()

class ColourIcon():
    def __init__(self,parent,piece,x,y,callback=None):
        self.piece = piece
        self.label = tk.Label(parent)
        self.label.place(x=x,y=y,width=20,height=20)
        self.label.configure(background=f"#{piece.colour}")
        
        self.toolTip = ColourTip(self.label)
        def enter(event):
            self.toolTip.showTip(self.piece.name)
        def leave(event):
            self.toolTip.hideTip()
        self.label.bind("<Enter>",enter)
        self.label.bind("<Leave>",leave)
        if callback:
            self.label.bind("<Button-1>", lambda e: callback(self.piece))

    def destroy(self):
        self.label.destroy()

class ColourUI():
    def __init__(self,application,parent,colour):
        self.application = application
        self.colourIcons = []
        self.parent = parent
        self.originalColour = colour
        self.newColour = colour

        self.window = tk.Tk()
        self.window.title("Colour Swap")
        countOfPieces = math.sqrt(len(pieces))
        uiSize = math.ceil(countOfPieces)*20
        self.window.geometry(f"{uiSize}x{uiSize}")

        x = 0
        y = 0
        for piece in pieces:
            piece = pieces[piece]
            colourIcon = ColourIcon(self.window,piece,x*20,y*20,callback=self.submit)
            self.colourIcons.append(colourIcon)
            
            x += 1
            if x > countOfPieces:
                x = 0
                y += 1

        self.window.mainloop()

    def submit(self,piece):
        self.parent.colourIcon.piece = piece
        self.parent.colourIcon.label.configure(background="#"+piece.colour)
        self.application.canvas.itemconfigure("#"+self.originalColour.colour, fill="#"+piece.colour)
        self.window.destroy()
            
class ColourLabel():
    def __init__(self,piece,parent,x,y,app):
        self.app = app
        self.piece = piece
        self.parent = parent

        self.colourIcon = ColourIcon(parent,piece,(120*x)+5,(y*20)+5)
        CanvasTooltip(piece.colour,self.colourIcon,app.canvas)

        self.colourCount = tk.Label(parent,text=f"x{piece.count}")
        self.colourCount.place(x=(120*x)+25,y=(y*20)+5,width=80,height=20)

        self.checked = tk.IntVar()
        self.colourCheck = tk.Checkbutton(parent,variable=self.checked,onvalue=1,offvalue=0,command=self.app.updatePrice)
        self.colourCheck.place(x=(120*x)+105,y=(y*20)+5,width=20,height=20)

        self.colourIcon.label.bind("<Button-1>", self.changeColour)

    def changeColour(self,e):
        colour = self.piece
        ColourUI(self.app,self,colour)

    def destroy(self):
        self.piece.count = 0
        self.colourIcon.destroy()
        self.colourCount.destroy()
        self.colourCheck.destroy()

if __name__ == "__main__":
    getBrickColours()
    application = Application()
