# -*- coding: utf-8 -*-
"""
Created on Wed May 29 17:59:48 2019
Script para procesamiento de archivos de excel para BERT.
@author: RubénBerbena
"""
import xlrd #Libreria para leer el archivo .xls
import json
import sys

argfilein= str(sys.argv[1]) #Se definen las variables para los argumentos de consola.
argfileout= str(sys.argv[2])

file = (argfilein)# Se identifica la ruta del archivo excel.
libro = xlrd.open_workbook(file, on_demand=True) #Se abre el libro de excel de la ruta especificada.
hoja = libro.sheet_by_index(0)  #Se determina la hoja a leer.


def validacionarchivo(libro):
    hojas = len(libro.sheet_names())
    if hojas < 3:
        return True
    else:
        return False
    
def validacioncolumnas(hoja):
    ncolumns = hoja.ncols
    if ncolumns > 1:
        return True    
    else:
        return False
    
def validacionestrellas(estrellas):
            try:
               float(estrellas)
               return True
            except ValueError:
                return False
            
def validacionid(id):
            try:
               float(id)
               return True
            except ValueError:
                return False
        
def limpieza(primario, opiniones):
    for item in primario[:]: #En este for se eliminan los reviews repetidos que no contengan nada en el campo Text.
        if item["review_original"] == "":
            primario.remove(item)
    pcorregido = primario        
    
    
    for op in opiniones: #En este for se adjuntan las opiniones en la lista vacia de cada opinión.
        id_review = op['id']
        for review in pcorregido:
            if review['id'] == id_review:
                del op['id']
                review['opiniones'].append(op)
                break
    return primario


def limpiezaduplicados(pcorregido):
     for item in pcorregido[:]: #En este for se eliminan los reviews repetidos que no contengan nada en el campo Text.
         if len(item["opiniones"]) == 0:
             pcorregido.remove(item)
     return pcorregido
         
         

"""MAIN"""
def iteration():
        validarhoja = validacionarchivo(libro)
        validarcol = validacioncolumnas(hoja)
        if validarhoja and validarcol == True:
            try:
                nfilas = hoja.nrows - 1
                inicio = 0 
                acumulador1= [] #Se definen las listas de salida que van a conetener los arreglos con las opiniones y los reviews.
                acumulador2= []
                while inicio < nfilas:
                    inicio += 1
                    var = hoja.row_values(inicio, start_colx = 0, end_colx= None)
                    #Aqui se leen los valores de todas las filas que contengan información.
                    #Se identifica el sentimiento y se le asigna un valor nuevo a continuación.
                    polaridad = ""
                    if var[9] == "-":
                        polaridad = "Neutral"
                        
                    elif var[9] == "N":
                        polaridad = "Negative"
                        
                    elif var[9] == "P":
                        polaridad = "Positive"
                    
                    #Se referencian las variables correspondientes a las columnas y se castean
                    id =  var[0]
                    id = validacionid(id)
                    
                    if id == True:
                        id = int(var[0])
                    else:
                        id = "-"
                        
                    review_original = var[1].strip()
                    review_corregido= var[2].strip()
                    estrellas = var[3]
                    estrellas = validacionestrellas(estrellas)
                    
                    if estrellas == True:
                        estrellas = int(var[3])
                    else:
                        estrellas = "-"
                        
                    contexto = var[4].strip()
                    establecimiento = var[5].strip()
                    aspecto = var[6].strip()
                    target_entity = var[7].strip()
                    sentimiento = var[8].strip()
                    
                    #A continuación se crea el arreglo de opiniones.
                    opiniones = {"id":id, "aspecto": aspecto,"target_entity":target_entity,"sentimiento":sentimiento,"polaridad":polaridad}
                    
                    #A continuación se crea el arreglo primario con los reviews.
                    arreglo = {"id":id, "review_original":review_original, "review_corregido":review_corregido, "estrellas":estrellas, "contexto":contexto, "establecimiento":establecimiento}
                    opiniones2= {"opiniones":[]} #Se crea una lista vacia para adjuntar el arreglo de opiniones más adelante.
                    arreglo.update(opiniones2)
                    acumulador1.append(arreglo) #Se van adjuntando los arreglos de los reviews uno por uno en la lista acumulador1.
                    acumulador2.append(opiniones) #Se van adjuntando los arreglos de las opiniones uno por uno en la lista acumulador2.
                    primario= acumulador1 #Se renombran las variables.
                    opiniones = acumulador2
                
                pcorregido = limpieza(primario, opiniones)
                
                corregidofinal = limpiezaduplicados(pcorregido)
                             
                limpio= corregidofinal
                jsonlimpio= json.dumps(limpio, indent= 4, ensure_ascii = False).encode('utf8') #Aqui se le da formato a la lista, se cambian comillas simples por comillas dobles, se identa y se determina en falso el parámetro ensure ASCII para que se acepte el encoding UTF-8.
                fileout = open(""+argfileout+"",'wb') #Se especifica el archivo de salida.
                fileout.write(jsonlimpio) #Se escribe la lista en el archivo de salida.
                #print(jsonlimpio) #Se imprime la última forma de la lista para verificarla.
                
            except Exception as error:
                print(error)
        else:
            print("El formato del archivo es incorrecto")





if __name__ == '__main__': 
	iteration()                 