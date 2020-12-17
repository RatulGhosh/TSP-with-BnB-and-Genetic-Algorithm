#!/usr/bin/env python
# coding: utf-8

# In[25]:


import numpy as np, random, operator, pandas as pd, matplotlib.pyplot as plt
from tqdm import tqdm
import collections
from tsp_solver.greedy import solve_tsp
import os
import time

with open("output_sls.csv", "a") as f:
    f.writelines("81688982, 40204942, 32329404\nSLS\nTSP\n")

base_dir = "/data"
file_list = os.listdir(base_dir)

def cmp(c):
    return (int(c.split('-')[2])/1000)+(int(c.split('-')[3])/10000000)+(int(c.split('-')[4])/100)+(int(c.split('-')[5])/25)


file_list = sorted([x for x in file_list if x[-3:] == "txt"])

file_list = sorted(file_list, key = cmp)


for file_name in file_list:
    with open(os.path.join(base_dir, file_name), "r") as f:
        temp = f.readlines()

    temp = [x[:-1].split() for x in temp[1:]]
    temp = [[float(y) for y in x] for x in temp]


    # In[7]:


    early_stop = collections.deque(maxlen=100)


    # In[20]:


    class Fitness:
        def __init__(self, route):
            self.route = route
            self.distance = 0
            self.fitness= 0.0
        
        def routeDistance(self):
            if self.distance ==0:
                pathDistance = 0
                for i in range(0, len(self.route)):
                    fromCity = self.route[i]
                    toCity = None
                    if i + 1 < len(self.route):
                        toCity = self.route[i + 1]
                    else:
                        toCity = self.route[0]
                    pathDistance += temp[fromCity][toCity]
                self.distance = pathDistance
            return self.distance
        
        def routeFitness(self):
            if self.fitness == 0:
                self.fitness = 1 / float(self.routeDistance())
            return self.fitness


    # In[35]:


    def createRoute(num_cities):
        route = random.sample(list(range(num_cities)), num_cities)
        return route


    def cmp_key(c):
        lst = temp[c]
        lst = lst[:c]+lst[c+1:]
        return np.argmin(lst)

    def create_a_path_n(num_cities):
        cities = list(range(num_cities))
        city = random.sample(cities,1)[0]
        path = [city]
        remaining_cities = [rc for rc in cities if rc!=city]
        #loop while the list of remaining cities are not empty
        while remaining_cities:
            #get the minimum distance
            city = min(remaining_cities, key=cmp_key)
            path.append(city)
            remaining_cities.remove(city)
        return path

    def initialPopulation(popSize, num_cities):
        population = []

        for i in range(0, popSize-1):
            population.append(create_a_path_n(num_cities))
        
        # path = solve_tsp(temp)
        # population.append(path)
        return population

    def rankRoutes(population):
        fitnessResults = {}
        for i in range(0,len(population)):
            fitnessResults[i] = Fitness(population[i]).routeFitness()
        return sorted(fitnessResults.items(), key = operator.itemgetter(1), reverse = True)


    def selection(popRanked, eliteSize):
        selectionResults = []
        df = pd.DataFrame(np.array(popRanked), columns=["Index","Fitness"])
        df['cum_sum'] = df.Fitness.cumsum()
        df['cum_perc'] = 100*df.cum_sum/df.Fitness.sum()
        
        for i in range(0, eliteSize):
            selectionResults.append(popRanked[i][0])
        for i in range(0, len(popRanked) - eliteSize):
            pick = 100*random.random()
            for i in range(0, len(popRanked)):
                if pick <= df.iat[i,3]:
                    selectionResults.append(popRanked[i][0])
                    break
        return selectionResults


    def matingPool(population, selectionResults):
        matingpool = []
        for i in range(0, len(selectionResults)):
            index = selectionResults[i]
            matingpool.append(population[index])
        return matingpool


    def breed(parent1, parent2):
        child = []
        childP1 = []
        childP2 = []
        
        geneA = int(random.random() * len(parent1))
        geneB = int(random.random() * len(parent1))
        
        startGene = min(geneA, geneB)
        endGene = max(geneA, geneB)

        for i in range(startGene, endGene):
            childP1.append(parent1[i])
            
        childP2 = [item for item in parent2 if item not in childP1]

        child = childP2[:startGene] + childP1 + childP2[startGene:]
        return child


    def breedPopulation(matingpool, eliteSize):
        children = []
        length = len(matingpool) - eliteSize
        pool = random.sample(matingpool, len(matingpool))

        for i in range(0,eliteSize):
            children.append(matingpool[i])
        
        for i in range(0, length):
            child = breed(pool[i], pool[len(matingpool)-i-1])
            children.append(child)
        return children



    def mutate(individual, mutationRate):
        for swapped in range(len(individual)):
            if(random.random() < mutationRate):
                swapWith = int(random.random() * len(individual))
                
                city1 = individual[swapped]
                city2 = individual[swapWith]
                
                individual[swapped] = city2
                individual[swapWith] = city1
        return individual



    def mutatePopulation(population, mutationRate):
        mutatedPop = []
        
        for ind in range(0, len(population)):
            mutatedInd = mutate(population[ind], mutationRate)
            mutatedPop.append(mutatedInd)
        return mutatedPop


    def nextGeneration(currentGen, eliteSize, mutationRate, greedy = False):
        popRanked = rankRoutes(currentGen)
        selectionResults = selection(popRanked, eliteSize)
        matingpool = matingPool(currentGen, selectionResults)
        children = breedPopulation(matingpool, eliteSize)
        nextGeneration = mutatePopulation(children, mutationRate)
        if not greedy:
            return nextGeneration

        path = solve_tsp(temp)
        nextGeneration.pop()
        nextGeneration.append(path)
        return nextGeneration

    def geneticAlgorithm(population, popSize, eliteSize, mutationRate, generations):
        pop = initialPopulation(popSize, len(population))
        progress = []
        progress1 = []
        last_distance =  1 / rankRoutes(pop)[0][1]
        min_distance = last_distance
        early_stop.append(last_distance)
        progress.append(last_distance)
        best_route = pop[rankRoutes(pop)[0][0]]
        
        print("Initial distance: " + str(1 / rankRoutes(pop)[0][1]))    
        
        for i in tqdm(range(0, generations)):
            if i == 400:
                pop = nextGeneration(pop, eliteSize, mutationRate, greedy=True)
            else:
                pop = nextGeneration(pop, eliteSize, mutationRate)
                
            last_distance = 1 / rankRoutes(pop)[0][1]
        
            #store the best route
            if last_distance < min_distance:
                min_distance = last_distance
                best_route = pop[rankRoutes(pop)[0][0]]

            #early stop
            progress1.append(abs(last_distance - min(early_stop)))
            if abs(last_distance - max(early_stop))<0.00000001 and i > 800:
                break
                
            progress.append(last_distance)
            early_stop.append(last_distance)

        
        print("Final distance: " + str(min_distance))
        return progress, best_route, round(min_distance+temp[best_route[-1]][best_route[0]], 2), i


    # In[53]:



    start_time = time.time()
    progress, best_route, min_distance, num_episodes = geneticAlgorithm(population=temp, popSize=100, 
                                                                                eliteSize=20, mutationRate=0.1/len(temp), 
                                                                                generations=5000)
    time_taken = time.time()-start_time

    with open("output_sls.csv", "a") as f:
        f.writelines(file_name+","+str(round(min_distance, 2))+","+str(num_episodes)+"\n")





