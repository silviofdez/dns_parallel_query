#!/usr/bin/env python
import dns.resolver #dnspython
import threading
import time # para ver rendimiento
import logging
import os

#numero maximo de hilos simultaneos
max_threads = 50

class DNSQuery:
	"""Almacena informacion sobre una DNS query"""
	name = ""
	rdtype = ""
	answer = ""

def worker(server, rtype):
	"""Realiza un query dns y almacena los resultados en una variable del tipo DNSQuery
	@param line: peticion dns con el siguiente formato 'dns.msftncsi.com.	MX' termina en fin de linea
	"""
	myResolver = dns.resolver.Resolver() 
	myResolver.nameservers = ['8.8.8.8','8.8.4.4'] #dns de google
	myResolver.Timeout = 5.0
	myResolver.lifetime = 5.0
	query = DNSQuery()	
	query.name = server
	query.rdtype = rtype
	#formato de linea: query (tab) type (eol)
	try:
		result = myResolver.query(server, rtype) #myResolver.query(servidor, tipo de peticion)
		
		#almacenamos datos
		for rdata in result: #para cada respuesta
			query.answer = rdata.to_text()

	except dns.resolver.NXDOMAIN:
		query.answer = "No such domain %s" % server
	except dns.resolver.Timeout:
		query.answer = "Timed out while resolving %s" % server
	except dns.resolver.NoAnswer:
		query.answer = "the response did not contain an answer resolving %s" % server
	except dns.resolver.NoNameservers:
		query.answer = "no non-broken nameservers are available to answer the question for %s" % server
	except dns.exception.DNSException as exc:
		print exc
		print format(exc)
		query.answer = "Unhandled exception" #por si hay algun problema (no response, etc)
	queriesResult.append(query)

t0 = time.time()

queriesResult = []

f = open(os.path.dirname(os.path.abspath(__file__))+"/query.txt")

for line in f:
	server = line.split()[0]
	rtype = line.split()[1]
	if(threading.activeCount() >= max_threads): #limitamos hilos en ejecucion
		time.sleep(1)
	d = threading.Thread(target=worker, args=(server, rtype))
	d.setDaemon(True)
	d.start()
	
# hilo principal
mt = threading.currentThread()

#esperamos los hilos que quedan por terminar
for th in threading.enumerate():
    # si es el hilo principal saltar o entraremos en deadlock
    if th is mt:
        continue
    th.join()
#volcamos resultados a un fichero
g=open(os.path.dirname(os.path.abspath(__file__))+"/query_results.txt","w")

index = 1
for query in queriesResult:
	g.write(str(query.name)+"		"+str(query.rdtype)+"	"+str(query.answer)+"\n")
	print str(index)+" - "+str(query.name)+"		"+str(query.rdtype)+"	"+str(query.answer)
	index=index+1

g.close()

print os.path.dirname(os.path.abspath(__file__))

print "Tiempo de ejecucion: ",time.time()-t0


