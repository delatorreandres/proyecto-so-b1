from bd_config import conn
import threading as th
import time
from datetime import datetime

H_CARROS = 5
M_ENTRADA_POR_CARRO = 3
K_PUNTOS_CONTROL = 1


puntos_control = th.Semaphore(K_PUNTOS_CONTROL)
mutex = th.Semaphore(1)

def esperaPuntoControl():
	time.sleep(0.2)

def esperaEntrada ():
	time.sleep(0.05)

def entrada (nombreCarro):
	for i in range(M_ENTRADA_POR_CARRO):
		puntos_control.acquire()
		inicio = datetime.now()
		con = conn()
		cursor = con.cursor()
		mutex.acquire()
		cursor.execute("SELECT valor FROM espacio WHERE espacio.id = 1")
		autosDentro  = cursor.fetchone()[0]
		esperaEntrada() #entrando
		cursor.execute("UPDATE espacio SET valor = %s WHERE espacio.id = 1",(autosDentro+1,))
		cursor.execute("INSERT INTO entrada (carro,espacio_id,valor_leido,momento) VALUES (%s,1,%s,NOW())",(nombreCarro,autosDentro))
		mutex.release()
		esperaPuntoControl() #simulación espera punto de control (cajero)
		fin = datetime.now()
		cursor.execute("INSERT INTO atencion (carro,inicio,fin) VALUES (%s,%s,%s)",(nombreCarro,inicio,fin))
		cursor.close()
		con.close()
		puntos_control.release()


hilosCarros = []

for j in range(H_CARROS):
	h = th.Thread(target=entrada, args=(f"carro {j}",))
	hilosCarros.append(h)
	h.start()
#	time.sleep(0.3)

for c in hilosCarros:
	c.join()
