import pandas as pd
import random
import math
import numpy as np
from Aasterisk import Aasterisk
import matplotlib.pyplot as plt
import time

class GA:
    def __init__(self) -> None:
        self.pool=[]
        self.cityInfo={}
        self.minPathGlobal=[]
        self.minPathGlobalValue=10000
        self.pc=0.8
        self.pm=0.2
        self.size=50     #种群规模
        self.num=0      #基因数量
        self.times=1500   #迭代次数

    #初始化种群
    def raceInit(self):
        citysdf=pd.read_csv('citys.csv')
        citysdf.set_index('id',inplace=True)
        self.num=len(citysdf)
        for i in citysdf.index.tolist():
            self.cityInfo.update({i:(citysdf.loc[i,'xPos'],citysdf.loc[i,'yPos'])})
        # print(self.cityInfo)
        for i in range(0,self.size):
            teplist=list(self.cityInfo.keys())
            random.shuffle(teplist)
            self.pool.append(teplist[:])
        # print(self.pool)

    #获取初始解
    def getInitialResult(self):
        ones=Aasterisk()
        ones.readInfo()
        ones.solveProblem()
        self.pool.append(ones.minPathGlobal)
        self.minPathGlobal=ones.minPathGlobal

    #获取路径长度
    def getPathLength(self,path):
        pathLength=0
        for i in range(len(path)-1):
            # pathLength+=self.distancedf.loc[(path[i],path[i+1]),'dis']
            pathLength+=math.dist(self.cityInfo[path[i]],self.cityInfo[path[i+1]])
        pathLength+=int(math.dist(self.cityInfo[path[0]],self.cityInfo[path[-1]]))
        # pathLength+=self.distancedf.loc[(path[0],path[-1]),'dis']
        return pathLength

    def tournament(self):
        newPool=[]
        for i in range(self.size):
            selectPool=random.sample(self.pool,5)
            selectEntity=min(selectPool,key=lambda x:self.getPathLength(x))
            newPool.append(selectEntity[:])
        self.pool=newPool
        # print(newPool)

    #选择下一代子代
    def rouletteWheelSelection(self):
        fitness_values = [1 / self.getPathLength(path) for path in self.pool]
        total_fitness = sum(fitness_values)       
        # 计算选择概率
        selection_probabilities = [fitness / total_fitness for fitness in fitness_values]             
        # 选择
        new_pool=[]
        for i in range(self.size):
            rate=random.random()
            for i in range(len(self.pool)):
                rate-=selection_probabilities[i]
                if rate<=0:
                    new_pool.append(self.pool[i][:])
                    break 
        self.pool = new_pool

    #进行一轮交配   
    def crossOver(self):
        time=self.size/2
        newPool=[]
        while time>0:
            time-=1
            selectPaths=random.sample(self.pool,2)
            if(random.random()<self.pc):
                self.switchPoint(selectPaths[0], selectPaths[1])
                self.duplicate(selectPaths[0], selectPaths[1])

            if(random.random()<self.pm):
                self.mutation(selectPaths[0])
                self.mutation(selectPaths[1])
            newPool.append(selectPaths[0])
            newPool.append(selectPaths[1])    

        self.pool=newPool
        # print(self.pool)

    #交换基因片段           
    def switchPoint(self,path1,path2):
        #片段交换
        pointPiece=random.sample(range(self.num),2)
        while abs(pointPiece[0]-pointPiece[1])>7:
            pointPiece=random.sample(range(self.num),2)
        maxPoint=max(pointPiece)
        minPoint=min(pointPiece)
        tep=path1[minPoint:maxPoint]
        path1[minPoint:maxPoint]=path2[minPoint:maxPoint]
        path2[minPoint:maxPoint]=tep
        # return path1,path2

    #变异
    def mutation(self,path):
        selectPoint=random.sample(range(self.num),2)
        path[selectPoint[0]],path[selectPoint[1]]=path[selectPoint[1]],path[selectPoint[0]]
        # return path

    #去除重复基因
    def duplicate(self,path1,path2):
        containmap1={i:0 for i in self.cityInfo}
        duplicateList1=[]
        for i in path1:
            containmap1[i]+=1
        for i in containmap1:
            if containmap1[i]==2:
                duplicateList1.append(i)

        containmap2={i:0 for i in self.cityInfo}
        duplicateList2=[]
        for i in path2:
            containmap2[i]+=1
        for i in containmap2:
            if containmap2[i]==2:
                duplicateList2.append(i)

        while len(duplicateList1) !=0:
            id1=path1.index(duplicateList1.pop())
            id2=path2.index(duplicateList2.pop())
            path1[id1],path2[id2]=path2[id2],path1[id1]
                   
        # return path1,path2

    #寻找最短路径    
    def findMinPath(self):
        minPath=min(self.pool,key=lambda x:self.getPathLength(x))
        minPathValue=self.getPathLength(minPath)
        return minPath,minPathValue

    def outputResult(self):
        plt.figure()
        for i in range(self.num-1):
            plt.scatter(self.cityInfo[i][0],self.cityInfo[i][1])
            plt.plot([self.cityInfo[self.minPathGlobal[i]][0],self.cityInfo[self.minPathGlobal[i+1]][0]],[self.cityInfo[self.minPathGlobal[i]][1],self.cityInfo[self.minPathGlobal[i+1]][1]],color='r')
            plt.text(self.cityInfo[i][0],self.cityInfo[i][1],i)
        plt.scatter(self.cityInfo[self.num-1][0],self.cityInfo[self.num-1][1])
        plt.plot([self.cityInfo[self.minPathGlobal[-1]][0],self.cityInfo[self.minPathGlobal[0]][0]],[self.cityInfo[self.minPathGlobal[-1]][1],self.cityInfo[self.minPathGlobal[0]][1]],color='r')
        plt.show()

if __name__ =="__main__":

    example=GA()
    example.raceInit()
    example.getInitialResult()
    lengthRecord=[]
    maxtime=example.times

    T1=time.time()
    while example.times>0:
        example.pc=0.5+(maxtime-example.times)/maxtime*0.4
        example.pm=0.5-0.2*(maxtime-example.times)/maxtime
        example.times-=1
        example.tournament()
        # example.rouletteWheelSelection()
        example.crossOver()
        minPath,minPathValue=example.findMinPath()
        lengthRecord.append(minPathValue)
        if minPathValue<example.minPathGlobalValue:
            example.minPathGlobalValue=minPathValue
            example.minPathGlobal=minPath      

    T2=time.time()
    print(example.minPathGlobal,example.minPathGlobalValue)
    plt.figure()
    plt.plot(range(len(lengthRecord)),lengthRecord)
    plt.show()
    print('程序运行时间:%s毫秒' % ((T2 - T1)*1000))
    example.outputResult()
