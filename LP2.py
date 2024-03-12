import pandas as pd
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import matplotlib.pyplot as plt
import math

class LP:
    def __init__(self) -> None:
        self.cityInfo={}
        self.citynum=20
        self.minPathGlobal={}
        self.minPathGlobalValue=0      

    #创建距离文件
    def makecsv(self):
        info={'in':[],'out':[],'dis':[],'value':[]}
        for i in range(self.citynum):
            for j in range(self.citynum):
                info['in'].append(i)
                info['out'].append(j)
                info['dis'].append(math.dist(self.cityInfo[i],self.cityInfo[j]))
                info['value'].append(0)

        distancedf=pd.DataFrame(info)
        distancedf.to_csv('distanceInfo.csv',index=None)

    #读取城市数据
    def loadInfo(self):
        citysdf=pd.read_csv('citys.csv')
        citysdf.set_index('id',inplace=True)
        self.citynum=len(citysdf)
        for i in citysdf.index.tolist():
            self.cityInfo.update({i:(citysdf.loc[i,'xPos'],citysdf.loc[i,'yPos'])})
        
        self.distancedf=pd.read_csv('distanceInfo.csv')
        self.distancedf.set_index(['in','out'],inplace=True)

    #建立模型
    def creatModel(self):
        model=pyo.ConcreteModel()
        #集合
        model.cityIndex=pyo.Set(initialize=range(self.citynum))
        model.smallIndex=pyo.Set(initialize=range(self.citynum-1))

        #参数
        def disPram_rule(model,i,j):
            return self.distancedf.loc[(i,j),'dis']
        model.disPram=pyo.Param(model.cityIndex,model.cityIndex,initialize=disPram_rule)

        #变量
        model.x=pyo.Var(model.cityIndex,model.cityIndex,within=pyo.Binary)
        model.u=pyo.Var(model.cityIndex,within=pyo.PositiveReals)

        #目标函数
        def obj_rule(model):
            return sum(model.disPram[i,j]*model.x[i,j] for i in model.cityIndex for j in model.cityIndex)
        model.obj=pyo.Objective(rule=obj_rule,sense=pyo.minimize)

        ##单流入
        def singleInRule(model,i):
            return sum(model.x[i,j] for j in model.cityIndex if i !=j)==1
        model.singleInConstr=pyo.Constraint(model.cityIndex,rule=singleInRule)
        ##单流出
        def singleOutRule(model,j):
            return sum(model.x[i,j] for i in model.cityIndex if i !=j)==1
        model.singleOutConstr=pyo.Constraint(model.cityIndex,rule=singleOutRule)
        ##不原地转(不需要这个约束，因为会导致边数浪费不能完成单流入单流出约束)
        ##路径连续 上一秒的终点是下一秒的起点
        model.continueConstr=pyo.ConstraintList()
        for i in model.smallIndex:
            for j in model.smallIndex:
                if i != j:
                    model.continueConstr.add(model.u[i]-model.u[j]+self.citynum*model.x[i,j]<=self.citynum-1)


        #求解
        opt=SolverFactory('gurobi')
        # opt.options['MIPGap']=0.2
        # opt.options['solutionTarget']=1
        # opt.options['TimeLimit'] = 100
        result=opt.solve(model)
        result.write()
        
        # #导出结果
        for i in model.cityIndex:
            for j in model.cityIndex:
                if i!=j:
                    if pyo.value(model.x[i,j])>0.5:
                        # self.distancedf.loc[(i,j),'vlaue']=1
                        self.minPathGlobal.update({i:j})
    
        self.minPathGlobalValue=pyo.value(model.obj)
        return pyo.value(model.obj)
    
    def outputResult(self):
        plt.figure()
        for i in range(self.citynum):
            plt.scatter(self.cityInfo[i][0],self.cityInfo[i][1])
            plt.text(self.cityInfo[i][0],self.cityInfo[i][1],i)
            plt.plot([self.cityInfo[i][0],self.cityInfo[self.minPathGlobal[i]][0]],[self.cityInfo[i][1],self.cityInfo[self.minPathGlobal[i]][1]],color='r')
        plt.show()
        teppath=[]
        start=self.minPathGlobal[0]
        next=start
        while self.minPathGlobal[next]!=start:
            teppath.append(next)
            next=self.minPathGlobal[next]
        self.minPathGlobal=teppath
        print(self.minPathGlobal,self.minPathGlobalValue)


if __name__ =="__main__":       
    example=LP()
    example.loadInfo()
    example.creatModel()
    example.outputResult()
