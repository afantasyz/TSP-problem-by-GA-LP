import pandas as pd
import matplotlib.pyplot as plt
import math

class searchPoint:
    def __init__(self,cityList,pathValue,pos,pathList) -> None:
        self.pathValue=pathValue
        self.cityTable=cityList[:]
        self.cityTable.remove(pos)
        self.nowPos=pos
        self.value=pathValue+18*len(self.cityTable)
        self.pathTable=pathList[:]
        self.pathTable.append(pos)


class Aasterisk:
    def __init__(self) -> None:
        self.cityInfo={}
        self.num=50      #城市数量
        self.minPathGlobal=[]
        self.minPathGlobalValue=10000

    def readInfo(self):
        citysdf=pd.read_csv('citys.csv')
        citysdf.set_index('id',inplace=True)
        self.num=len(citysdf)
        for i in citysdf.index.tolist():
            self.cityInfo.update({i:(citysdf.loc[i,'xPos'],citysdf.loc[i,'yPos'])})

    def solveProblem(self):
        cityList=list(self.cityInfo.keys())
        start=cityList[0]
        searchList=[]
        pathList=[]
        searchList.append(searchPoint(cityList,0,start,pathList))

        while(len(searchList)>0):
            minPoint=min(searchList,key=lambda x:x.value)
            if len(minPoint.cityTable)==0:
                self.minPathGlobalValue=minPoint.value
                self.minPathGlobal=minPoint.pathTable
                break
            searchList.remove(minPoint)
            for i in minPoint.cityTable:
                newPathValue=int(math.dist(self.cityInfo[minPoint.nowPos],self.cityInfo[i]))
                # newPathValue=self.distancedf.loc[(minPoint.nowPos,i),'dis']
                if newPathValue<=35:
                    searchList.append(searchPoint(minPoint.cityTable,newPathValue+minPoint.pathValue,i,minPoint.pathTable))

        # print(start,self.minPathGlobalValue)
        

    def outputResult(self):
        print(self.minPathGlobalValue,self.minPathGlobal)
        plt.figure()
        for i in range(self.num-1):
            plt.scatter(self.cityInfo[i][0],self.cityInfo[i][1])
            plt.text(self.cityInfo[i][0],self.cityInfo[i][1],i)
            plt.plot([self.cityInfo[self.minPathGlobal[i]][0],self.cityInfo[self.minPathGlobal[i+1]][0]],[self.cityInfo[self.minPathGlobal[i]][1],self.cityInfo[self.minPathGlobal[i+1]][1]],color='r')
        plt.scatter(self.cityInfo[self.num-1][0],self.cityInfo[self.num-1][1])
        plt.plot([self.cityInfo[self.minPathGlobal[-1]][0],self.cityInfo[self.minPathGlobal[0]][0]],[self.cityInfo[self.minPathGlobal[-1]][1],self.cityInfo[self.minPathGlobal[0]][1]],color='r')
        plt.show()

if __name__ == "__main__":        
    example=Aasterisk()
    example.readInfo()
    example.solveProblem()
    example.outputResult()
