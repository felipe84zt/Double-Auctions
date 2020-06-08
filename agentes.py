#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import random

from scipy.stats import expon

import math

import time

import p_limites

from IPython.core.display import display, HTML
display(HTML("<style>.container { width:100% !important; }</style>"))


# In[2]:


class agente_FP:
    
    def __init__(self,p_lim,L=5):
        
        self.erro_controle=0
        self.p_limites=p_lim.p_limites
        self.tipo=p_lim.tipo
        self.tipo_agente = 'FP'
        self.commodities=len(self.p_limites)
        self.memoria=L
        
        self.inf=p_lim.inf
        self.sup=p_lim.sup
        
        self.ordens_executadas=0
        self.executadas_valores=[]
        self.historico=[]        
            
    def belief(self,H=[],lance=1,oa=100,ob=0):
        
        
        
        #__________________________ Definindo variáveis básicas para a função belief _________________________________
        
        self.H=H
        
        self.A=[]
        self.TA=[]
        self.B=[]
        self.TB=[]
        self.RA=[]
        self.RB=[]
        
        # ____________________________________________________________________________________________________________
        # ________________________Define a sequência H de ordens que o jogador lembra __________________________________
        
        controle=0
        
        for i in range(1,len(self.H)+1):
            
            if self.H[-i][0]!=0 and self.H[-i][1]!=0:
                
                controle+=1
                if controle>self.memoria:
                    self.H=self.H[-i+1:]
                    break
                
        for j in range(1,len(self.H)+1):
            
            if self.H[-j][0]!=0 and self.H[-j][1]!=0:
                
                if j==1:
                    H_controle=[]
                    break
                
                H_controle=self.H[-j+1:]
    
                break
                
        if len(self.H)==0:
            H_controle=[]
         
        if self.erro_controle==0:
            t_controle=0
        
            for i in range(1,len(self.H)+1):
                if self.H[-i][0]!=0 and self.H[-i][1]!=0:
                    t_controle+=1
            if t_controle==0:
                H_controle=[]
            else:
                self.erro_controle=1
            
            
        for k in range(1,len(H_controle)+1):
            
            if H_controle[-k][0]!=0:
                self.H=self.H[::-1]
                self.H.pop(self.H.index(H_controle[-k]))
                self.H=self.H[::-1]
                break
        for f in range(1,len(H_controle)+1):
            
            if H_controle[-f][1]!=0:
                self.H=self.H[::-1]
                self.H.pop(self.H.index(H_controle[-f]))
                self.H=self.H[::-1]
                break
                
      #  ___________________________________________________________________________________________________________
      # ________________________________________ Calcula A,TA,B,TB _________________________________________________
        
        
        # Calcula A e TA
        
        for ind,msg in enumerate(self.H):
            
            if msg[0]!=0 and msg[1]==0:
                self.A.append(msg[2])
                
            elif msg[0]!=0 and msg[1]!=0:
                for i in reversed(range(0,ind)):
                    if self.H[i][2]==msg[2]:
                        if self.H[i][0]!=0:
                            self.TA.append(msg[2])
                            
                            break
                        else:
                            break
                    
            
        # Calcula B e TB
        
        for ind,msg in enumerate(self.H):
            
            if msg[0]==0 and msg[1]!=0:
                self.B.append(msg[2])
                
            elif msg[0]!=0 and msg[1]!=0:
                for i in reversed(range(0,ind)):
                    if self.H[i][2]==msg[2]:
                        if self.H[i][1]!=0:
                            self.TB.append(msg[2])
                            
                            break
                        else:
                            break
        
        self.RA = [k for k in self.A if k not in self.TA]
        self.RB = [k for k in self.B if k not in self.TB]
    #  ___________________________________________________________________________________________________________
    # ________________________________________ Função belief _________________________________________________
    
        def funcao_belief(RA,TA,A,RB,TB,B,oa,ob,tipo="indefinido",lance=1):

            if tipo=="vendedor":

                TAG=0
                BG=0
                RAL=0

                for d in TA:
                    if d>=lance:
                        TAG+=1

                for d in B:
                    if d>=lance:
                        BG+=1

                for d in RA:
                    if d<=lance:
                        RAL+=1

                if lance>oa:
                    p=0
                    
                elif lance==self.sup:
                    p=0
                
                elif (TAG+BG+RAL)==0:
                    p=1
                else:
                    p=round((TAG+BG)/(TAG+BG+RAL),2)

                return p


            elif tipo=="comprador":

                TBL=0
                AL=0
                RBG=0

                for d in TB:
                    if d<=lance:
                        TBL+=1

                for d in A:
                    if d<=lance:
                        AL+=1

                for d in RB:
                    if d>=lance:
                        RBG+=1
                
                if lance<ob:
                    p=0
                
                elif lance==self.inf:
                    p=0
                
                elif (TBL+AL+RBG)==0:
                    p=1
                    
                else:
                    p=round((TBL+AL)/(TBL+AL+RBG),2)
                    

                return p
        
      
        
        if self.tipo=='vendedor':
            
            if lance in self.A:

                return funcao_belief(self.RA,self.TA,self.A,self.RB,self.TB,self.B,oa,ob,self.tipo,lance)

            else:

                A_controle=self.A.copy()
                A_controle.append(lance)
                A_controle.append(self.inf)
                A_controle.append(self.sup)
                A_controle=sorted(A_controle)

                lancek0=A_controle[A_controle.index(lance)-1]
                lancek1=A_controle[A_controle.index(lance)+1]
                pak0=funcao_belief(self.RA,self.TA,self.A,self.RB,self.TB,self.B,oa,ob,self.tipo,lancek0)
                pak1=funcao_belief(self.RA,self.TA,self.A,self.RB,self.TB,self.B,oa,ob,self.tipo,lancek1)

                Spline=np.array([[lancek0**3,lancek0**2,lancek0,1],                               [lancek1**3,lancek1**2,lancek1,1],                               [3*lancek0**2,2*lancek0,1,0],                               [3*lancek1**2,2*lancek1,1,0]])

                coeficiente=np.linalg.solve(Spline,np.array([pak0,pak1,0,0]))

                return coeficiente[0]*lance**3+coeficiente[1]*lance**2+coeficiente[2]*lance+coeficiente[3]
            
        elif self.tipo=='comprador':
            
            if lance in self.B:

                return funcao_belief(self.RA,self.TA,self.A,self.RB,self.TB,self.B,oa,ob,self.tipo,lance)

            else:

                B_controle=self.B.copy()
                B_controle.append(lance)
                B_controle.append(self.inf)
                B_controle.append(self.sup)
                B_controle=sorted(B_controle)

                lancek0=B_controle[B_controle.index(lance)-1]
                lancek1=B_controle[B_controle.index(lance)+1]
                pak0=funcao_belief(self.RA,self.TA,self.A,self.RB,self.TB,self.B,oa,ob,self.tipo,lancek0)
                pak1=funcao_belief(self.RA,self.TA,self.A,self.RB,self.TB,self.B,oa,ob,self.tipo,lancek1)

                Spline=np.array([[lancek0**3,lancek0**2,lancek0,1],                               [lancek1**3,lancek1**2,lancek1,1],                               [3*lancek0**2,2*lancek0,1,0],                               [3*lancek1**2,2*lancek1,1,0]])

                coeficiente=np.linalg.solve(Spline,np.array([pak0,pak1,0,0]))

                return coeficiente[0]*lance**3+coeficiente[1]*lance**2+coeficiente[2]*lance+coeficiente[3]

            
                
            
    
    # __________________________________________________________________________________________________________________
    # _____________________________________Expected Surplus ____________________________________________________________
    def surplus(self,H=[],oa=100,ob=0):
        
        def s(lance):
            if self.tipo=="comprador":
                
                return (self.p_limites[self.ordens_executadas]-lance)*self.belief(H,lance,oa,ob)
            elif self.tipo=="vendedor":
                return (lance-self.p_limites[self.ordens_executadas])*self.belief(H,lance,oa,ob)
        
        def otimizador(s,ob,oa,it=200):
    
            lances=np.linspace(ob+0.1,oa-0.1,it)
            resultados=[]
    
            for ba in lances:
        
                resultados.append(s(ba))
    
            return lances[resultados.index(max(resultados))]
        
        preco_otimo=otimizador(s,ob,oa)
        
        if self.tipo=="comprador":
            return max((self.p_limites[self.ordens_executadas]-preco_otimo)*self.belief(H,preco_otimo,oa,ob),0),        round(preco_otimo+0.1,2)
        elif self.tipo=="vendedor":
            return max((preco_otimo-self.p_limites[self.ordens_executadas])*self.belief(H,preco_otimo,oa,ob),0),        round(preco_otimo-0.1,2)


# In[ ]:





# In[3]:


class agente_DP(agente_FP):
    
    def __init__(self,p_lim,L,per,gamma):
        
        self.erro_controle=0
        self.p_limites=p_lim.p_limites
        self.tempo=per
        self.tipo=p_lim.tipo
        self.tipo_agente = 'DP'
        self.commodities=len(self.p_limites)
        self.memoria=L
        self.gamma=gamma
        
        self.inf=p_lim.inf
        self.sup=p_lim.sup
        
        self.ordens_executadas=0
        self.executadas_valores=[]
        self.historico=[]
        
        #--------- Programação Dinâmica --------------
        self.V=np.zeros([(self.tempo+1),(self.commodities+1)])
        self.politica=np.zeros([(self.tempo+1),(self.commodities+1)])
        
    # ____________________________________________________________________________________________________________________
    # ________________________________________ Função Valor  ____________________________________________________________
    
    def funcao_valor(self,H,oa,ob,nr_com=0,N=0):
        
        def recursao(lance,N,com):
            
            if self.tipo=='comprador':
                        
                valor=(self.belief(H,lance=lance,oa=oa,ob=ob)*((self.p_limites[com-1]-lance)+self.gamma*self.V[N-1,com-1]))+                (1-self.belief(H,lance=lance,oa=oa,ob=ob))*self.gamma*self.V[N-1,com]
                    
            elif self.tipo=='vendedor':
                valor=(self.belief(H,lance=lance,oa=oa,ob=ob)*((lance-self.p_limites[com-1])+self.gamma*self.V[N-1,com-1]))+                (1-self.belief(H,lance=lance,oa=oa,ob=ob))*self.gamma*self.V[N-1,com]
                
            else:
                print('error')
                    
            return valor
        
        valores=list(np.linspace(self.inf,self.sup-1,self.sup))
        resultados=[]
        preco_otimo=0
        
        commodity=self.commodities-nr_com
        
        for t in range(1,N+1):
            for x in range(1,commodity+1):
                for lance in valores:
                    resultados.append(recursao(lance,N=t,com=x))
                
                temp=np.copy(self.V)
                self.V[t,x-1]=max(resultados)
                self.politica[t,x-1]=valores[resultados.index(max(resultados))]
                resultados=[]
        
        return self.politica[N,nr_com]
    
    


# In[ ]:





# In[15]:


class agente_Q:   
    
    def __init__(self,p_lim,alfa,gamma,acoes=100,per=50):
        
        self.inf=p_lim.inf
        self.sup=p_lim.sup
        self.alfa=alfa
        self.gamma=gamma
        
        self.tipo=p_lim.tipo
        self.tipo_agente = 'Q'
        self.p_limites=p_lim.p_limites
       
        self.ordens_executadas=0
        self.executadas_valores=[]
        
        self.qtd_acoes=acoes+1
        self.commodities=len(self.p_limites)
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
        
    
    def Q_Learning(self,oa,ob,lance,nr_com=0,N=0):

        if self.tipo=='comprador':
            if (lance>=oa) or (lance<=ob):
                self.Q[nr_com,N][oa]=self.Q[nr_com,N][oa]+self.alfa*((self.p_limites[nr_com]-oa)+self.gamma*max(self.Q[(ob):(self.sup)][nr_com+1,N-1])-self.Q[nr_com,N][oa])
            else:
                self.Q[nr_com,N][lance]=self.Q[nr_com,N][lance]+self.alfa*(self.gamma*max(self.Q[(ob):(oa)][nr_com,N-1])-self.Q[nr_com,N][lance])

        elif self.tipo=='vendedor':
            if (lance>=oa) or (lance<=ob):
                self.Q[nr_com,N][ob]=self.Q[nr_com,N][ob]+self.alfa*((ob-self.p_limites[nr_com])+self.gamma*max(self.Q[(self.inf):(oa)][nr_com+1,N-1])-self.Q[nr_com,N][ob])
            else:
                self.Q[nr_com,N][lance]=self.Q[nr_com,N][lance]+self.alfa*(self.gamma*max(self.Q[(ob):(oa)][nr_com,N-1])-self.Q[nr_com,N][lance])


    def ucb(self,oa,ob,t=0,com=0,N=0,c=2):
        QQ=[]

        if oa<=ob or ((oa-ob)==1):
            if self.tipo=='vendedor':
                QQ.append((1,ob))
            else:
                QQ.append((1,oa))
        
        for i,a in enumerate(self.Nt[com,N]):

            if a==0:
                if self.tipo=='comprador':
                   
                    QQ.append((1000000000-i,i))
                else:
                   
                    QQ.append((1000000000+i,i))
            else:
            
                QQ.append((self.Q[com,N][i]+c*(math.sqrt((math.log(t))/(a))),i))
        
        if max(QQ)[0]<0:
            lance=-1
            
        else:
            lance=max(QQ)[1]
        
        return lance


# In[ ]:





# In[15]:


class agente_DQ:   
    
    def __init__(self,p_lim,alfa,gamma,acoes,per):
        
        self.inf=p_lim.inf
        self.sup=p_lim.sup
        self.alfa=alfa
        self.gamma=gamma
        
        self.tipo=p_lim.tipo
        self.tipo_agente = 'Q'
        self.p_limites=p_lim.p_limites
       
        self.ordens_executadas=0
        self.executadas_valores=[]
        
        self.qtd_acoes=acoes+1
        self.commodities=len(self.p_limites)
        self.tempo=per
        
        colunas=[]
        for i in range(self.commodities+1):
            for j in range(0,self.tempo+1):
                colunas.append((i,j))
                
        z=np.zeros([self.qtd_acoes,((self.commodities+1)*(self.tempo+1))])
        y=np.zeros([self.qtd_acoes,((self.commodities+1)*(self.tempo+1))])

        self.Q1=pd.DataFrame(z,columns=colunas)
        self.Q2=pd.DataFrame(z,columns=colunas)
        
        self.Nt=pd.DataFrame(y,columns=colunas)
        self.Nt[0:1]=1000000
        self.Nt[acoes:]=1000000
        
    
    def Q_Learning(self,oa,ob,lance,nr_com=0,N=0):
        
        sorteio=np.random.random()
        
        if sorteio<0.5:
            if self.tipo=='comprador':
                if (lance>=oa) or (lance<=ob):
                    self.Q1[nr_com,N][oa]=self.Q1[nr_com,N][oa]+self.alfa*((self.p_limites[nr_com]-oa)+self.gamma*self.Q2[nr_com+1,N-1][np.argmax(self.Q1[(ob):(self.sup)][nr_com+1,N-1])]-self.Q1[nr_com,N][oa])
                else:
                    self.Q1[nr_com,N][lance]=self.Q1[nr_com,N][lance]+self.alfa*(self.gamma*self.Q2[nr_com,N-1][np.argmax(self.Q1[(ob):(oa)][nr_com,N-1])]-self.Q1[nr_com,N][lance])

            elif self.tipo=='vendedor':
                if (lance>=oa) or (lance<=ob):
                    self.Q1[nr_com,N][ob]=self.Q1[nr_com,N][ob]+self.alfa*((ob-self.p_limites[nr_com])+self.gamma*self.Q2[nr_com+1,N-1][np.argmax(self.Q1[(self.inf):(oa)][nr_com+1,N-1])]-self.Q1[nr_com,N][ob])
                else:
                    self.Q1[nr_com,N][lance]=self.Q1[nr_com,N][lance]+self.alfa*(self.gamma*self.Q2[nr_com,N-1][np.argmax(self.Q1[(ob):(oa)][nr_com,N-1])]-self.Q1[nr_com,N][lance])


        elif sorteio>=0.5:
            if self.tipo=='comprador':
                if (lance>=oa) or (lance<=ob):
                    self.Q2[nr_com,N][oa]=self.Q2[nr_com,N][oa]+self.alfa*((self.p_limites[nr_com]-oa)+self.gamma*self.Q1[nr_com+1,N-1][np.argmax(self.Q2[(ob):(self.sup)][nr_com+1,N-1])]-self.Q2[nr_com,N][oa])
                else:
                    self.Q2[nr_com,N][lance]=self.Q2[nr_com,N][lance]+self.alfa*(self.gamma*self.Q1[nr_com,N-1][np.argmax(self.Q2[(ob):(oa)][nr_com,N-1])]-self.Q2[nr_com,N][lance])

            elif self.tipo=='vendedor':
                if (lance>=oa) or (lance<=ob):
                    self.Q2[nr_com,N][ob]=self.Q2[nr_com,N][ob]+self.alfa*((ob-self.p_limites[nr_com])+self.gamma*self.Q1[nr_com+1,N-1][np.argmax(self.Q2[(self.inf):(oa)][nr_com+1,N-1])]-self.Q2[nr_com,N][ob])
                else:
                    self.Q2[nr_com,N][lance]=self.Q2[nr_com,N][lance]+self.alfa*(self.gamma*self.Q1[nr_com,N-1][np.argmax(self.Q2[(ob):(oa)][nr_com,N-1])]-self.Q2[nr_com,N][lance])

            
            
    def ucb(self,oa,ob,t=0,com=0,N=0,c=2):
        QQ=[]
        Q=self.Q1+self.Q2

        if oa<=ob or ((oa-ob)==1):
            if self.tipo=='vendedor':
                QQ.append((1,ob))
            else:
                QQ.append((1,oa))
        
        for i,a in enumerate(self.Nt[com,N]):

            if a==0:
                if self.tipo=='comprador':
                   
                    QQ.append((1000000000-i,i))
                else:
                   
                    QQ.append((1000000000+i,i))
            else:
            
                QQ.append((Q[com,N][i]+c*(math.sqrt((math.log(t))/(a))),i))
        
        if max(QQ)[0]<0:
            lance=-1
            
        else:
            lance=max(QQ)[1]
        
        return lance


# In[ ]:





# In[ ]:


class agente_ES:   
    
    def __init__(self,p_lim,alfa,gamma,acoes=100,per=50):
        
        self.inf=p_lim.inf
        self.sup=p_lim.sup
        self.alfa=alfa
        self.gamma=gamma
        
        self.tipo=p_lim.tipo
        self.tipo_agente = 'Q'
        self.p_limites=p_lim.p_limites
       
        self.ordens_executadas=0
        self.executadas_valores=[]
        
        self.qtd_acoes=acoes+1
        self.commodities=len(self.p_limites)
        self.tempo=per
        
        colunas=[]
        for i in range(self.commodities+1):
            for j in range(0,self.tempo+1):
                colunas.append((i,j))
                
        z=np.ones([self.qtd_acoes,((self.commodities+1)*(self.tempo+1))])
        y=np.zeros([self.qtd_acoes,((self.commodities+1)*(self.tempo+1))])

        self.Q=pd.DataFrame(z,columns=colunas)
        self.Nt=pd.DataFrame(y,columns=colunas)
        self.Nt[0:1]=1000000
        self.Nt[acoes:]=1000000
        
    
    def Q_Learning(self,oa,ob,lance,nr_com=0,N=0):

        if self.tipo=='comprador':
            if (lance>=oa) or (lance<=ob):
                
                expected_Q=[max(0,self.Q[acao:acao+1][nr_com+1,N-1].values)*(self.Q[acao:acao+1][nr_com+1,N-1].values/sum(self.Q.loc[self.Q[nr_com+1,N-1]>0][(ob):(self.sup)][nr_com+1,N-1])) for acao in range(ob,self.sup)]
                
                self.Q[nr_com,N][oa]=self.Q[nr_com,N][oa]+self.alfa*((self.p_limites[nr_com]-oa)+self.gamma*sum(expected_Q)[0]-self.Q[nr_com,N][oa])
            else:
                
                expected_Q=[max(0,self.Q[acao:acao+1][nr_com,N-1].values) *(self.Q[acao:acao+1][nr_com,N-1].values/sum(self.Q.loc[self.Q[nr_com,N-1]>0][(ob):(oa)][nr_com,N-1])) for acao in range(ob,oa)]
                
                self.Q[nr_com,N][lance]=self.Q[nr_com,N][lance]+self.alfa*(self.gamma*sum(expected_Q)[0]-self.Q[nr_com,N][lance])

        elif self.tipo=='vendedor':
            if (lance>=oa) or (lance<=ob):
                
                expected_Q=[max(0,self.Q[acao:acao+1][nr_com+1,N-1].values) *(self.Q[acao:acao+1][nr_com+1,N-1].values/sum(self.Q[self.Q[nr_com+1,N-1]>0][(self.inf):(oa)][nr_com+1,N-1])) for acao in range(self.inf,oa)]
                
                self.Q[nr_com,N][ob]=self.Q[nr_com,N][ob]+self.alfa*((ob-self.p_limites[nr_com])+self.gamma*sum(expected_Q)[0]-self.Q[nr_com,N][ob])
            else:
                
                expected_Q=[max(0,self.Q[acao:acao+1][nr_com,N-1].values) *(self.Q[acao:acao+1][nr_com,N-1].values/sum(self.Q[self.Q[nr_com,N-1]>0][(ob):(oa)][nr_com,N-1])) for acao in range(ob,oa)]
                
                self.Q[nr_com,N][lance]=self.Q[nr_com,N][lance]+self.alfa*(self.gamma*sum(expected_Q)[0]-self.Q[nr_com,N][lance])


    def ucb(self,oa,ob,t=0,com=0,N=0,c=2):
        QQ=[]

        if oa<=ob or ((oa-ob)==1):
            if self.tipo=='vendedor':
                QQ.append((1,ob))
            else:
                QQ.append((1,oa))
        
        for i,a in enumerate(self.Nt[com,N]):

            if a==0:
                if self.tipo=='comprador':
                   
                    QQ.append((1000000000-i,i))
                else:
                   
                    QQ.append((1000000000+i,i))
            else:
            
                QQ.append((self.Q[com,N][i]+c*(math.sqrt((math.log(t))/(a))),i))
        
        if max(QQ)[0]<0:
            lance=-1
            
        else:
            lance=max(QQ)[1]
        
        return lance


# In[ ]:





# In[10]:


def define_agentes(jogadores,quantidade,per,memo,inf,sup,acoes,distribuicao,media,dp,alfa,gamma):
        
        tipo='vazio'
        p_lim=p_limites.valores(inf,sup,quantidade,tipo,distribuicao,media,dp)
        
        Trader_FP=[agente_FP(p_lim,L=memo)]
        Trader_DP=[agente_FP(p_lim,L=memo)]
        Trader_Q=[agente_FP(p_lim,L=memo)]
        Trader_DQ=[agente_FP(p_lim,L=memo)]
        Trader_ES=[agente_FP(p_lim,L=memo)]
     
        for i in range(jogadores//2):
            
            tipo='vendedor'
            p_lim=p_limites.valores(inf,sup,quantidade,tipo,distribuicao,media,dp)
            
            Trader_FP.append(agente_FP(p_lim,memo))
            Trader_DP.append(agente_DP(p_lim,memo,per,gamma))
            Trader_Q.append(agente_Q(p_lim,alfa,gamma,acoes,per))
            Trader_DQ.append(agente_DQ(p_lim,alfa,gamma,acoes,per))
            Trader_ES.append(agente_ES(p_lim,alfa,gamma,acoes,per))
                
        for w in range(jogadores//2):
                               
            tipo='comprador'
            p_lim=p_limites.valores(inf,sup,quantidade,tipo,distribuicao,media,dp)
            
            Trader_FP.append(agente_FP(p_lim,memo))
            Trader_DP.append(agente_DP(p_lim,memo,per,gamma))
            Trader_Q.append(agente_Q(p_lim,alfa,gamma,acoes,per))
            Trader_DQ.append(agente_DQ(p_lim,alfa,gamma,acoes,per))
            Trader_ES.append(agente_ES(p_lim,alfa,gamma,acoes,per))
        
        print('Valores Limites')
        print()
        for ind,g in enumerate(Trader_FP):
            print(g.tipo,' ',ind,':',[round(i,2) for i in g.p_limites])
            
        return [Trader_FP,Trader_DP,Trader_Q,Trader_DQ,Trader_ES]


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




