from bd_config import conn
import threading as th
import time
from datetime import datetime

H_CARROS = 5
M_ENTRADA_POR_CARRO = 5
K_PUNTOS_CONTROL = 2
B_COLA = 2
N_MAX_INGRESOS = 25
C_TRABAJADORES = 2

puntosControl = th.Semaphore(0)
mutexEspacio = th.Semaphore(1)
mutexCola = th.Semaphore(1)
mutexIngresos = th.Semaphore(1)
vacios = th.Semaphore(B_COLA)
llenos = th.Semaphore(0)
fin = th.Event()

colaPTrabajador = []
ingresosActuales = 0

def esperaTrabajador ():
	time.sleep(1)

def esperaPuntoControl():
	time.sleep(0.2)

def esperaEntrada ():
	time.sleep(0.05)

def trabajador (nombreTrabajador):
	global colaPTrabajador, fin
	while(True):
		llenos.acquire()
		mutexCola.acquire()
		if(fin.is_set() and not colaPTrabajador):
			mutexCola.release()
			vacios.release()
			llenos.release()
			break
		puntoAtendido = colaPTrabajador.pop(0)
		enCola = len(colaPTrabajador)
		mutexCola.release()
		vacios.release()
		esperaTrabajador()  #simulación espera trabajador
		con = conn()
		cursor = con.cursor()
		cursor.execute("INSERT INTO ingreso (punto_control,trabajador,en_cola, guardado) VALUES (%s,%s,%s,NOW())",
				(puntoAtendido,nombreTrabajador,enCola))
		cursor.close()
		con.close()

def puntoControl (nombrePunto):
	global ingresosActuales, colaPTrabajador, fin
	while(True):
		vacios.acquire()
		mutexIngresos.acquire()
		ingresosActuales+=1
		if(ingresosActuales > N_MAX_INGRESOS):
			mutexIngresos.release()
			fin.set()
			llenos.release()
			break
		mutexIngresos.release()
		puntosControl.release()
		mutexCola.acquire()
		colaPTrabajador.append(nombrePunto)
		mutexCola.release()
		llenos.release()

def entrada (nombreCarro):
	for i in range(M_ENTRADA_POR_CARRO):
		puntosControl.acquire()
		inicio = datetime.now()
		con = conn()
		cursor = con.cursor()
		mutexEspacio.acquire()
		cursor.execute("SELECT valor FROM espacio WHERE espacio.id = 1")
		autosDentro  = cursor.fetchone()[0]
		esperaEntrada() #entrando
		cursor.execute("UPDATE espacio SET valor = %s WHERE espacio.id = 1",(autosDentro+1,))
		cursor.execute("INSERT INTO entrada (carro,espacio_id,valor_leido,momento) VALUES (%s,1,%s,NOW())",(nombreCarro,autosDentro))
		mutexEspacio.release()
#		esperaPuntoControl() #simulación espera punto de control (cajero)
		fin = datetime.now()
		cursor.execute("INSERT INTO atencion (carro,inicio,fin) VALUES (%s,%s,%s)",(nombreCarro,inicio,fin))
		cursor.close()
		con.close()


hilosCarros = []
hilosPControl = []
hilosTrabajador = []

for j in range(H_CARROS):
	h = th.Thread(target=entrada, args=(f"carro {j}",))
	hilosCarros.append(h)
	h.start()
#	time.sleep(0.3)

for k in range(K_PUNTOS_CONTROL):
	k+=1
	h1 = th.Thread(target=puntoControl, args=(f"punto de control {k}",))
	hilosPControl.append(h1)
	h1.start()

for l in range(C_TRABAJADORES):
	l+=1
	h2 = th.Thread(target=trabajador, args=(f"trabajador {l}",))
	hilosTrabajador.append(h2)
	h2.start()


for c in hilosCarros:
	c.join()
for p in hilosPControl:
	p.join()
for t in hilosTrabajador:
	t.join()
