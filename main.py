import grammar

def main():
    print('Inserte archivo')
    direccion = input()
    stream = open(direccion)
    terminales = []
    no_terminales = []
    producciones = []  # [(string,[string])]
    tokens = []
    diccionario = {}
    grupos = {}

    next = 1

    produce = stream.readline()
    tokens.append(produce)
    produce = produce.split(' ')
    distinguido = produce[0]

    while True:
        produce.remove("-->")
        cabecera = produce[0]
        grupos[cabecera] = []
        no_terminales.append(produce[0])

        nueva_parte_derecha = []


        for x in produce[1:len(produce)]:
            if x!=' ' and len(x)>0:
                if x!='|':
                    if x[len(x)-1]=='\n':
                        x = x[0:len(x)-1]
                    if not(terminales.__contains__(x)):
                        terminales.append(x)
                    nueva_parte_derecha.append(x)
                else:
                    nueva_produccion = (cabecera,nueva_parte_derecha.copy())
                    diccionario[next] = nueva_produccion
                    grupos[cabecera].append(next)
                    next+=1
                    producciones.append(nueva_produccion)
                    nueva_parte_derecha.clear()
        
        nueva_produccion = (cabecera,nueva_parte_derecha.copy())
        diccionario[next] = nueva_produccion
        grupos[cabecera].append(next)
        next+=1
        producciones.append(nueva_produccion)

        produce = stream.readline()
        if len(produce) < 3:
            break
        tokens.append(produce)
        produce = produce.split(' ')
        
    if terminales.__contains__('\n'):
        terminales.remove('\n')
    for x in no_terminales:
        if terminales.__contains__(x):
            terminales.remove(x)
    stream.close()


    ordenar(terminales)
    G = grammar.Grammar(diccionario,grupos,terminales,no_terminales,producciones,distinguido)
    G.generar_reporte()

def ordenar(lista):
    for i in range(0,len(lista)):
        menor = lista[i]
        pos = i
        for j in range(i+1,len(lista)):
            if lista[j]<menor:
                menor = lista[j]
                pos = j
        lista[pos] = lista[i]
        lista[i] = menor

'''
    G.clasificar_LR()
    cadena = input().split()
    while cadena!='ya':
        parsear = G.producir_palabra()
        print("Parsear la cadena: ",parsear)
        if len(parsear)!=0:
            pprod = G.parsear_LR(parsear)
            print("Aplicar producciones: ",pprod)
        cadena = input().split()
'''

main()
