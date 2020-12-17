

import collections
import sys
import math
import os 
import time
maxsize = float('inf')


# Function to copy temporary solution 
# to the final solution 
def copyToFinal(curr_path): 
    final_path[:N + 1] = curr_path[:] 
    final_path[N] = curr_path[0] 
  
# Function to find the minimum edge cost  
# having an end at the vertex i 
def firstMin(adj, i): 
    min = maxsize 
    for k in range(N): 
        if adj[i][k] < min and i != k: 
            min = adj[i][k] 
  
    return min
  
# function to find the second minimum edge  
# cost having an end at the vertex i 
def secondMin(adj, i): 
    first, second = maxsize, maxsize 
    for j in range(N): 
        if i == j: 
            continue
        if adj[i][j] <= first: 
            second = first 
            first = adj[i][j] 
  
        elif(adj[i][j] <= second and 
             adj[i][j] != first): 
            second = adj[i][j] 
  
    return second 
  
# function that takes as arguments: 
# curr_bound -> lower bound of the root node 
# curr_weight-> stores the weight of the path so far 
# level-> current level while moving 
# in the search space tree 
# curr_path[] -> where the solution is being stored 
# which would later be copied to final_path[] 
def TSPRec(adj, curr_bound, curr_weight,  
              level, curr_path, visited, start): 
    global final_res 
 
    # base case is when we have reached level N  
    # which means we have covered all the nodes once 
    time_now = time.time()
    if time_now - start > 1050:
        return
    if level == N: 
          
        # check if there is an edge from 
        # last vertex in path back to the first vertex 
        if adj[curr_path[level - 1]][curr_path[0]] != 0: 
              
            # curr_res has the total weight 
            # of the solution we got 
            curr_res = curr_weight + adj[curr_path[level - 1]][curr_path[0]] 
            if curr_res < final_res: 
                copyToFinal(curr_path) 
                final_res = curr_res 
        return
  
    # for any other level iterate for all vertices 
    # to build the search space tree recursively 
    def cmp(c):
        return c[0]
    var = []
    for i in range(N):
        temp = adj[curr_path[level-1]][i];
        var.append([temp, i])
    var = sorted(var, key=cmp)
    for i in range(N): 
        # Consider next vertex if it is not same  
        # (diagonal entry in adjacency matrix and  
        #  not visited already)
        if (adj[curr_path[level-1]][var[i][1]] != 0 and
                            visited[var[i][1]] == False): 
            temp = curr_bound 
            curr_weight += adj[curr_path[level - 1]][var[i][1]] 
  
            # different computation of curr_bound  
            # for level 2 from the other levels 
            if level == 1: 
                curr_bound -= ((firstMin(adj, curr_path[level - 1]) + 
                                firstMin(adj, var[i][1])) / 2) 
            else: 
                curr_bound -= ((secondMin(adj, curr_path[level - 1]) +
                                 firstMin(adj, var[i][1])) / 2) 
  
            # curr_bound + curr_weight is the actual lower bound  
            # for the node that we have arrived on. 
            # If current lower bound < final_res,  
            # we need to explore the node further 
            if curr_bound + curr_weight < final_res: 
                curr_path[level] = var[i][1]
                visited[var[i][1]] = True
                  
                # call TSPRec for the next level 
                TSPRec(adj, curr_bound, curr_weight,  
                       level + 1, curr_path, visited,start) 
  
            # Else we have to prune the node by resetting  
            # all changes to curr_weight and curr_bound 
            curr_weight -= adj[curr_path[level - 1]][var[i][1]] 
            curr_bound = temp 
  
            # Also reset the visited array 
            visited = [False] * len(visited) 
            for j in range(level): 
                if curr_path[j] != -1: 
                    visited[curr_path[j]] = True
  
# This function sets up final_path 
def TSP(adj): 
      
    # Calculate initial lower bound for the root node  
    # using the formula 1/2 * (sum of first min +  
    # second min) for all edges. Also initialize the  
    # curr_path and visited array 
    start = time.time()
    curr_bound = 0
    curr_path = [-1] * (N + 1) 
    visited = [False] * N 
  
    # Compute initial bound 
    for i in range(N): 
        curr_bound += (firstMin(adj, i) + 
                       secondMin(adj, i)) 
  
    # Rounding off the lower bound to an integer 
    curr_bound = math.ceil(curr_bound / 2) 
  
    # We start at vertex 1 so the first vertex  
    # in curr_path[] is 0 
    visited[0] = True
    curr_path[0] = 0
  
    # Call to TSPRec for curr_weight  
    # equal to 0 and level 1 
    TSPRec(adj, curr_bound, 0, 1, curr_path, visited,start) 



with open("output_bnb.csv", "a") as f:
    f.writelines("81688982, 40204942, 32329404\nBnB\nTSP\n")

base_dir = "C:/Users/Aditya/Downloads/271_AI_Project-main/Data"
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
    adj = temp
    N = len(temp)
    call_num = 0
    
    # final_path[] stores the final solution  
    # i.e. the // path of the salesman. 
    final_path = [None] * (N + 1) 
    
    # visited[] keeps track of the already 
    # visited nodes in a particular path 
    visited = [False] * N 
    
    # Stores the final minimum weight 
    # of shortest tour. 
    final_res = maxsize 
     
    start_time = time.time()
    TSP(adj)
    time_taken = time.time()-start_time

    with open("output_bnb.csv", "a") as f:
        f.writelines(file_name + ","+str(round(final_res, 8))+"\n")

         
