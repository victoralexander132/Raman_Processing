# ====================================================
# Programa que corrige y compara un espectro de Raman 
# desconocido contra una base de datos de referencia.
# Utiliza la función airPLS para la
# corrección por línea base.
# 2019
# Elaboró: Víctor Alexander
# Supervisó: Dr. Josué Tago Pacheco
# ====================================================

# Importamos las librerìas necesarias
from pathlib import Path
home = str(Path.home())
import sys
sys.path.append(home+'/MEGA/UNAM/Tesis/Funciones')
import Funcion as fun
import numpy as np
import matplotlib.pyplot as plt
import time
import multiprocessing as mp


def mp_airPLS(i_registro):
    # Espectro de entrada
    x = np.copy(X)
    y = np.copy(Y)
    # Espectros de la base de datos RRUFF
    xR = np.copy(datos[i_registro][1])
    yR = np.copy(datos[i_registro][2])
    # Empatar dominio de los espectros a comparar
    xc, yc, xR, yR = fun.fix_ind(x, y, xR, yR)
    xc, yc, xR, yR = fun.fix_ind(xc, yc, xR, yR)
    #============================================ Método
    z = fun.my_airPLS(yc, lambda_=10, porder=6, itermax=5)
    yc = yc-z
    # ============================================ Método
    # =========================================== Filtro
    #order = 4
    #cutoff = 0.05
    #fs = 1/(x[1]-x[0])       # sample rate, Hz
    #yf = fun.lowpass(y, cutoff, fs, order)
    # Filtramos el espectro
    fc = 30
    fs = 1000
    order = 5
    yf = fun.lp(yc, fc, fs, order)
    # Filtramos el espectro de la base de datos para tener una comparación en condiciones similares
    yR = fun.lp(yR, fc, fs, order)
    #=========================================== Filtro
    # Eliminamos los valores negativos del espectro llevando el mínimo a cero
    yc = yf-np.amin(yf)
    # Aplicamos un factor de relajación
    yc = fun.fac_re(yc, 1)
    # Normalizamos los espectros
    yc /= np.amax(yc)
    yR /= np.amax(yR)
    return np.array(fun.mycorr(xc, yc, xR, yR))


if __name__ == "__main__":
    # Iniciamos contador de tiempo para medir el tiempo de ejecución
    start = time.time()
    # Ruta del espectro a analizar
    ruta = home+'/MEGA/UNAM/Tesis/Datos/INAH/TingL8 (oligoclasa).CSV'
    # Cargamos el espectro a analizar
    X, Y = np.loadtxt(ruta, unpack=True, comments='##', delimiter=',')
    # Almacenamos todos los espectros de la base de datos en una variable
    datos = fun.datos_RRUFF(home+'/MEGA/UNAM/Tesis/Base_Datos/RRUFF_532.db')
    # Número total de espectros en la base de datos
    n_registros = len(datos)
    # Inicializamos el arreglo para guardar los coeficientes de correlación
    correlaciones = np.zeros((len(datos), 1))

    # ================================================ Multiprocesamiento
    p = mp.Pool(mp.cpu_count())
    correlaciones = p.map(mp_airPLS, range(n_registros))
    p.close()
    p.join()
    # ================================================ Multiprocesamiento

    # Calculando los coeficientes de correlación más altos
    imax = []
    max = []
    correlaciones = np.array(correlaciones)
    for im in range(3):
        max.append(np.amax(correlaciones))
        imax.append(correlaciones.argmax())
        correlaciones[imax[im]] = 0

    # Repetimos el procesamiento, pero esta vez, solamente para los
    # tres espectros con un mayor coeficiente de correlación.
    plt.subplot(2, 2, 1)
    plt.plot(X, Y, 'k', label='Espectro de entrada')
    plt.ylabel('Intensidad [U.A.]')
    plt.xlabel('Corrimiento Raman [cm⁻¹]')
    plt.legend()

    for n in range(3):
        registro = imax[n]
        corr = max[n]
        nombre = datos[registro][0]
        x = np.copy(X)
        y = np.copy(Y)
        xR = datos[registro][1]
        yR = datos[registro][2]
        xc, yc, xR, yR = fun.fix_ind(x, y, xR, yR)
        xc, yc, xR, yR = fun.fix_ind(xc, yc, xR, yR)
        z = fun.my_airPLS(yc, lambda_=10, porder=6, itermax=5)
        yc = yc - z
        #order = 4
        #cutoff = 0.05
        #fs = 1/(x[1]-x[0])       # sample rate, Hz
        #yf = fun.lowpass(y, cutoff, fs, order)
        fc = 30
        fs = 1000
        order = 5
        yf = fun.lp(yc, fc, fs, order)
        yR = fun.lp(yR, fc, fs, order)
        yc = yf-np.amin(yf)
        yc = fun.fac_re(yc, 1)
        yc /= np.amax(yc)
        yR /= np.amax(yR)
        plt.subplot(2, 2, n + 2)
        plt.plot(xc, yc, label='Espectro corregido')
        plt.plot(xR, yR, '.', label='Muestra: ' + nombre, markersize=2)
        plt.xlabel('Corrimiento Raman [cm⁻¹]')
        plt.title('Coeficiente de correlación: \n'+"%.4f" % max[n])
        plt.legend()
    fig = plt.gcf()
    fig.set_size_inches(10, 6)
    plt.tight_layout()

    end = time.time()
    print("Tiempo transcurrido: %3.3f" % (end - start)+" segundos")
    plt.show()
