#!/usr/bin/env python3


from solver import Population, Climber

import sys
import os
from datetime import datetime
from time import sleep
from threading import Thread
from math import sqrt, floor, ceil

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QColor, QPixmap, QImage
from PyQt5.QtCore import QPoint, QSize, QRectF, QTimer
from PyQt5.uic import loadUi
from PIL import Image, ImageDraw, ImageChops
from PIL.ImageQt import ImageQt


class Painter(QWidget):

    def __init__(self, parent=None):

        super(Painter, self).__init__()
        
        #self.setWindowTitle('Drawing')
        #self.setGeometry(300, 200, 800, 600)

        # Load gui
        self.ui = loadUi('%s/../gui/genetic.ui' %
                    os.path.dirname(os.path.realpath(sys.argv[0])))

        population = 4
        resolution = 300
        triangles  = 600

        ref = Image.open('../input/chameleon.jpg')
        ref = ref.convert("RGB")
        self.ref = ref
        thumb = ref.copy()
        thumb.thumbnail((resolution, resolution), Image.ANTIALIAS)
        self.thumbSize = thumb.size

        # col = int(ceil(sqrt(population)))
        # row = int(ceil(sqrt(population)))

        row = 8
        col = int(ceil(population / row))

        self.thumbs = {}
        for y in range(row):
            for x in range(col):
                name = 'lbl_t%d' % (y * col + x)
                self.thumbs[name] = QLabel()
                self.ui.layout_thumbnails.addWidget(self.thumbs[name], y, x)

        # Create a population
        self.population = Population(image=self.ref, int_res=resolution, 
                                     n_triangles=triangles, pop_size=population)
        #self.climber = Climber(ref, 20)

        self.startup = True

        # Start the worker thread
        self.worker = Thread(target=self.evolve)
        self.worker.setDaemon(True)
        self.worker.start()

        # # start display thread
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update)
        # self.timer.start(1000)


    def evolve(self):

        
        while True:

            if self.startup:
                    qimg = ImageQt(self.ref)
                    self.refPixmap = QPixmap.fromImage(qimg)
                    self.ui.lbl_original.setPixmap(self.refPixmap)
                    self.startup = False


            self.population.iterate()

            t = datetime.now()

            # for i in range(self.population.size):
            #     img = self.population.genomeRanking[i].drawPhenome(self.thumbSize)
            #     qimg = ImageQt(img)
            #     pixmap = QPixmap.fromImage(qimg)
            #     name = 'lbl_t%d' % i
            #     self.thumbs[name].setPixmap(pixmap)

            qimg = ImageQt(self.ref)
            self.refPixmap = QPixmap.fromImage(qimg)
            self.ui.lbl_original.setPixmap(self.refPixmap)

            img = self.population.bestGenome.drawPhenome(self.ref.size)
            #img.save('image.png', 'PNG')
            qimg = ImageQt(img)
            pixmap = QPixmap.fromImage(qimg)
            self.ui.lbl_painting.setPixmap(pixmap)

            self.ui.lbl_generation.setText(str(self.population.generation))
            self.ui.lbl_fitness.setText('%.2f %%' % self.population.fitnessPercentage)

            print('display:   %.2f ms' % (1000 * (datetime.now() - t).total_seconds()))
                
            #print(self.population.fitnessRanking)



    def update(self):
        """ Update the GUI. """
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    painter = Painter()
    painter.ui.show()
    app.exec_()
