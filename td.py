#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
import random
import altair as alt
alt.renderers.enable('notebook')
import matplotlib.pyplot as plt

from scipy import optimize
from scipy.stats import expon

import math

import time
from IPython.core.display import display, HTML
display(HTML("<style>.container { width:100% !important; }</style>"))


# In[3]:


class agente:   
    
    def __init__(self,t='indefinido',acoes=100,c=10,per=50,inf=0,sup=100):
        
        self.inf=inf
        self.sup=sup
        
        self.tipo=t
        self.p_limites=sorted([random.randint(self.inf+1,self.sup-1) for i in range(c)])
        
        if t=='comprador':
            self.p_limites=sorted(self.p_limites,reverse=True)
        
        self.ordens_executadas=0
        self.executadas_valores=[]
        
        self.qtd_acoes=acoes+1
        self.commodities=c
        self.tempo=per
        
        colunas=[]
        for i in range(self.commodities+1):
            for j in range(0,self.tempo+1):
                colunas.append((i,j))
                
        z=np.zeros([self.qtd_acoes,((self.commodities+1)*(self.tempo+1))])
        y=np.zeros([self.qtd_acoes,((self.commodities+1)*(self.tempo+1))])

        self.Q=pd.DataFrame(z,columns=colunas)
        self.Nt=pd.DataFrame(y,columns=colunas)
        self.Nt[0:1]=1000000
        self.Nt[acoes:]=1000000
        
    
    def TD(self,oa,ob,lance,nr_com=0,N=0,gamma=0.9,alfa=0.9):

        if self.tipo=='comprador':
            if (lance>=oa) or (lance<=ob):
                self.Q[nr_com,N][oa]=self.Q[nr_com,N][oa]+alfa*((self.p_limites[nr_com]-oa)+gamma*max(self.Q[(ob):(self.sup)][nr_com+1,N-1])-self.Q[nr_com,N][oa])
            else:
                self.Q[nr_com,N][lance]=self.Q[nr_com,N][lance]+alfa*(gamma*max(self.Q[(ob):(oa)][nr_com,N-1])-self.Q[nr_com,N][lance])

        elif self.tipo=='vendedor':
            if (lance>=oa) or (lance<=ob):
                self.Q[nr_com,N][ob]=self.Q[nr_com,N][ob]+alfa*((ob-self.p_limites[nr_com])+gamma*max(self.Q[(self.inf):(oa)][nr_com+1,N-1])-self.Q[nr_com,N][ob])
            else:
                self.Q[nr_com,N][lance]=self.Q[nr_com,N][lance]+alfa*(gamma*max(self.Q[(ob):(oa)][nr_com,N-1])-self.Q[nr_com,N][lance])


    def ucb(self,oa,ob,t=0,com=0,N=0,c=2):
        QQ=[]

        if oa<=ob or ((oa-ob)==1):
            if self.tipo=='vendedor':
                QQ.append((1,oa))
            else:
                QQ.append((1,ob))
        
        #for i,a in enumerate(self.Nt[(ob+1):(oa)][com,N]):
        for i,a in enumerate(self.Nt[com,N]):

            if a==0:
                if self.tipo=='comprador':
                    #QQ.append((1000000000-i+1+ob,i+1+ob))
                    QQ.append((1000000000-i,i))
                else:
                    #QQ.append((1000000000,i+1+ob))
                    QQ.append((1000000000,i))
            else:
                #QQ.append((self.Q[com,N][i+1+ob]+c*(math.sqrt((math.log(t))/(a))),i+1+ob))
                QQ.append((self.Q[com,N][i]+c*(math.sqrt((math.log(t))/(a))),i))
        
        if max(QQ)[0]<0:
            lance=-1
            
        else:
            lance=max(QQ)[1]
            if self.tipo=='vendedor':
                if lance==oa:
                    lance=lance
            else:
                if lance==ob:
                    lance=lance
        
        return lance


# In[1]:


#jogds=2
#agentes=[]
#bens=3
#a=11
#p=2
#for i in range(jogds//2):
   # tipo='vendedor'
   # agentes.append(agente(t=tipo,acoes=a,c=bens,per=p,inf=0,sup=10))
                
#for w in range(jogds//2):                   
   ## tipo='comprador'
   # agentes.append(agente(t=tipo,acoes=a,c=bens,per=p,inf=0,sup=10))

#print(agentes[0].p_limites)
#print(agentes[1].p_limites)


# In[9]:


#periodos=list(np.linspace(0,20-1,20))


# In[10]:


#k=agente(t='comprador',acoes=100,c=10,per=50,inf=0,sup=100)


# In[11]:


#for perd in periodos:
 #   n=int(20-perd)
  #  print(n)


# In[ ]:




