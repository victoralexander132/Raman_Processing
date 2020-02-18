"""
====================================================
Programa que corrige y compara un espectro de Raman 
desconocido contra una base de datos de referencia.
Utiliza el filtro Savitzky Golay para la
corrección por línea base.
2019
Elaboró: Víctor Alexander
Supervisó: Dr. Josué Tago Pacheco
====================================================
"""

# Importamos las funciones y librerías necesarias
from Funcion import *
from scipy.signal import savgol_filter


def mp_SG(i_registro):
    # Espectro de entrada
    x = np.copy(X)
    y = np.copy(Y)
    # Espectros de la base de datos RRUFF
    xR = np.copy(datos[i_registro][1])
    yR = np.copy(datos[i_registro][2])
    # Empatar dominio de los espectros a comparar
    xc, yc, xR, yR = fix_ind(x, y, xR, yR)
    xc, yc, xR, yR = fix_ind(xc, yc, xR, yR)
    # ============================================ Método
    # Calcular el lower envelope
    low_env = envelope(yc)
    # Calcular envolvente a la envolvente
    low_env = envelope(low_env)
    le = np.copy(low_env)
    # Aplicamos filtro SG 100 veces con ventana de
    # tamaño (2k+1) con k = 5
    for i in range(100):
        SG = savgol_filter(le, 11, 1)
        le = np.copy(SG)
    # Removemos la línea base calculada
    yc -= SG
    # =========================================== Método
    # =========================================== Filtro
    fs = 1000
    fc = 50
    order = 9
    yf = lp(yc, fc, fs, order)
    # Filtramos el espectro de la base de datos para tener una comparación en condiciones similares
    yR = lp(yR, fc, fs, order)
    # =========================================== Filtro
    # Eliminamos los valores negativos del espectro llevando el mínimo a cero
    yc = yf-np.amin(yf)
    # Aplicamos un factor de relajación
    yc = fac_re(yc, 1)
    # Normalizamos los espectros
    yc /= np.amax(yc)
    yR /= np.amax(yR)
    return mycorr(xc, yc, xR, yR)


if __name__ == "__main__":
    plt.rcParams.update(params)
    # Ventana para pedir archivo
    ventana = tk.Tk()
    # Impide que se muestre toda la GUI
    ventana.withdraw()
    # Ruta del espectro a analizar mediante selección del usuario
    ruta = filedialog.askopenfilename(initialdir="Datos/",
                                      title="Select file", filetypes=(("CSV files", "*.CSV"), ("all files", "*.*")))
    f_name = ruta.split('/')[-2:]
    f_name = f_name[0]+'_'+f_name[1]
    f_name = f_name[0:-4]
    print('=======================================')
    print('Analizando: {}'.format(f_name))
    # Iniciamos contador de tiempo para medir el tiempo de ejecución
    start = time.time()
    # Cargamos el espectro a analizar
    X, Y = np.loadtxt(ruta, unpack=True, comments='##', delimiter=',')
    # Almacenamos todos los espectros de la base de datos en una variable
    datos = datos_RRUFF('RRUFF.db')
    # Número total de espectros en la base de datos
    n_registros = len(datos)
    # Inicializamos el arreglo para guardar los coeficientes de correlación
    correlaciones = np.zeros((n_registros, 1))

    # ================================================ Multiprocesamiento
    p = mp.Pool(mp.cpu_count())
    correlaciones = p.map(mp_SG, range(n_registros))
    p.close()
    p.join()
    # ================================================ Multiprocesamiento

    # Calculando los coeficientes de correlación más altos
    imax = []
    max = []
    correlaciones = np.array(correlaciones)
    for im in range(10):
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
        xc, yc, xR, yR = fix_ind(x, y, xR, yR)
        xc, yc, xR, yR = fix_ind(xc, yc, xR, yR)
        low_env = envelope(yc)
        low_env = envelope(low_env)
        le = np.copy(low_env)
        for i in range(100):
            SG = savgol_filter(le, 11, 1)
            le = np.copy(SG)
        yc -= SG
        #order = 4
        #cutoff = 0.05
        # fs = 1/(x[1]-x[0])       # sample rate, Hz
        #yf = lowpass(y, cutoff, fs, order)
        fs = 1000
        fc = 50
        order = 9
        yf = lp(yc, fc, fs, order)
        yR = lp(yR, fc, fs, order)
        yc = yf-np.amin(yf)
        yc = fac_re(yc, 1)
        yc /= np.amax(yc)
        yR /= np.amax(yR)
        plt.subplot(2, 2, n + 2)
        plt.plot(xc, yc, label='Espectro corregido')
        plt.plot(xR, yR, '.', label='Muestra: ' + nombre, markersize=1)
        plt.xlabel('Corrimiento Raman [cm⁻¹]')
        plt.title('Coeficiente de correlación: \n'+"%.4f" % max[n])
        plt.legend()
    plt.savefig('Images/SG/'+f_name+'.pdf')
    end = time.time()
    print('Procesamiento terminado')
    print("Tiempo transcurrido: %3.3f" % (end - start)+" segundos")
    print('=======================================')
    print('Resultados\n')
    for k in range(10):
        k +=1
        registro = imax[k-1]
        nombre = datos[registro][0]
        print('%2d'%k +'. '+nombre+' - %.4f' % max[k-1])
    plt.show()
