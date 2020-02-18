"""
================================================================
 Módulo que contiene las funciones necesarias para el
 procesamiento y análisis espectral de los registros en 
 una base de datos.
===============================================================
 Elaboró: Víctor Manuel Soto Alexander
 Asesor: Dr. Josué Tago Pacheco

"""

# Importamos las librerías necesarias
import io
import sqlite3
from scipy import interpolate
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt, freqz
from scipy.sparse import csc_matrix, diags, eye
from scipy.sparse.linalg import spsolve
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg',warn=False, force=True)
import numpy as np
import time
import tkinter as tk
from tkinter import filedialog
import multiprocessing as mp
from pathlib import Path

home = str(Path.home())
params = {
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'font.size': 8,
    'figure.autolayout': True,
    'figure.figsize': [7.2, 4.45],
    'axes.titlesize': 9,
    'axes.labelsize': 9,
    'lines.linewidth': 1,
    'lines.markersize': 1,
    'legend.fontsize': 9,
    'figure.figsize': [7.48, 7.48*(np.sqrt(5)-1.0)/2.0],
    'axes.grid.which': 'minor',
    'figure.dpi': 300.0,
    'figure.autolayout': True,
    'savefig.bbox': 'tight'
}


def adapt_array(arr):
    # Agregar arreglos de numpy a la base de datos
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    # Agregar arreglos de numpy a la base de datos
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("array", convert_array)


def datos_RRUFF(ruta):
    """
    Función que lee una base de datos y almacena la
    información en un arreglo de numpy.

    Parametros
    ----------
    ruta : str
        ruta de la base de datos

    Returns
    -------
    data : ndarray
        Arreglo que contiene los registros de la base de datos [nombre, x, y].
    """
    # Conectar con base de datos
    conn = sqlite3.connect(ruta, detect_types=sqlite3.PARSE_DECLTYPES)
    # Crear cursor para ejecutar comandos en la base de datos
    c = conn.cursor()
    # Seleccionar toda la base de datos
    c.execute("SELECT * FROM RRUFF")
    # Asignar los datos a la variable data
    data = c.fetchall()
    # Cerramos la conexión de la base de datos
    conn.close()
    return data


def lp(y, fc, fs, order):
    """
    Función que aplica un filtro pasa bajo
    a una serie de datos
    """
    w = fc / (fs / 2)
    b, a = butter(order, w, 'low', analog=False)
    yf = filtfilt(b, a, y)
    return yf


def fix_ind(x, y, xR, yR):
    """
    Funcion que arregla los indices de dos archivos 
    para empatar los dominios; que terminen y
    empiecen en el mismo valor.

    Entrada:
    x:  Dominio del espectro a analizar
    xR: Dominio del espectro de la base de datos
    y:  Rango del espectro a analizar
    yR: Rango del espectro de la base de datos

    Salida:
    x:  Dominio corregido del espectro a analizar
    xR: Dominio corregido del espectro de la base de datos
    y:  Rango corregido del espectro a analizar
    yR: Rango corregido del espectro de la base de datos
    """
    # Determinar donde inician los espectros
    xmin = np.amin(x)
    xRmin = np.amin(xR)
    # Determinar donde acaban los espectros
    xmax = np.amax(x)
    xRmax = np.amax(xR)
    ii = 0
    # Si RRUFF inicia primero
    if xRmin < xmin:
        # Empatar limite inferior
        while True and ii < len(xR):
            if xR[ii] < xmin:
                ii += 1
            else:
                break
        # Indice de limite inferior
        ind_ini = ii + 1
        # Empatar limite superior
        while True and ii < len(xR):
            if xR[ii] < xmax:
                ii += 1
            else:
                break
        # Indice del limite superior
        ind_fin = ii - 1
        # Redefinir dominio para que sea el mismo
        xR = xR[ind_ini:ind_fin]
        yR = yR[ind_ini:ind_fin]
    # Si recolectado inicia primero
    else:
        # Empatar limite inferior
        while True and ii < len(x):
            if x[ii] < xRmin:
                ii += 1
            else:
                break
        # Indice del limite inferior
        ind_ini = ii - 1
        # Empatar limite superior
        while True and ii < len(x):
            if x[ii] < xRmax:
                ii += 1
            else:
                break
        # Indice del limite superior
        ind_fin = ii + 1
        # Redefinir dominio para que sea el mismo
        x = x[ind_ini:ind_fin]
        y = y[ind_ini:ind_fin]
    # Corregir el dominio de RRUFF
    # Si es mas grande que el recolectado
    while True:
        if xR[-1] > xmax:
            xR = np.delete(xR, -1)
            yR = np.delete(yR, -1)
        else:
            break
    return x, y, xR, yR


def polynomial(data, order):

    x = np.arange(len(data))
    fit = np.polyval(np.polyfit(x, data, deg=order), x)

    yp = data - fit
    return yp


def envelope(y):
    """
    Función que calcula el lower envelope de un vector.

    Input
        y : ndarray
        Espectro al que se le calculará un low envelope

    Returns
        q_l : ndarray
        Envelope calculado
    """
    # Inicializar arreglo del modelo de los mínimos locales
    q_l = np.zeros(y.shape)

    # Inicializar arreglos para los mínimos locales
    l_x = [0, ]
    l_y = [y[0], ]

    # Detectar mínimos locales y marcar su ubicación en l_x y l_y.
    for k in range(1, len(y)-1):
        if (np.sign(y[k]-y[k-1]) == -1) and ((np.sign(y[k]-y[k+1])) == -1):
            l_x.append(k)
            l_y.append(y[k])

    # Añade el último valor de (y) a los valores a interpolar.
    l_x.append(len(y)-1)
    l_y.append(y[-1])

    # Ajustar modelo a los datos. Usando quadratic splines.
    l_p = interp1d(l_x, l_y, kind='quadratic',
                   bounds_error=False, fill_value=0.0)
    # Evaluar el modelo en el dominio de (y).
    for k in range(0, len(y)):
        q_l[k] = l_p(k)
    return q_l


def PLS(x, w, lambda_, differences=1):
    X = np.matrix(x)
    m = X.size
    E = eye(m, format='csc')
    # numpy.diff() no funciona con matrices sparse.
    # Esto es una solución
    D = E[1:]-E[:-1]
    W = diags(w, 0, shape=(m, m))
    A = csc_matrix(W+(lambda_*D.T*D))
    B = csc_matrix(W*X.T)
    background = spsolve(A, B)
    return np.array(background)


def my_airPLS(x, lambda_=10, porder=5, itermax=5):
    m = x.shape[0]
    w = np.ones(m)
    for i in range(1, itermax+1):
        z = PLS(x, w, lambda_, porder)
        d = x-z
        dssn = np.abs(d[d < 0].sum())
        if(dssn < 0.001*(abs(x)).sum() or i == itermax):
            if(i == itermax):
                #print('Warning: Límite de iteraciones alcanzado!')
                break
        # d > 0 significa que este punto is parte de un pico
        # entonces se fija el peso a 0 para ignorarlo
        w[d >= 0] = 0
        w[d < 0] = np.exp(i*np.abs(d[d < 0])/dssn)
        w[0] = np.exp(i*(d[d < 0]).max()/dssn)
        w[-1] = w[0]
    return z


def fac_re(Y, n):
    """
    Función que aplica un factor de relajamiento 
    a una serie de datos

    Returns
    -------
    Y : ndarray
    """
    for i in range(n):
        media = np.mean(Y)
        for index in range(len(Y)):
            dy = media - Y[index]
            fac = dy/media
            Y[index] *= (1-fac)
    return Y


def mycorr(x, y, xR, yR):
    """
    Función que calcula la correlación entre dos series de datos.

    Returns
    ------
    corr : float
    Coeficiente de correlación

    """
    # Generamos una interpolación para tener la misma tasa de muestreo en los datos a comparar
    f = interpolate.interp1d(x, y)
    y = f(xR)
    # Realizamos la correlación
    corr = pearsonr(y, yR)[0]
    return corr


