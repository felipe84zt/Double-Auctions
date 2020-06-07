#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


class instituicao:
    
    def __init__(self,M):
        
        self.reset=M
        self.oa=M
        self.ob=0
        self.H=[]
     
    def send_message(self,m=()):
        
        self.message=m
        
        
        if self.message[0]!=0: # se verdadeiro, então a mensagem veio de um vendedor
            
            if self.message[2]<=self.ob:
                
                
                for p in range(1,len(self.H)+1):
                        
                    if self.H[-p][1]!=0:
                        comprador=self.H[-p][1]
                        break
                
                h=(self.message[0],comprador,self.ob)
                self.H.append(h)
                
                self.ob=0
                #self.oa=self.reset
            
            elif self.message[2]<self.oa:
                
                h=self.message
                self.H.append(h)
                self.oa=self.message[2]
                
            else:
                pass
            
        else:  #mensagem veio de um comprador
            
            
            if self.message[2]>=self.oa:
                
                for p in range(1,len(self.H)+1):
                    
                    if self.H[-p][0]!=0:
                        vendedor=self.H[-p][0]
                        break
                
                h=(vendedor,self.message[1],self.oa)
                self.H.append(h)
                self.oa=self.reset
                #self.ob=0
                
            elif self.message[2]>self.ob:
                
                h=self.message
                self.H.append(h)
                self.ob=self.message[2]
                
            else:
                pass
            


# In[5]:


class market:
    
    def __init__(self,lista_agentes,periodos):
        
        self.Trader=lista_agentes
        
        self.com=lista_agentes[1].commodities
        self.per=periodos
        
        self.jogadores=[]
        self.Trader_out=[]
        self.inf=lista_agentes[1].inf
        self.sup=lista_agentes[1].sup
        
        self.negociacoes=[]
        
        self.instituicao=instituicao(self.sup)
        
        self.t=1
        #__________________
        # Resumo
        
        self.res_spread=[]
        self.res_spread_y=[]
        self.res_precos_executados=[]
        self.res_ordens_fim=[]
        
        self.eps_count=0
        
        #___________________
        
       
    def inicio(self,ss_p=1,a=0.5,pi=4):

        self.ordem=[]
        self.Trader_out=[]
        
        #self.a=a
        
        for w in self.Trader:
            w.ordens_executadas=0
            w.executadas_valores=[]
        
        self.jogadores=[]
        for ind,d in enumerate(self.Trader):
            self.jogadores.append(ind)
        
        if ss_p==1:
            self.s_p=ss_p
            
        s_t=0
        
        periodos=list(np.linspace(0,self.per-1,self.per))
    
        for perd in periodos:
            
            self.ordem=[]
            
            for k in self.jogadores:
                
                if k==0:
                    continue
                    
                if self.Trader[k].ordens_executadas>=self.Trader[k].commodities:
                    continue
                
                ativo=random.randint(1,pi)
                if ativo==1:
                    self.ordem.append(k)
 
            random.shuffle(self.ordem)
            self.negociacoes.append(self.ordem)
            
            for k in self.ordem:
                
                if(self.Trader[k].ordens_executadas==self.com):
                    print('Constraint error:',k)
                    print(self.jogadores)
                    continue
                    
                if k==0:
                    
                    print('ERROO')
                    break
                
                if self.Trader[k].tipo_agente=='DP':
                    
                    n=int(self.per-perd)
                
                    com=self.Trader[k].ordens_executadas
                    
                    p=self.Trader[k].funcao_valor(self.instituicao.H,self.instituicao.oa,self.instituicao.ob,nr_com=com,N=n)
                    s=1
                    
                elif self.Trader[k].tipo_agente=='FP':
                    
                    s,p=self.Trader[k].surplus(self.instituicao.H,self.instituicao.oa,self.instituicao.ob)
                    
                elif self.Trader[k].tipo_agente=='Q':
                    
                    n=int(self.per-perd)
                    com=self.Trader[k].ordens_executadas
                        
                    p=self.Trader[k].ucb(oa=self.instituicao.oa,ob=self.instituicao.ob,t=self.t,com=com,N=n,c=2)
                    
                    if p>=0:
                        self.t+=1
                        s=1
                        
                        for jog in self.Trader[1:]:
                        
                            jog.Nt[com,n][p]+=1
                            if jog.ordens_executadas>=self.com:
                                jog.Q_Learning(oa=self.instituicao.oa,ob=self.instituicao.ob,lance=p,nr_com=(self.com-1),N=n)
                                
                            else:
                                jog.Q_Learning(oa=self.instituicao.oa,ob=self.instituicao.ob,lance=p,nr_com=jog.ordens_executadas,N=n)
                        
                    else:
                        s=0
                        
                if self.Trader[k].tipo=='vendedor':
                    
                    if s!=0:
                        
                        temp=self.instituicao.ob
                        self.instituicao.send_message(m=(k,0,p))
                        
                       
                        if p<=temp:
                            
                            self.Trader[k].executadas_valores.append(temp)
                            self.Trader[k].ordens_executadas+=1
                            if len(self.Trader[k].executadas_valores)==len(self.Trader[k].p_limites):
                                #print('Jogador: ',k,', no tempo ',periodos.index(periodos[pd]))
                                self.Trader_out.append((self.Trader[k],k))
                                self.jogadores.pop(self.jogadores.index(k))
                                
                            self.Trader[self.instituicao.H[-1][1]].executadas_valores.append(temp)
                            self.Trader[self.instituicao.H[-1][1]].ordens_executadas+=1
                            if len(self.Trader[self.instituicao.H[-1][1]].executadas_valores)==len(self.Trader[self.instituicao.H[-1][1]].p_limites):
                                #print('Jogador: ',k,', no tempo ',periodos.index(periodos[pd]))
                                self.Trader_out.append((self.Trader[self.instituicao.H[-1][1]],self.instituicao.H[-1][1]))
                                self.jogadores.pop(self.jogadores.index(self.instituicao.H[-1][1]))
                            #self.res_precos_executados.append((temp,time.time()-start))
                            self.res_precos_executados.append(temp)
                            self.res_spread_y.extend([self.s_p])
                            self.s_p+=1
                            
                elif self.Trader[k].tipo=='comprador':
                    
                    if s!=0:
                        
                        temp=self.instituicao.oa
                        self.instituicao.send_message(m=(0,k,p))
                    
                        if p>=temp:
                            
                            self.Trader[k].executadas_valores.append(temp)
                            self.Trader[k].ordens_executadas+=1
                            if len(self.Trader[k].executadas_valores)==len(self.Trader[k].p_limites):
                                #print('Jogador: ',k,', no tempo ',periodos.index(periodos[pd]))
                                self.Trader_out.append((self.Trader[k],k))
                                self.jogadores.pop(self.jogadores.index(k))
                                
                            self.Trader[self.instituicao.H[-1][0]].executadas_valores.append(temp)
                            self.Trader[self.instituicao.H[-1][0]].ordens_executadas+=1
                            if len(self.Trader[self.instituicao.H[-1][0]].executadas_valores)==len(self.Trader[self.instituicao.H[-1][0]].p_limites):
                                #print('Jogador: ',k,', no tempo ',periodos.index(periodos[pd]))
                                self.Trader_out.append((self.Trader[self.instituicao.H[-1][0]],self.instituicao.H[-1][0]))
                                self.jogadores.pop(self.jogadores.index(self.instituicao.H[-1][0]))
                            #self.res_precos_executados.append((temp,time.time()-start))
                            self.res_precos_executados.append(temp)
                            self.res_spread_y.extend([self.s_p])
                            self.s_p+=1                        
       


# In[ ]:





# In[ ]:





# In[ ]:




