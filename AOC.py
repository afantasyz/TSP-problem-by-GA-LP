import pandas as pd
import math
import random
import matplotlib.pyplot as plt
import time

class Ant:
    def __init__(self,citys) -> None:
        self.cityTable=citys
        self.routeTable=[]
        self.viewTable={}
        self.pathLength=0
        initialPos=random.choice(self.cityTable)
        self.cityTable.remove(initialPos)
        self.routeTable.append(initialPos)
        self.initialPos=initialPos
        self.nowPos=initialPos

    def move(self,nextPos):
        self.routeTable.append(nextPos)
        self.cityTable.remove(nextPos)
        self.nowPos=nextPos

    def calculateLength(self,cityInfo):
        for i in range(len(self.routeTable)-1):
            self.pathLength+=math.dist(cityInfo[self.routeTable[i]],cityInfo[self.routeTable[i+1]])

        
class Aoc:
    def __init__(self) -> None:
        self.AntNum=10  #蚂蚁数量
        self.cityInfo={}    #坐标记录
        self.citySign={}    #信息素记录
        self.citynum=51     #城市数量
        self.minPathGlobal=[]   
        self.minPathGlobalValue=1000
        self.decreaseV=0.8  #信息素衰减速率
        self.times=100   #迭代次数
        self.AntList=[]     #蚂蚁列表
        self.alpha=1    #信息素参数
        self.beta=1     #启发性参数
        self.Q=1    #施加信息素强度

    def readInfo(self):
        citysdf=pd.read_csv('citys.csv')
        citysdf.set_index('id',inplace=True)
        self.citynum=len(citysdf)
        for i in citysdf.index.tolist():
            self.cityInfo.update({i:(citysdf.loc[i,'xPos'],citysdf.loc[i,'yPos'])})
            self.citySign.update({i:1})
        
        self.valueRecord=[500]


    def initializeAnts(self):
        for i in range(self.AntNum):
            self.AntList.append(Ant(list(self.cityInfo.keys())))

    def updateInfo(self):
        #计算距离，获取精英,补充信息素
        bestAnt=min(self.AntList,key=lambda x:x.pathLength)
        self.minPathGlobal=bestAnt.routeTable
        self.minPathGlobalValue=bestAnt.pathLength
        for i in bestAnt.routeTable:
            self.citySign[i]=self.citySign[i]*self.decreaseV+self.Q

        # if bestAnt.pathLength<min(self.valueRecord):
        #     self.minPathGlobal=bestAnt.routeTable
        self.valueRecord.append(self.minPathGlobalValue)

    def oneGeneration(self):
        #所有蚂蚁进行寻路
        for one in self.AntList:
            while len(one.cityTable)>0:
                #获取启发性值
                one.viewTable.clear()
                for i in one.cityTable:
                    length=math.dist(self.cityInfo[i],self.cityInfo[one.nowPos])
                    if length<100:
                        length=(1/length)*(self.citySign[i])
                        one.viewTable.update({i:length})
                #寻找下一城市
                tepcity=list(one.viewTable.keys())
                # if len(one.viewTable)>10:
                #     tepcity=random.sample(tepcity,k=5)
                nextPos=max(tepcity,key=lambda x:one.viewTable[x])
                # totalInfo=sum(one.viewTable[i] for i in one.viewTable)
                # nextRate=[one.viewTable[i]/totalInfo for i in one.viewTable]
                # rate=random.random()
                # for i in range(len(nextRate)):
                #     rate-=nextRate[i]
                #     if rate<=0:
                #         nextPos=list(one.viewTable.keys())[i]
                #         break
                one.move(nextPos)
            one.routeTable.append(one.initialPos)
            one.calculateLength(self.cityInfo)

    def outputResult(self):
        print(self.minPathGlobalValue,self.minPathGlobal)
        plt.figure()
        for i in range(self.citynum-1):
            plt.scatter(self.cityInfo[i][0],self.cityInfo[i][1])
            plt.text(self.cityInfo[i][0],self.cityInfo[i][1],i)
            plt.plot([self.cityInfo[self.minPathGlobal[i]][0],self.cityInfo[self.minPathGlobal[i+1]][0]],[self.cityInfo[self.minPathGlobal[i]][1],self.cityInfo[self.minPathGlobal[i+1]][1]],color='r')
        plt.scatter(self.cityInfo[self.citynum-1][0],self.cityInfo[self.citynum-1][1])
        plt.plot([self.cityInfo[self.minPathGlobal[-1]][0],self.cityInfo[self.minPathGlobal[-2]][0]],[self.cityInfo[self.minPathGlobal[-1]][1],self.cityInfo[self.minPathGlobal[-2]][1]],color='r')
        plt.show()

        plt.figure()
        plt.plot(range(len(self.valueRecord)),self.valueRecord)
        plt.show()
        print(min(self.valueRecord))

if __name__ == "__main__":
    example=Aoc()
    example.readInfo()
    T1=time.time()
    while example.times>0:
        example.times-=1
        example.initializeAnts()
        example.oneGeneration()
        example.updateInfo()
    T2=time.time()
    example.outputResult()
    print('程序运行时间:%s毫秒' % ((T2 - T1)*1000))