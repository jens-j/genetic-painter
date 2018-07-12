#!/usr/bin/env python3

import sys
from random import randint, uniform, sample
from datetime import datetime
from copy import copy, deepcopy

import numpy as np
from PIL import Image, ImageDraw, ImageChops
from PIL.ImageQt import ImageQt



class Gene:
    """ codes a single triangle with color and alpha. """

    MAX_ALPHA = 100
    MIN_ALPHA = 10
    STD_ALPHA = 10.0
    STD_COLOR = 20.0
    STD_SPACE = 0.02 # standard deviation as fraction of the image size
    STD_PROMINENCE = 0.02


    def __init__(self, genome, color=None, vertices=None, active=True):
        """ create a new random gene. 

            genome     -- the genome this gene is part of
            color      -- list of rgba color values
            vertices   -- list of (x, y) vertex location tuples
            prominence -- determines order of drawing
            active     -- boolean flag for enabling gene
        """

        self.genome = genome

        if vertices is not None:
            self.vertices = vertices
        else:
            x = uniform(0, 1)
            y = uniform(0, 1)

            self.vertices = []
            for i in range(3):
                self.vertices.append((x + uniform(-0.5, 0.5), y + uniform(-0.5, 0.5)))

        if color is not None:
            self.color = color
        else:
            self.color = [randint(0, 255), randint(0, 255), randint(0, 255)]
            if active:
                #self.color.append(randint(self.MIN_ALPHA, self.MAX_ALPHA))
                self.color.append(0)
            else:
                self.color.append(0)



    def mutate(self, rate):

        # mutute rgb channels
        for i in range(3):
            if uniform(0,1) < rate:
                self.color[i] = max(0, min(255, int(np.random.normal(self.color[i], self.STD_COLOR))))

        # mutate alpha channel
        if uniform(0,1) < rate:
            self.color[3] = max(self.MIN_ALPHA, min(self.MAX_ALPHA, int(np.random.normal(self.color[3], self.STD_ALPHA))))

        # mutate vertices
        for i in range(3):
            if uniform(0,1) < rate:
                x = max(-0.5, min(1.5, np.random.normal(self.vertices[i][0], self.STD_SPACE)))
            else:
                x = self.vertices[i][0]

            if uniform(0,1) < rate:
                y = max(-0.5, min(1.5, np.random.normal(self.vertices[i][1], self.STD_SPACE)))
            else:
                y = self.vertices[i][1]

            self.vertices[i] = (x, y)


class Genome:

    ACTIVE_FRAC = 0.1

    def __init__(self, length, genes=None):
        """ Create a new genome. 

            img_res -- resolution of the original image
            int_res -- internal resolution used to calculate fitness (x, y)
            length  -- the length of the genome (number of triangles)
            genes   -- optional list of genes
        """

        self.length = length 
        self.genes = []

        # Create a genome using a list of genes
        if genes is not None:
            assert len(genes) == length, '%d, %d' % (len(genes), length)
            for i in range(length):
                self.genes.append(Gene(self, 
                                       color=copy(genes[i].color), 
                                       vertices=copy(genes[i].vertices)))

        # Create a random new genome
        else:
            for i in range(length):

                self.genes.append(Gene(self, active=True))
                        
                # if i < length * self.ACTIVE_FRAC:
                #     self.genes.append(Gene(self, active=True))
                # else:
                #     self.genes.append(Gene(self, active=False))

        self.phenome = None


    @staticmethod
    def cross(genome0, genome1):
        """ Cross two genomes and return two children. """

        assert genome0.length == genome1.length

        g0 = []
        g1 = []

        for i in range(genome0.length):
            if uniform(0, 1) < 0.5:
                g0.append(genome0.genes[i])
                g1.append(genome1.genes[i])
            else:
                g1.append(genome0.genes[i])
                g0.append(genome1.genes[i])

        c0 = Genome(genome0.length, genes=g0)
        c1 = Genome(genome0.length, genes=g1)

        return c0, c1



    def drawPhenome(self, resolution):
        """ Return the phenome as an image. """

        # if self.phenome is None:

        img = Image.new('RGB', (resolution[0], resolution[1]))
        drw = ImageDraw.Draw(img, 'RGBA')

        for i in range(self.length):
            scaledVertices = [(x*resolution[0], y*resolution[1]) for (x, y) in self.genes[i].vertices]
            drw.polygon(scaledVertices, tuple(self.genes[i].color))

        del drw
        self.phenome = img

        return self.phenome



    def fitness(self, img):
        """ Calculate the difference between the phenome and a reference image. 

            img -- reference image 

            The fitness is defined as the difference between the phenome and the reference 
            image. The value returned is the sum of the difference of all pixels. So lower
            is better. 
        """

        #print('%s %s' % (self.drawPhenome().mode, img.mode))

        res = (img.width, img.height)

        # Subtract images
        diff = ImageChops.difference(self.drawPhenome(res), img)
        #diff.save('diff.png', 'PNG')

        # Convert to grayscale
        #grey = diff.convert('L')
        #grey.save('grey.png', 'PNG')

        # Convert image to numpy array and calculate the square of the error
        arr = np.asarray(diff, dtype=np.uint16)
        arr = arr**2

        # Return the sum of all elements
        return arr.sum(0).sum(0).sum(0)


    def mutate(self, rate):

        for i in range(self.length):
            self.genes[i].mutate(rate)

    

    def printGenome(self):
        """ print the genome in readable form """

        print('Genome:')
        for i in range(self.length):
            print('%s,%s, ' % (self.genes[i].vertices, self.genes[i].color), end='')
        print('')





