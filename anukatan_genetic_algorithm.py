'''
This file contains support code for B551 Hw6                                 # File version:  November 19, 2015                                            #

For questions related to genetic algorithms or the knapsack problem, any AI can be of help. For questions related to the support code itself, contact Alex at aseewald@indiana.edu.
'''
import sys
import math
import random
import pickle
import numpy as np
import pandas as pd
from scipy.stats import norm

def fitness(max_volume,volumes,prices):
    '''
    This should return a scalar which is to be maximized.
    max_volume is the maximum volume that the knapsack can contain.
    volumes is a list containing the volume of each item in the knapsack.
    prices is a list containing the price of each item in the knapsack, which is aligned with 'volumes'.
    '''
    if sum(volumes) <= 0 or sum(volumes) > max_volume :
        fitness = 0
    else:
        fitness = sum(prices)

    return fitness

def randomSelection(population,fitnesses):
    '''
    This should return a single chromosome from the population. The selection process should be random, but with weighted probabilities proportional
    to the corresponding 'fitnesses' values.
    '''
    # implementing roulette wheel with weighted probailites
    total_sum = sum(fitnesses)
    limit = random.randint(0, int(total_sum))
    estimated_sum = 0
    for i in range(len(population)):
        estimated_sum += fitnesses[i]
        if estimated_sum >= limit:
            return population[i]
    return population[random.randint(0, len(population) - 1)]

def reproduce(mom,dad,world):
    "This does genetic algorithm crossover. This takes two chromosomes, mom and dad, and returns two chromosomes."

    middle_value = len(mom) / 2
    mom = list(mom)
    dad = list(dad)

    child1 = mom[:middle_value] + dad[middle_value:]

    child2 = dad[:middle_value] + mom[middle_value:]



    return np.array([np.array(x) for x in child1]), np.array([np.array(y) for y in child2])

def mutate(child):
    "Takes a child, produces a mutated child."

    bit_index = random.choice(range(len(child)))

    child[bit_index] = int(not child[bit_index])
    return child

def compute_fitnesses(world,chromosomes):
    '''
    Takes an instance of the knapsack problem and a list of chromosomes and returns the fitness of these chromosomes, according to your 'fitness' function.
    Using this is by no means required, if you want to calculate the fitnesses in your own way, but having a single definition for this is convenient because
    (at least in my solution) it is necessary to calculate fitnesses at two distinct points in the loop (making a function abstraction desirable).

    Note, 'chromosomes' is required to be a 2D numpy array of boolean values (a fixed-size boolean array is the recommended encoding of a chromosome, and there should be multiple of these arrays, hence the matrix).
    '''
    return [fitness(world[0], world[1] * chromosome, world[2] * chromosome) for chromosome in chromosomes]

def generatePopulation(world, popsize):
    pop = []
    while popsize != 0:
        chromosomes = []
        for i in range(len(world[1])):
            chromosomes = chromosomes + [(random.choice([0,1]))]
        if sum(world[1]*np.array(chromosomes)) <= world[0]:
            pop.append(chromosomes)
            popsize -= 1
    population = np.array([np.array(x) for x in pop])
    return population

def genetic_algorithm(world,popsize,max_years,mutation_probability):
    '''
    world is a data structure describing the problem to be solved, which has a form like 'easy' or 'medium' as defined in the 'run' function.
    The other arguments to this function are what they sound like.
    genetic_algorithm *must* return a list of (chromosomes,fitnesses) tuples, where chromosomes is the current population of chromosomes, and fitnesses is
    the list of fitnesses of these chromosomes. 
    '''

    # The below generates the initial population
    chromosomes_list =[]
    size = len(world[1])


    population = generatePopulation(world, popsize)
    fitnesses = compute_fitnesses(world,population)
    for i in range(max_years):
            population = [randomSelection(population, fitnesses) for i in range(popsize)]
            fitnesses = np.array(fitnesses)
            population = np.array(population)
            sort_index = fitnesses.argsort()
            new_gen = list(population[sort_index])
            list(fitnesses).sort()
         #selecting the best two childs based on their fitness score -- Elitism
            for i in range(0, len(population)-3, 2):
                new_gen[i], new_gen[i+1] = reproduce(population[i], population[i+1],world)

            if random.choice(range(1, 100)) <= (mutation_probability * 100):
                mut = random.choice(range(len(new_gen)))
                new_gen[mut] = mutate(new_gen[mut])
            fitnesses = compute_fitnesses(world, new_gen)
            population = new_gen[:]

            chromosomes_list = chromosomes_list + [(population, fitnesses)]

    return chromosomes_list

def run(popsize,max_years,mutation_probability):
    '''
    The arguments to this function are what they sound like.
    Runs genetic_algorithm on various knapsack problem instances and keeps track of tabular information with this schema:
    DIFFICULTY YEAR HIGH_SCORE AVERAGE_SCORE BEST_PLAN'''
    table = pd.DataFrame(columns=["DIFFICULTY", "YEAR", "HIGH_SCORE", "AVERAGE_SCORE", "BEST_PLAN"])
    sanity_check = (10, [10, 5, 8], [100,50,80])
    chromosomes = genetic_algorithm(sanity_check,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'sanity_check', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)
    easy = (20, [20, 5, 15, 8, 13], [10, 4, 11, 2, 9] )
    chromosomes = genetic_algorithm(easy,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'easy', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)
    medium = (100, [13, 19, 34, 1, 20, 4, 8, 24, 7, 18, 1, 31, 10, 23, 9, 27, 50, 6, 36, 9, 15],
                   [26, 7, 34, 8, 29, 3, 11, 33, 7, 23, 8, 25, 13, 5, 16, 35, 50, 9, 30, 13, 14])
    chromosomes = genetic_algorithm(medium,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'medium', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)
    hard = (5000, norm.rvs(50,15,size=100), norm.rvs(200,60,size=100))
    chromosomes = genetic_algorithm(hard,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'hard', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)
    for difficulty_group in ['sanity_check','easy','medium','hard']: #,'sanity_check','easy',
        group = table[table['DIFFICULTY'] == difficulty_group]
        bestrow = group.ix[group['HIGH_SCORE'].argmax()]
        print("Best year for difficulty {} is {} with high score {} and chromosome {}".format(difficulty_group,int(bestrow['YEAR']), bestrow['HIGH_SCORE'], bestrow['BEST_PLAN']))
    table.to_pickle("results.pkl") #saves the performance data, in case you want to refer to it later. pickled python objects can be loaded back at any later point.

if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]))