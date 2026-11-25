from bd_config import conn
import threading as th
import time

H_CARROS = 5
M_ENTRADA_POR_CARRO = 10

mutex = th.Semaphore(1)

def esperaEntrada ():
	time.sleep(0.05)

def entrada (nombreCarro):
	for i in range(M_ENTRADA_POR_CARRO):
		con = conn()
		cursor = con.cursor()
		mutex.acquire()
		cursor.execute("SELECT valor FROM espacio WHERE espacio.id = 1")
		autosDentro  = cursor.fetchone()[0]
		esperaEntrada() #entrando
		cursor.execute("UPDATE espacio SET valor = %s WHERE espacio.id = 1",(autosDentro+1,))
		cursor.execute("INSERT INTO entrada (carro,espacio_id,valor_leido,momento) VALUES (%s,1,%s,NOW())",(nombreCarro,autosDentro))
		mutex.release()
		cursor.close()
		con.close()


hilosCarros = []

for j in range(H_CARROS):
	h = th.Thread(target=entrada, args=(f"carro {j}",))
	hilosCarros.append(h)
	h.start()
	time.sleep(0.3)

for c in hilosCarros:
	c.join()
