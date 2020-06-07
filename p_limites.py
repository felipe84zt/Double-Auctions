#!/usr/bin/env python
# coding: utf-8

# In[11]:


import random
import numpy as np


# In[37]:


class valores:
    
    def __init__(self,inf,sup,quantidade,tipo,distribuicao,media,dp):
        
        self.inf=inf
        self.sup=sup
        self.tipo=tipo
    
        if distribuicao=='normal':
            p_lim=sorted([int(np.random.normal(media,dp)) for i in range(quantidade)])
            p_lim=[j if j>inf else inf+1 for j in p_lim]
            p_lim=[k if k<sup else sup-1 for k in p_lim]
        else:
            p_lim=sorted([random.randint(inf,sup) for i in range(quantidade)])

        if tipo=='comprador':
            p_lim=sorted(p_lim,reverse=True)

        self.p_limites=p_lim


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




