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

import td


# In[2]:


class instituicao:
    
    def __init__(self,M=100):
        
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
            


# In[61]:


class Jogador_DP:
    
    def __init__(self,t='indefinido',M=100,c=10,L=5,per=50,inf=0,sup=100,acoes=100):
        
        self.erro_controle=0
        
        self.tempo=per
        self.tipo=t
        self.commodities=c
        self.memoria=L
        self.p_limites=sorted([random.randint(inf,sup) for i in range(c)])
        self.M=M
        self.inf=inf
        self.sup=sup
        
        if t=='comprador':
            self.p_limites=sorted(self.p_limites,reverse=True)
        
        self.ordens_executadas=0
        self.executadas_valores=[]
        self.historico=[]
        
        #--------- Programação Dinâmica --------------
        self.V=np.zeros([(self.tempo+1),(self.commodities+1)])
        self.politica=np.zeros([(self.tempo+1),(self.commodities+1)])
        
        #--------- Temporal Difference --------------
        
        self.qtd_acoes=acoes
        
        colunas=[]
        for i in range(self.commodities+1):
            for j in range(1,self.tempo+1):
                colunas.append((i,j))
                
        z=np.zeros([self.qtd_acoes,((self.commodities+1)*self.tempo)])
        y=np.zeros([self.qtd_acoes,((self.commodities+1)*self.tempo)])

        self.Q=pd.DataFrame(z,columns=colunas)
        self.Nt=pd.DataFrame(y,columns=colunas)
        self.Nt[0:1]=100000
        self.Nt[(self.qtd_acoes-1):]=100000
        #t=0
        ##for i in range(0,int(len(self.Q)/3)):
        #    self.Q[i:i+1]=t
        #    t+=1
       # f=20
        #for i in range(int(len(self.Q)/3),int(2*len(self.Q)/3)):
         #   self.Q[i:i+1]=f
        #for i in range(int(2*len(self.Q)/3),len(self.Q)):
         #   self.Q[i:i+1]=t
         #   t-=1
            
        
        self.epsilon=0.5
        self.politica_TD=[[1-self.epsilon+(self.epsilon/self.qtd_acoes),self.epsilon/self.qtd_acoes]]
        
        
        
            
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
                            #self.B.append(msg[2])
                            #self.TB.append(msg[2])
                            #self.TA.append(msg[2])
                            self.TA.append(msg[2])
                            #self.A.append(msg[2])
                            
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
                            #self.A.append(msg[2])
                            #self.TA.append(msg[2])
                            #self.TB.append(msg[2])
                            self.TB.append(msg[2])
                            #self.B.append(msg[2])
                            
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
        
    # ____________________________________________________________________________________________________________________
    # ________________________________________ Tempo para fazer um lance  ________________________________________________
            
    def time_send_message(self,T=100,t=0,S=0,a=0.5):
        
        impa=a
        f=S*(T/(T-impa*t))
        
        return expon.rvs(scale=1/f)
    
    # ____________________________________________________________________________________________________________________
    # ________________________________________ Função Valor  ____________________________________________________________
    
    def funcao_valor(self,H,oa,ob,nr_com=0,N=0,gamma=0.9,M=100):
        
        def recursao(lance,N,com):
            
            if self.tipo=='comprador':
                        
                valor=(self.belief(H,lance=lance,oa=oa,ob=ob)*((self.p_limites[com-1]-lance)+gamma*self.V[N-1,com-1]))+                (1-self.belief(H,lance=lance,oa=oa,ob=ob))*gamma*self.V[N-1,com]
                    
            elif self.tipo=='vendedor':
                valor=(self.belief(H,lance=lance,oa=oa,ob=ob)*((lance-self.p_limites[com-1])+gamma*self.V[N-1,com-1]))+                (1-self.belief(H,lance=lance,oa=oa,ob=ob))*gamma*self.V[N-1,com]
                
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
    
    # ____________________________________________________________________________________________________________________
    # ________________________________________ Aprendizado por Reforço  - TD(0)___________________________________________
        
    def TD(self,oa,ob,lance,nr_com=0,N=0,gamma=0.9,alfa=0.9,epslon=0.1):
        
        if self.tipo=='comprador':
            if lance>=oa:
                self.Q[nr_com,N][oa-100]=self.Q[nr_com,N][oa-100]+alfa*((self.p_limites[nr_com]-oa)+gamma*max(self.Q[(ob-100):(199-100)][nr_com+1,N-1])-self.                                                                        Q[nr_com,N][oa-100])
            else:
                self.Q[nr_com,N][lance-100]=self.Q[nr_com,N][lance-100]+alfa*(gamma*max(self.Q[(ob-100):(oa-100)][nr_com,N-1])-self.Q[nr_com,N][lance-100])
            
        elif self.tipo=='vendedor':
            if lance<=ob:
                self.Q[nr_com,N][ob-100]=self.Q[nr_com,N][ob-100]+alfa*((ob-self.p_limites[nr_com])+gamma*max(self.Q[(100-100):(oa-100)][nr_com+1,N-1])-self.                                                                        Q[nr_com,N][ob-100])
            else:
                self.Q[nr_com,N][lance-100]=self.Q[nr_com,N][lance-100]+alfa*(gamma*max(self.Q[(ob-100):(oa-100)][nr_com,N-1])-self.Q[nr_com,N][lance-100])
        
    
    
    
    def ucb(self,oa,ob,t=0,com=0,N=0,c=2):
        QQ=[]
        
        if oa<=ob:
            if self.tipo=='vendedor':
                QQ.append((1,oa-100))
            else:
                QQ.append((1,ob-100))
        
        
        
        for i,a in enumerate(self.Nt[(ob-100):(oa-100)][com,N]):
            
            if a==0:
                QQ.append((1000000000,i+ob-100))
            else:
                
                QQ.append((self.Q[com,N][i+ob-100]+c*(math.sqrt((math.log(t))/(a))),i+ob-100))
        
        return max(QQ)[1]
        


# In[64]:


class market:
    
    def __init__(self,jogadores=10,co=10,per=10,paper_values=False,memo=5,FP_DP_TD=0,inf=0,sup=100,acoes=100):
        
        #self.tempo=tempo
        self.com=co
        self.per=per
        self.Trader=[td.agente(t='vazio',acoes=acoes,c=self.com,per=self.per,inf=inf,sup=sup)]
        self.jogadores=[]
        self.Trader_out=[]
        self.M=sup
        self.memo=memo
        self.inf=inf
        self.sup=sup
        
        self.negociacoes=[]
        self.FP_DP_TD=FP_DP_TD
        
        self.instituicao=instituicao(M=self.M)
        
        self.t=1
        #__________________
        # Resumo
        
        self.res_spread=[]
        self.res_spread_y=[]
        self.res_precos_executados=[]
        self.res_ordens_fim=[]
        
        self.eps_count=0
        
        #___________________
        
        
        for i in range(jogadores//2):

            tipo='vendedor'
            if FP_DP_TD==3:
                self.Trader.append(td.agente(t=tipo,acoes=acoes,c=self.com,per=self.per,inf=inf,sup=sup))
            #if DP==False:
            #    self.Trader.append(Jogador_DP(tipo,M=self.M,L=self.memo,tempo=self.tempo))
            #else:
            else:
                self.Trader.append(Jogador_DP(tipo,M=self.M,L=self.memo,c=self.com,per=self.per,inf=inf,sup=sup,acoes=acoes))
                
        for w in range(jogadores//2):
                               
            tipo='comprador'
            if FP_DP_TD==3:
                self.Trader.append(td.agente(t=tipo,acoes=acoes,c=self.com,per=self.per,inf=inf,sup=sup))
            #if DP==False:
             #   self.Trader.append(Jogador_DP(tipo,M=self.M,L=self.memo,tempo=self.tempo))
            #else:
            else:
                self.Trader.append(Jogador_DP(tipo,M=self.M,L=self.memo,c=self.com,per=self.per,inf=inf,sup=sup,acoes=acoes))
        
        if paper_values==True:
            
            f=[[3.3,2.25,2.1],[2.8,2.35,2.2],[2.6,2.4,2.15],[3.05,2.35,2.3]]
            c=[[1.9,2.35,2.5],[1.4,2.45,2.6],[2.1,2.3,2.55],[1.65,2.35,2.4]]

            for t in self.Trader:
                if t.tipo=='vendedor':
                    t.p_limites=c[0]
                    c.pop(0)
                elif t.tipo=='comprador':
                    t.p_limites=f[0]
                    f.pop(0)
                else:
                    t.p_limites=[]
            
        
        print('Valores Limites')
        print()
        for ind,g in enumerate(self.Trader):
            print(g.tipo,' ',ind,':',[round(i,2) for i in g.p_limites])
    
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
                if self.Trader[k].ordens_executadas>=10:
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
                
                if self.FP_DP_TD==1:
                    
                    n=int(self.per-perd)
                
                    com=self.Trader[k].ordens_executadas
                    
                    p=self.Trader[k].funcao_valor(self.instituicao.H,self.instituicao.oa,self.instituicao.ob,nr_com=com,N=n,gamma=0.9,M=self.M)
                    s=1
                    
                elif self.FP_DP_TD==0:
                    
                    s,p=self.Trader[k].surplus(self.instituicao.H,self.instituicao.oa,self.instituicao.ob)
                    
                elif self.FP_DP_TD==2:
                    
                    n=int(self.per-perd)
                    com=self.Trader[k].ordens_executadas
                    
                    if self.Trader[k].tipo=='comprador':
                        
                        p=self.Trader[k].ucb(oa=self.instituicao.oa,ob=self.Trader[k].p_limites[self.Trader[k].ordens_executadas],t=self.t,com=com,N=n,c=2)+100
                    
                    elif self.Trader[k].tipo=='vendedor':
                        
                        p=self.Trader[k].ucb(oa=self.Trader[k].p_limites[self.Trader[k].ordens_executadas],ob=self.instituicao.ob,t=self.t,com=com,N=n,c=2)+100
                    
                    self.t+=1
                    for jog in self.Trader:
                        
                        jog.Nt[com,n][(p-100)]+=1
                        
                        if jog.ordens_executadas>=self.com:
                            jog.TD(self.instituicao.oa,self.instituicao.ob,lance=p,nr_com=0,N=n,gamma=0.9,alfa=0.1,epslon=0.1)
                        else:
                            jog.TD(self.instituicao.oa,self.instituicao.ob,lance=p,nr_com=jog.ordens_executadas,N=n,gamma=0.9,alfa=0.1,epslon=0.1)
                    
                    s=1
                
                elif self.FP_DP_TD==3:
                    
                    n=int(self.per-perd)
                    com=self.Trader[k].ordens_executadas
                        
                    p=self.Trader[k].ucb(oa=self.instituicao.oa,ob=self.instituicao.ob,t=self.t,com=com,N=n,c=2)
                    
                    if p>=0:
                        self.t+=1
                        s=1
                        #self.Trader[k].Nt[com,n][p]+=1
                        #self.Trader[k].TD(oa=self.instituicao.oa,ob=self.instituicao.ob,lance=p,nr_com=com,N=n,gamma=0.9,alfa=0.1)
                        for jog in self.Trader:
                        
                            jog.Nt[com,n][p]+=1
                            if jog.ordens_executadas>=self.com:
                                #jog.TD(oa=self.instituicao.oa,ob=self.instituicao.ob,lance=p,nr_com=0,N=n,gamma=0.9,alfa=0.1)
                                jog.TD(oa=self.instituicao.oa,ob=self.instituicao.ob,lance=p,nr_com=(self.com-1),N=n,gamma=0.9,alfa=0.1)
                                pass
                            else:
                                jog.TD(oa=self.instituicao.oa,ob=self.instituicao.ob,lance=p,nr_com=jog.ordens_executadas,N=n,gamma=0.9,alfa=0.1)
                        
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
       
            
                
        


# In[1]:


#mercado=market2(10,tempo=50,co=5,per=20,M=201,paper_values=False,memo=30,FP_DP_TD=0)


# In[2]:


def iteracoes(mercado,it,pi=4):
    start=time.time()
    
    for j in range(1,it+1):
        mercado.inicio(ss_p=j,a=0.9,pi=pi)

    print(time.time()-start)


# In[350]:


def plot_sim(mercado):

    demanda_x=[]
    demanda_y=[]
    oferta_x=[]
    oferta_y=[]

    for k in mercado.Trader:
        if k.tipo=='vendedor':
            for i in k.p_limites:
                oferta_y.append(i)
        elif k.tipo=='comprador':
            for j in k.p_limites:
                demanda_y.append(j)

    demanda_y=sorted(demanda_y)
    oferta_y=sorted(oferta_y)
    copia_demanda_y=demanda_y.copy()
    copia_oferta_y=oferta_y.copy()

    for s,n in enumerate(copia_demanda_y):
        if s==(len(demanda_y)-1):
            continue

        if n==demanda_y[s+1]:
            pass
        else:
            demanda_y.append(n)

    for w,q in enumerate(copia_oferta_y):
        if w==(len(oferta_y)-1):
            continue

        if q==oferta_y[w+1]:
            pass
        else:
            oferta_y.append(q)

    demanda_y=sorted(demanda_y,reverse=True)
    oferta_y=sorted(oferta_y)

    c=0
    for s,n in enumerate(demanda_y):
        if s==(len(demanda_y)-1):
            continue

        if n==demanda_y[s+1]:
            demanda_x.append(c)
            c+=1

        else:
            demanda_x.append(c)
        
    c=0        
    for w,q in enumerate(oferta_y):
        if w==(len(oferta_y)-1):
            continue

        if q==oferta_y[w+1]:
            oferta_x.append(c)
            c+=1
        else:
            oferta_x.append(c)
        
    demanda_x.append(demanda_x[-1])
    oferta_x.append(oferta_x[-1])
    
    fig, ax1 = plt.subplots()
    plt.figure(num=None, figsize=(18, 18), dpi=80, facecolor='w', edgecolor='k')
    
    color = 'tab:red'
    color2='tab:blue'
    ax1.set_xlabel('Oferta/Demanda')
    ax1.set_ylabel('Preço', color=color)
    ax1.step(demanda_x, demanda_y, color=color,label='Demanda')
    ax1.step(oferta_x, oferta_y, color=color2,label='Oferta')
    ax1.tick_params(axis='y', labelcolor=color)   
    
    ax2 = ax1.twiny()  # instantiate a second axes that shares the same x-axis

    color3= 'tab:purple'
    ax2.set_xlabel('Quantidade Negociada', color=color3)  # we already handled the x-label with ax1
    ax2.scatter(mercado.res_spread_y,mercado.res_precos_executados,c=color3)
    ax2.tick_params(axis='x', labelcolor=color3)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    plt.show()

    


# In[3]:


def belief(n,ob,oa,j):
    teste=[]
    testey=[]
    for i in np.linspace(ob,oa,j):
        teste.append(mercado.Trader[n].belief(mercado.instituicao.H,lance=i,oa=mercado.instituicao.oa,ob=mercado.instituicao.ob))
        testey.append(i)
    plt.title('Função Crença')
    plt.ylabel('Probabilidade')
    plt.xlabel('Preço')
    plt.plot(testey,teste)


# In[4]:


#mercado_DP=market2(10,tempo=50,co=5,per=20,M=201,paper_values=False,memo=30,DP=True)

