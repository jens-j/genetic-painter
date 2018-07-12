#!/usr/bin/env python3

from genetic import Genome

from datetime import datetime
from random import randint, uniform

from PIL import Image
import numpy as np


class Population:

    MIN_SP = 1.9
    MAX_SP = 0.1

    CROSSOVER_RATE = 1.0
    MUTATION_RATE = 0.001  

    def __init__(self, image, int_res, n_triangles, pop_size):
        """ Create a new population of random genomes. """

        assert pop_size % 2 == 0, 'Population size must be even'

        self.bestFitness = None
        self.bestGenome = None
        self.generation = 0
        self.fitnessRanking = None

        self.image = image
        self.int_res = int_res
        self.length = n_triangles
        self.size = pop_size #+ 1

        self.ref = self.image.copy()
        self.ref.thumbnail((100, 100), Image.ANTIALIAS)

        sp = np.linspace(self.MIN_SP, self.MAX_SP, self.size) # Selection pressure per ranking
        self.distribution = np.cumsum(sp) / np.sum(sp) # Cumulative selection distribution

        self.members = []
        for i in range(self.size):
            self.members.append(Genome(n_triangles))



    def iterate(self):
        """ Create the next generation. """

        # for i in range(self.size):
        #     for j in range(self.length):
        #         print(self.members[i].genes[j], end=', ')
        #     print('')
        # print('')

        newPop = []

        t = datetime.now()

        # Calculate each members fitness 
        fitness = []
        for i in range(self.size):
            fitness.append(self.members[i].fitness(self.ref))

        # Rank members by fitness
        ranking = zip(fitness, self.members)
        ranking = sorted(ranking, key=lambda x: x[0])
        self.fitnessRanking, self.genomeRanking = zip(*ranking)

        self.bestGenome = self.genomeRanking[0]

        # Calculate the best fitness as percentage 
        sum = self.fitnessRanking[0]
        total =  self.ref.width * self.ref.height * 3 * 255 * 255 # error is squared
        self.fitnessPercentage = 100 - (100.0 * sum / total)

        print('fitness:   %0.2f ms' % (1000 * (datetime.now() - t).total_seconds()))
        t = datetime.now()
         
        # Pick (population / 2) pairs to produce 2 offspring each
        for i in range(int(self.size / 2)):

            # Pick two (diffenent) members of the population as parents
            p0 = self._pickMate(self.genomeRanking)
            p1 = p0
            while p1 == p0:
                p1 = self._pickMate(self.genomeRanking)

            # Crossover
            if uniform(0, 1) < self.CROSSOVER_RATE:
                c0, c1 = Genome.cross(p0, p1)
            else:
                c0 = p0
                c1 = p1

            newPop.extend([c0, c1])

        self.members = newPop

        print('crossover: %0.2f ms' % (1000 * (datetime.now() - t).total_seconds()))
        t = datetime.now()

        for i in range(self.size):
            self.members[i].mutate(self.MUTATION_RATE)

        print('mutation:  %0.2f ms' % (1000 * (datetime.now() - t).total_seconds()))    

        self.generation += 1


    def _pickMate(self, ranking):
        """ Pick a mate from the population pool. """

        r0 = uniform(0, 1)
        for i, f in enumerate(self.distribution):
            if r0 < f:
                return ranking[i]



class Climber:

    #MUTATION_RATE = 0.5

    def __init__(self, img, triangles):

        
        self.length = triangles
        self.img = img

        self.genome = Genome(img.width, img.height, triangles)
        self.fitness = self.genome.fitness(img)

        self.generation = 0


    def climb(self):

        newGenome = Genome(self.img.width, self.img.height, self.length, genes=self.genome.genes)

        rate = 1.0
        
        while uniform(0,1) < rate:
            i = randint(0, self.length-1)
            newGenome.genes[i].mutate()
            rate = 2 * rate / 3
        

        newFitness = newGenome.fitness(self.img)
        #print('%d %d' % (self.fitness, newFitness))
        #print('')

        if newFitness < self.fitness:
           self.genome = newGenome
           self.fitness = newFitness

        self.generation += 1