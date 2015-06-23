"""
Probability density functions compliant with the lmfit package
Author: Cyril Grima <cyril.grima@gmail.com>
"""

import math 
import numpy as np
from scipy import stats, integrate
from scipy.special import jv, kv, digamma



def gamma(params, x, data=None, eps=None):
    """Gamma PDF from scipy with adequate variables
    """
    # Initialisation
    mu = params['mu']
    if hasattr(mu, 'value'): mu = mu.value #debug due to lmfit.minimize
    # Model function
    model = stats.gamma.pdf(x, mu, scale = 1)
    model = np.nan_to_num(model)

    if data is None:
        return model
    if eps is None:
        return (model - data) #residual
    return (model - data)/eps



def rayleigh(params, x, data=None, eps=None):
    """Rayleigh PDF from scipy with adequate variables
    """
    # Initialisation
    s = params['s']
    # Model function
    model = stats.rayleigh.pdf(x, scale = s)
    model = np.nan_to_num(model)

    if data is None:
        return model
    if eps is None:
        return (model - data) #residual
    return (model - data)/eps



def rice(params, x, data=None, eps=None):
    """Rice PDF from scipy with adequate variables
    """
    # Initialisation
    a = params['a']
    s = params['s']
    # Model function
    model = stats.rice.pdf(x, a/s, scale = s)
    model = np.nan_to_num(model)

    if data is None:
        return model
    if eps is None:
        return (model - data) #residual
    return (model - data)/eps



def k(params, x, data=None, eps=None):
    """K PDF
    """
    # Initialisation
    s = params['s']
    mu = params['mu']
    # Model function
    b = np.sqrt(2*mu)/s
    model = 2*(x/2.)**mu *b**(mu+1.) /math.gamma(mu) *kv(mu-1,b*x)
    model = np.nan_to_num(model)

    if data is None:
        return model
    if eps is None:
        return (model - data) #residual
    return (model - data)/eps



def hk(params, x, data=None, eps=None, method = 'compound', verbose=False):
    """Homodyne K-distribution from various methods:
    'analytic' = from the common analytic form (!!UNSTABLE!!)
    'compound' = from the compound representation [Destrempes and Cloutier,
                 2010, Ultrasound in Med. and Biol. 36(7): 1037 to 1051, Eq. 16]
    """
    # Initialisation
    a = params['a']
    s = params['s']
    mu = params['mu']
    if hasattr(a, 'value'): a = a.value #debug due to lmfit.minimize
    if hasattr(s, 'value'): s = s.value #idem
    if hasattr(mu, 'value'): mu = mu.value #idem
    if verbose is True: print(a, s, mu)
    x = np.array([x]).flatten(0) # debug for iteration over 0-d element
    
    def integrand(w, x, a, s, mu, method=method):
        if method == 'analytic':
            return x*w*jv(0, w*a)*jv(0, w*x)*(1. +w**2*s**2/(2.*mu))**-mu
        if method == 'compound':
            return rice({'a':a,'s':s*np.sqrt(w/mu)}, x) * gamma({'mu':mu}, w)
            
    model = [integrate.quad(integrand, 0., np.inf, args=(i, a, s, mu, method))[0] 
             for i in x] # Integration
    model = np.array(model)
    
    if data is None:
        return model
    if eps is None:
        return (model - data) #residual
    return (model - data)/eps