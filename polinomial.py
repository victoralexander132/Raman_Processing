# ====================================================
# Programa que corrige y compara un espectro de Raman 
# desconocido contra una base de datos de referencia.
# Utiliza un método de ajuste polinomial para la
# corrección por línea base.
# 2019
# Elaboró: Víctor Alexander
# Supervisó: Dr. Josué Tago Pacheco
# ====================================================

# Importamos las librerìas necesarias
from pathlib import Path
home = str(Path.home())
import Funcion as fun
import numpy as np
import matplotlib.pyplot as plt
from obspy.signal.detrend import polynomial
import time
import multiprocessing as mp


def polinomial(i_registro):
    # Espectro de entrada
    x = np.copy(X)
    y = np.copy(Y)
    # Espectros de la base de datos RRUFF
    xR = datos[i_registro][1]
    yR = datos[i_registro][2]
    # Empatar dominio de los espectros a comparar
    xc, yc, xR, yR = fun.fix_ind(x, y, xR, yR)
    xc, yc, xR, yR = fun.fix_ind(xc, yc, xR, yR)
    # ============================================ Método
    # Eliminamos la tendencia del espectro de entrada
    polynomial(yc, order=j + 1, plot=False)
    # ============================================ Método
    # =========================================== Filtro
    # order = 4
    # cutoff = 0.05
    # fs = 1 / (x[1] - x[0])
    # yf = fun.lowpass(yc, cutoff, fs, order)
    # Filtramos el espectro
    fc = 30
    fs = 1000
    order = 5
    yf = fun.lp(yc, fc, fs, order)
    # Filtramos el espectro de la base de datos para tener una comparación en condiciones similares
    yR = fun.lowpass(yR, fc, fs, order)
    # =========================================== Filtro
    # Eliminamos los valores negativos del espectro llevando el mínimo a cero
    yc = yf - np.amin(yf)
    # Aplicamos un factor de relajación
    yc = fun.fac_re(yc, 1)
    # Normalizamos los espectros
    yc /= np.amax(yc)
    yR /= np.amax(yR)
    return fun.mycorr(xc, yc, xR, yR)


if __name__ == "__main__":
    # Iniciamos contador de tiempo para medir el tiempo de ejecución
    start = time.time()
    # Ruta del espectro a analizar
    ruta = home + '/MEGA/UNAM/Tesis/Datos/Giovanni_Leon/Analisis/Nueva carpeta 2/med 1.CSV'
    # Cargamos el espectro a analizar
    X, Y = np.loadtxt(ruta, comments='##', delimiter=',', unpack=True)
    # Almacenamos todos los espectros de la base de datos en una variable
    datos = fun.datos_RRUFF(home + '/MEGA/UNAM/Tesis/Base_Datos/RRUFF_532.db')
    # Número total de espectros en la base de datos
    n_registros = len(datos)
    # Grado inicial para el ajuste polinomial
    grado_ini = 1
    # Grado final para el ajuste polinomial
    grado_fin = 10
    # Inicializamos el arreglo para guardar los coeficientes de correlación
    correlaciones = np.zeros((n_registros, grado_fin))

    # ================================================ Multiprocesamiento
    p = []
    for j in range(grado_fin):
        p.append(mp.Pool(mp.cpu_count()))
        correlaciones[:, j] = p[j].map(polinomial, range(n_registros))
        p[j].close
        p[j].join
        print(f"Grado: {j+1}")
    # ================================================ Multiprocesamiento

    #Calculando los coeficientes de correlación más altos
    imax = []
    grad = []
    max = []
    for maximo in range(3):
        max.append(np.amax(correlaciones))
        imax.append(np.unravel_index(
            correlaciones.argmax(), correlaciones.shape)[0])
        grad.append(np.unravel_index(
            correlaciones.argmax(), correlaciones.shape)[1])
        correlaciones[imax[maximo], grad[maximo]] = 0

    # Repetimos el procesamiento, pero esta vez, solamente para los
    # tres espectros con un mayor coeficiente de correlación.
    fig = plt.figure()
    plt.subplot(2, 2, 1)
    plt.plot(X, Y, 'k-', label='Espectro de entrada')
    plt.xlabel('Corrimiento Raman [cm⁻¹]')
    plt.ylabel('Intensidad [U.A.]')
    plt.legend()
    for n in range(3):
        grado_ini = grad[n]
        registro = imax[n]
        corr = max[n]
        nombre = datos[registro][0]
        x = np.copy(X)
        y = np.copy(Y)
        xR = datos[registro][1]
        yR = datos[registro][2]
        xc, yc, xR, yR = fun.fix_ind(x, y, xR, yR)
        xc, yc, xR, yR = fun.fix_ind(xc, yc, xR, yR)
        polynomial(yc, order=grado_ini, plot=False)
        # order = 4
        # cutoff = 0.05
        # fs = 1 / (x[1] - x[0])
        # yf = fun.lowpass(yc, cutoff, fs, order)
        fc = 30
        fs = 1000
        order = 5
        yf = fun.lp(yc, fc, fs, order)
        yR = fun.lowpass(yR, fc, fs, order)
        yc = yf - np.amin(yf)
        yc = fun.fac_re(yc, 1)
        yc /= np.amax(yc)
        yR /= np.amax(yR)
        plt.subplot(2, 2, n + 2)
        plt.plot(xc, yc, label='Espectro corregido')
        plt.plot(xR, yR, '.', label='Muestra: ' + nombre, markersize=2)
        plt.legend()
        plt.xlabel('Corrimiento Raman [cm⁻¹]')
        plt.title("Grado del polinomio: %1d" % grado_ini +
                  "\nCoeficiente de correlación: %.4f" % corr)
    fig = plt.gcf()
    fig.set_size_inches(10, 6)
    plt.tight_layout()

    end = time.time()
    print("Tiempo transcurrido: %3.3f" % (end - start) + " segundos")
    plt.show()
