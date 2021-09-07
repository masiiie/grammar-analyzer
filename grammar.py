
class Grammar:
    def __init__(self,diccionario,grupos, terminales = [], noterminales = [], producciones = [], distinguido = 'S'):
        self.terminales = terminales
        self.noterminales = noterminales
        self.producciones = producciones
        self.distinguido = distinguido
        self.epsilon = 'epsilon'

        self.FIRST = {}
        self.FOLLOW = {} 
        self.FP = {}  
        self.FFirst = {}

        self.LL = {}
        self.conflicto_LL = []
        
        self.tabla_LR = [] #lista de diccionarios (string contra tupla)
        self.conflicto_LR = {}

        self.dictionary = diccionario
        self.grupos = grupos  # grupos[no_terminal] = [] con los # de las prod

        self.flecha = '<span class=flecha>-></span>'

        self.ordenar(terminales)
        self.first() 
        self.follow() 
        self.ffirst()
        self.LL_metodo()


    def lista_to_string(self,lista,espacio = False):
        a = ''
        for x in lista:
            if espacio:
                a+= ' '
            a+= x
        return a   

    def imprimir_prod(self,produccion):
        return produccion[0] + self.flecha + self.lista_to_string(produccion[1])
        
    def generar_reporte(self):
        reporte = open('reporte.html','w')
        reporte.write('<head><link href="estilo.css" rel="stylesheet" type="text/css"></head>')
        reporte.write('<div><h2>Gramatica</h2><ul>')
        for x in self.noterminales:
            no = self.grupos[x][0]
            prod = x + self.flecha + self.lista_to_string(self.dictionary[no][1]) 
            for i in range(1,len(self.grupos[x])):
                no = self.grupos[x][i]
                prod += ' | ' + self.lista_to_string(self.dictionary[no][1])
            reporte.write('<li>'+prod+'</li>')
        reporte.write('</ul></div>')


        reporte.write('<div><h2>Conjuntos first y follow</h2><table><tr><th>No terminal</th><th>First</th><th>Follow</th></tr>')
        for x in self.noterminales:
            reporte.write('<tr><td>'+x+'</td>')
            reporte.write('<td>'+ self.lista_to_string(self.FIRST[x], espacio = True)+'</td>')
            reporte.write('<td>'+ self.lista_to_string(self.FOLLOW[x], espacio = True)+'</td></tr>')
        reporte.write('</table></div>')

        self.generar_reporte_analisis_LL(reporte)
        self.generar_reporte_analisis_LR(reporte)       
        

    #items: (no_produccion,cantidad de elementos antes de la coma,elemento(en caso de LR))            
    def generar_reporte_analisis_LL(self,reporte):
        reporte.write('<div><h2>Analisis LL(1)</h2><table><tr><th>Produccion</th><th>First parte derecha</th><th>FFirst</th></tr>')
        for x in self.producciones:
            reporte.write('<tr><td>'+self.imprimir_prod(x)+'</td>')
            reporte.write('<td>'+self.lista_to_string(self.FP[self.no_produccion(x)], espacio = True)+'</td>')
            reporte.write('<td>'+self.lista_to_string(self.FFirst[self.no_produccion(x)], espacio = True)+'</td>')
        reporte.write('</table>')

        if len(self.conflicto_LL)>0:
            reporte.write('<h4>Conclusion: La gramatica no es LL(1):</h4><ul>')
            for x in self.conflicto_LL:
                par = '<ul><li>'+self.imprimir_prod(self.dictionary[x[0]])+'</li><li>'+self.imprimir_prod(self.dictionary[x[1]])+'</li></ul>'
                reporte.write('<li><h4>Conflicto</h4>' + par  + '</li>')
            reporte.write('</ul>')
        else:
            reporte.write('<h4>Conclusion: La gramatica es LL(1)</h4>')
            reporte.write('<table><tr><th></th>')

            a = self.terminales.copy()
            a.remove(self.epsilon)
            a.append('$')

            for x in a:
                reporte.write('<th>' + x + '</th>')
            reporte.write('</tr>')
            for x in self.noterminales:
                reporte.write('<tr><td>' + x + '</td>')
                for y in a:
                    if self.LL[x][y]==None:
                        reporte.write('<td></td>')
                    else:
                        reporte.write('<td>'+self.imprimir_prod(self.dictionary[self.LL[x][y]])+'</td>')                
                reporte.write('</tr>')
            reporte.write('</table>')   
        reporte.write('</div>')
    #fin

    def generar_reporte_analisis_LR(self,reporte):
        self.aumentar_gramatica()
        reporte.write('<div><h2>Gramatica aumentada</h2><ul>')
        conjunto = ["S'"] + self.noterminales
        for x in conjunto:
            no = self.grupos[x][0]
            prod = x + self.flecha + self.lista_to_string(self.dictionary[no][1]) 
            prod += '<sup>('+str(no)+')</sup>'
            for i in range(1,len(self.grupos[x])):
                no = self.grupos[x][i]
                prod += ' | ' + self.lista_to_string(self.dictionary[no][1])
                prod += '<sup>('+str(no)+')</sup>'

            reporte.write('<li>'+prod+'</li>')
        reporte.write('</ul></div>')
        self.reporte_analisis_LR(reporte,False)
        self.reporte_analisis_LR(reporte,True)

    #fin  

    def aumentar_gramatica(self):
        self.dictionary[0] = ("S'",[self.distinguido])
        self.grupos["S'"] = [0]
        self.FIRST["S'"] = self.FIRST[self.distinguido].copy()
        self.FOLLOW["S'"] = {'$'}

    
    #fin

    #la gramatica tiene que estar aumentada
    def reporte_analisis_LR(self,reporte,LR):
        if LR:
            reporte.write('<div><h2>Analisis LR(1)</h2>')
        else:
            reporte.write('<div><h2>Analisis SLR(1)</h2>')

        estados, transiciones = self.group_LR(LR)
        reporte.write('<h3>Estados</h3>')
        reporte.write('<table><tr><th>Estado</th><th>Items</th><th>Transiciones</th><th>Conflicto</th></tr>')
        for i in range(0,len(estados)):
            columnas = '<td>I<sub>'+ str(i) +'</sub></td><td><ul>'
            
            for x in estados[i]:
                columnas += '<li>'+ self.imprimir_item(x,LR) +'</li>'
            columnas += '</ul></td><td><ul>'
            columnas += self.imprimir_transiciones(i,transiciones)
            columnas += '</ul></td><td><ul>'
            if self.conflicto_LR.__contains__(i):
                conflicto = '<li>'+self.conflicto_LR[i][0]+'</li>'
                conflicto += '<li>'+self.imprimir_item(self.conflicto_LR[i][1],LR)+'</li>'
                conflicto += '<li>'+self.imprimir_item(self.conflicto_LR[i][2],LR)+'</li>'
                columnas += conflicto + '</ul></td>'

            reporte.write('<tr>'+ columnas +'</tr>')
        reporte.write('</table>')


        if len(self.conflicto_LR)>0:
            if LR:
                reporte.write('<h4>Conclusion: La gramatica no es LR(1)</h4></div>')
            else:
                reporte.write('<h4>Conclusion: La gramatica no es SLR(1)</h4></div>')
        else:
            if LR:
                reporte.write('<h4>Conclusion: La gramatica es LR(1)</h4></div>')
                reporte.write('<div><h3>Tabla LR(1)</h3><table><tr>')
            else:
                reporte.write('<h4>Conclusion: La gramatica es SLR(1)</h4></div>')
                reporte.write('<div><h3>Tabla SLR(1)</h3><table><tr>')
            
            a = self.terminales + ['$']
            a.remove(self.epsilon)
            reporte.write('<th></th>')
            for x in a:
                reporte.write('<th>'+ x +'</th>')
            reporte.write('<th class=separador></th>')
            for x in self.noterminales:
                reporte.write('<th>'+ x +'</th>')
            reporte.write('</tr>')

            for i in range(0,len(estados)):
                reporte.write('<tr>')
                reporte.write('<td>I<sub>'+str(i)+'</sub></td>')
                for x in a:
                    if self.tabla_LR[i].__contains__(x):
                        reporte.write('<td>'+ self.tabla_LR[i][x] +'</td>')
                    else:
                        reporte.write('<td></td>')
                reporte.write('<td class=separador></td>')
                for x in self.noterminales:
                    if self.tabla_LR[i].__contains__(x):
                        reporte.write('<td>'+ str(self.tabla_LR[i][x]) +'</td>')
                    else:
                        reporte.write('<td></td>')
                reporte.write('</tr>')        
            reporte.write('</table></div>')

        if LR:
            self.reporte_analisis_LALR(reporte,estados,transiciones)


    #fin


    def imprimir_item(self,item_x,LR):
        prod = self.dictionary[item_x[0]]
        item = '<span class=simbolo>'+ prod[0] +'</span>' + self.flecha
        for i in range(0,item_x[1]):
            item += '<span class=simbolo>'+ prod[1][i] +'</span>' 
        item += '<span class=punto>.</span>'
        for i in range(item_x[1],len(prod[1])):
            if prod[1][i]==self.epsilon:
                break
            item += '<span class=simbolo>'+ prod[1][i] +'</span>'
        if LR:
            item += ' ,'
            for x in item_x[2]:
                item += ' ' + '<span class=simbolo>'+ x +'</span>' + ' |'
            return item[0:len(item)-1]

        return item
    #fin

    def imprimir_transiciones(self,estado,funcion_transicion):
        transiciones = ''
        for x in funcion_transicion[estado]:
            transiciones += '<li>GOTO(I<sub>'+  str(estado) +'</sub>, '+    x[0]+') = I<sub>'+ str(x[1])+'</sub></li>'
        return transiciones   
    #fin

    def imprimir_transiciones_LALR(self,estado,funcion_transicion,nombres):
        transiciones = ''
        for x in funcion_transicion[estado]:
            transiciones += '<li>GOTO(I<sub>'+  str(nombres[estado]) +'</sub>, '+    x[0]+') = I<sub>'+ str(nombres[x[1]])+'</sub></li>'
        return transiciones   
    #fin

    def reporte_analisis_LALR(self,reporte,estados_LR,transiciones_LR):
        reporte.write('<div><h2>Analisis LALR</h2>')
        reporte.write('<h3>Estados</h3>')
        reporte.write('<table><tr><th>Estado</th><th>Items</th><th>Transiciones</th><th>Conflicto</th></tr>')
        nombres = self.analisis_LALR(estados_LR)
        for i in range(0,len(estados_LR)):
            if estados_LR[i]==None:
                continue
            columnas = '<td>I<sub>'+ str(nombres[i]) +'</sub></td><td><ul>'
            
            for x in estados_LR[i]:
                columnas += '<li>'+ self.imprimir_item(x,True) +'</li>'
            columnas += '</ul></td><td><ul>'
            columnas += self.imprimir_transiciones_LALR(i,transiciones_LR,nombres)
            columnas += '</ul></td><td><ul>'
            if self.conflicto_LR.__contains__(i):
                conflicto = '<li>'+self.conflicto_LR[i][0]+'</li>'
                conflicto += '<li>'+self.imprimir_item(self.conflicto_LR[i][1],True)+'</li>'
                conflicto += '<li>'+self.imprimir_item(self.conflicto_LR[i][2],True)+'</li>'
                columnas += conflicto + '</ul></td>'

            reporte.write('<tr>'+ columnas +'</tr>')
        reporte.write('</table>')


        if len(self.conflicto_LR)>0:
            reporte.write('<h4>Conclusion: La gramatica no es LALR(1)</h4></div>')

        else:
            reporte.write('<h4>Conclusion: La gramatica es LALR(1)</h4></div>')
            reporte.write('<div><h3>Tabla LALR(1)</h3><table><tr>')
            
            a = self.terminales + ['$']
            a.remove(self.epsilon)
            reporte.write('<th></th>')
            for x in a:
                reporte.write('<th>'+ x +'</th>')
            reporte.write('<th class=separador></th>')
            for x in self.noterminales:
                reporte.write('<th>'+ x +'</th>')
            reporte.write('</tr>')

            for i in range(0,len(estados_LR)):
                if estados_LR[i]==None:
                    continue
                reporte.write('<tr>')
                reporte.write('<td>I<sub>'+str(nombres[i])+'</sub></td>')
                for x in a:
                    if self.tabla_LR[i].__contains__(x):
                        reporte.write('<td>'+ self.tabla_LR[i][x] +'</td>')
                    else:
                        reporte.write('<td></td>')
                reporte.write('<td class=separador></td>')
                for x in self.noterminales:
                    if self.tabla_LR[i].__contains__(x):
                        reporte.write('<td>'+ str(self.tabla_LR[i][x]) +'</td>')
                    else:
                        reporte.write('<td></td>')
                reporte.write('</tr>')        
            reporte.write('</table></div>')


    #fin    

    def analisis_LALR(self,estados_LR):
        # la tabla LR se sigue indexando con numeros
        # si se indexa en una llave que no esta es porque ese estado se unio con otro        
        
        self.conflicto_LR.clear()
        nuevos_nombres_estados = {}
        for i in range(0,len(estados_LR)):
            actual = estados_LR[i]
            if actual == None:
                continue
            union = []
            nuevos_nombres_estados[i] = str(i)
            for j in range(i+1,len(estados_LR)):
                if estados_LR[j]==None:
                    continue
                nuevo = self.comparar_centro(actual,estados_LR[j])
                if nuevo != None:
                    actual = nuevo
                    estados_LR[j] = None
                    nuevos_nombres_estados[i] +='+'+ str(j)
                    union.append(j)
                    self.tabla_LR[i].update(self.tabla_LR[j])
                    self.tabla_LR[j] = None
            for x in union:
                nuevos_nombres_estados[x] = nuevos_nombres_estados[i]
            estados_LR[i] = actual.copy()
            self.no_hay_conflicto(estados_LR[i],True,i)
        #fin

        for i in range(0,len(estados_LR)):
            if estados_LR[i]==None:
                continue
            for x in self.tabla_LR[i]:
                content = self.tabla_LR[i][x]
                if content == 'OK':
                    continue
                if type(content)==type(1):
                    self.tabla_LR[i][x] = nuevos_nombres_estados[content]
                    continue
                if content[0]=='r':
                    continue
                change = int(content[1:]) 
                change = nuevos_nombres_estados[change]
                self.tabla_LR[i][x] = content[0] + change



        return nuevos_nombres_estados
    #fin


    
    def comparar_centro(self,estado_1,estado_2):
        nuevo_estado = []
        for i in range(0,len(estado_1)):
            if i==len(estado_2):
                return None
            item_1 = estado_1[i]
            item_2 = estado_2[i]
            if not(item_1[0]==item_2[0] and item_1[1]==item_2[1]):
                return None 
            reduce_item = item_1[2].union(item_2[2])
            nuevo_estado.append((item_1[0],item_1[1],reduce_item))

        return nuevo_estado




    def group_LR(self,LR):         
        estados = []
        transiciones = {}
        self.tabla_LR.clear()
        self.conflicto_LR.clear()

        estados.append([(0,0)])
        if LR:
            estados.clear()
            estados.append([(0,0,{"$"})])
        self.desplegar(estados[0],LR)
        self.no_hay_conflicto(estados[0],LR,0)

        cola = [0]
        proximo = 1
        while len(cola) > 0:
            estado_actual = cola[0]
            transiciones[estado_actual] = [] #lista de tuplas
            cola.remove(estado_actual)            
            self.tabla_LR.append({})
            elementos = []
            equipos = []
            #agrupar
            for item in estados[estado_actual]:                
                p = self.dictionary[item[0]] # item LR:  (no_produccion,cant_antes_coma,conjunto)
                pderecha = p[1]
                cond1 = item[1] == len(pderecha) # si todo esta antes del punto
                cond2 = False
                if not(cond1):
                    cond2 = pderecha[item[1]] == self.epsilon
                
                if cond1  or cond2:   #si es un reduce
                    if item[0] == 0:
                        self.tabla_LR[estado_actual]['$'] = 'OK'
                        continue
                    fo = self.FOLLOW[p[0]]
                    if LR:
                        fo = item[2]
                    for x in fo:
                        self.tabla_LR[estado_actual][x] = ('r'+str(item[0]))               
                    continue
                
                
                
                letra = pderecha[item[1]]
                punto_corrido = (item[0],item[1]+1)
                if LR:
                    punto_corrido = (item[0],item[1]+1,item[2].copy())
                pos = -1
                for i in range(0,len(elementos)):
                    if elementos[i] == letra:
                        pos = i
                        break
                if pos == -1:
                    equipos.append([punto_corrido])
                    elementos.append(letra)
                else:
                    equipos[pos].append(punto_corrido)

                  
            # 'equipos' tiene los nuevos posibles estados
            for i in range(0,len(elementos)):
                self.desplegar(equipos[i],LR)

                transicion = -1
                for j in range(0,len(estados)):
                        if estados[j] == equipos[i]:
                            transicion = j
                            break

                if transicion == -1:
                    transicion = proximo
                    cola.append(proximo)
                    estados.append(equipos[i].copy())
                    proximo+=1 

                self.no_hay_conflicto(equipos[i],LR,transicion)
                transiciones[estado_actual].append((elementos[i],transicion))        
                if self.terminales.__contains__(elementos[i]):
                    self.tabla_LR[estado_actual][elementos[i]] = ('s'+str(transicion))
                else:
                    self.tabla_LR[estado_actual][elementos[i]] = transicion

        return (estados,transiciones)
    
    
    
    def generar(self,item, no_produccion, LR):  # devuelve un item
        # item LR:  (no_produccion,antes_coma,conjunto)
        if not(LR):
            return (no_produccion,0)
        else:
            derecha = self.dictionary[item[0]][1]
            derecha = derecha[item[1]+1:len(derecha)]
            first = self.first_prod(derecha)
            if first.__contains__('epsilon') or len(derecha)==0:
                first.update(set(item[2]))
                first -= {self.epsilon}
            return (no_produccion,0,first.copy())

    def ordenar(self, lista):
        lista = list(lista)
        for i in range(0,len(lista)):
            menor = lista[i]
            pos = i
            for j in range(i+1,len(lista)):
                if lista[j]<menor:
                    menor = lista[j]
                    pos = j
            lista[pos] = lista[i]
            lista[i] = menor

    def desplegar(self, X, LR):  # X es un estado incompleto
        a = X.copy()
        while len(a) > 0:
            temp = []
            for i in a:
                tpto = self.dictionary[i[0]][1]
                if len(tpto) == i[1]:
                    temp.append(i)
                    continue
                tpto = tpto[i[1]]
                if self.noterminales.__contains__(tpto):
                    for x in self.grupos[tpto]:  # grupos[no_terminal] tiene los numeros de las producciones q lo tienen como cabecera
                        nueva = self.generar(i,x,LR)
                        if not(X.__contains__(nueva)):
                            a.append(nueva)
                            X.append(nueva)
                        
                temp.append(i)  
            for x in temp:
                a.remove(x)            
            temp.clear() 

            if not(LR):
                return

            for i in range(0,len(X)):
                if X[i]==None:
                    continue
                nueva = X[i]
                for j in range(i+1,len(X)):
                    if X[j]==None:
                        continue
                    if nueva[0]==X[j][0] and nueva[1]==X[j][1]:
                        nueva=(nueva[0],nueva[1],nueva[2].union(X[j][2]))
                        X[j]=None
                X[i]=nueva
            while X.__contains__(None):
                X.remove(None)


    def no_hay_conflicto(self,estado,LR,no_estado): # un estado es una lista de tuplas
        shift = []
        mi_reduce = []

        for x in estado:
            p = self.dictionary[x[0]]
            pd = p[1]
            cond1 = x[1] == len(pd) # si todo esta antes del punto
            cond2 = False
            if not(cond1):
                cond2 = pd[x[1]] == self.epsilon
            
            if cond1  or cond2:   #si es un reduce
                fo1 = self.FOLLOW[p[0]]
                if LR:
                    fo1 = x[2]
                for y in mi_reduce:
                    fo2 = self.FOLLOW[self.dictionary[y[0]][0]]
                    if LR:
                        fo2 = y[2]
                    if len(fo1.intersection(fo2)) > 0:
                        self.conflicto_LR[no_estado] = ('reduce-reduce',x,y)
                        return False 
                mi_reduce.append(x)
                
                for y in shift:
                    tpto = self.dictionary[y[0]][1][y[1]]
                    if fo1.__contains__(tpto):
                        self.conflicto_LR[no_estado] = ('shift-reduce',x,y)
                        return False #conflicto shift-reduce
            elif self.terminales.__contains__(self.dictionary[x[0]][1][x[1]]):
                shift.append(x)
                for y in mi_reduce:
                    foy = self.FOLLOW[self.dictionary[y[0]][0]]
                    if LR:
                        foy = y[2]
                    if  foy.__contains__(self.dictionary[x[0]][1][x[1]]):
                        return False #conflicto shift-reduce
        return True

    def no_produccion(self,produccion):
        for x in self.dictionary.keys():
            if self.dictionary[x] == produccion:
                return x
        return -1
            
    def LL_metodo(self):
        k = set(self.terminales.copy())
        k.add('$')
        for x in self.noterminales:
            self.LL[x] = {}
            for y in k:
                self.LL[x][y] = None
                for z in self.grupos[x]:
                    if self.FFirst[z].__contains__(y):
                        if self.LL[x][y] != None:
                            self.conflicto_LL.append((self.LL[x][y],z))
                        self.LL[x][y] = z

        

    def first_prod(self,forma_oracional):  #calcula el first de una forma oracional
        sol = set()
        for x in forma_oracional:
            if self.terminales.__contains__(x):
                sol.add(x)
                if x!= self.epsilon:
                    sol-={self.epsilon}
                break
            else:
                sol.update(self.FIRST[x])
                if not(self.FIRST[x].__contains__(self.epsilon)):  # si no contiene a epsilon
                    break
        return sol    

    def ffirst(self):
        for x in self.producciones:
            no = self.no_produccion(x)
            self.FFirst[no] = set()
            self.FFirst[no].update(self.FP[no])
            if self.FP[no].__contains__(self.epsilon):
                self.FFirst[no].update(self.FOLLOW[x[0]])
                self.FFirst[no] -= {self.epsilon}
        
                            
    def follow(self):
        for x in self.noterminales:
            self.FOLLOW[x] = set()
        self.FOLLOW[self.distinguido].add('$')

        pendientes = set()   # (0,1) follow(0).add(follow(1))
        for prod in self.producciones:
            derecha = prod[1]
            for i in range(0,len(derecha)):
                if self.noterminales.__contains__(derecha[i]):
                    sufijo = derecha[i+1:len(derecha)]
                    fo = self.first_prod(sufijo)
                    cond1 = fo.__contains__(self.epsilon) or len(sufijo) == 0
                    fo -= {self.epsilon}
                    self.FOLLOW[derecha[i]].update(fo)
                    if cond1 and derecha[i] != prod[0]:
                        pendientes.add((derecha[i],prod[0]))

        cambio = True
        while cambio:
            cambio = False
            for x in pendientes:
                if not(self.FOLLOW[x[1]].issubset(self.FOLLOW[x[0]])):
                    cambio = True
                    self.FOLLOW[x[0]].update(self.FOLLOW[x[1]]) 
 
    def first(self):
        pila = {}
        prod_epsilon = []
        for x in self.noterminales:
            self.FIRST[x] = set()
            pila[x] = []
            for y in self.grupos[x]:
                pila[x].append(y)
                prod = self.dictionary[y]
                self.FP[y] = set()
                if prod[1][0] == self.epsilon:
                    pila[x].remove(y)
                    prod_epsilon.append(prod)
                    self.FIRST[prod[0]].add(self.epsilon)
                    self.FP[y].add(self.epsilon)
        #fin                    
 
        nueva = True
        posibles_epsilon = self.producciones.copy()
        for x in prod_epsilon:
            posibles_epsilon.remove(x)
        while nueva:
            nueva = False
            for x in posibles_epsilon:
                si = True
                for y in x[1]:
                    if self.terminales.__contains__(y) or not(self.FIRST[y].__contains__(self.epsilon)): 
                        si = False
                if si:
                    self.FIRST[x[0]].add(self.epsilon)
                    self.FP[self.no_produccion(x)].add(self.epsilon)
                    prod_epsilon.append(x)
                    nueva = True
            for x in prod_epsilon:
                if posibles_epsilon.__contains__(x):
                    posibles_epsilon.remove(x)
        #hola
    
        cambio = True
        temp = []
        while cambio:
            cambio = False
            for x in self.noterminales:
                for no_prod in pila[x]:
                    parte_derecha = self.dictionary[no_prod][1]
                    print('derecha '+str(parte_derecha))
                    for y in parte_derecha:
                        print(' '+y)
                        if self.terminales.__contains__(y):
                            if not(self.FP[no_prod].__contains__(y)): 
                                cambio = True
                            self.FP[no_prod].add(y)
                            self.FIRST[x].add(y)
                            break
                        else:
                            cond = len(self.FIRST[y].difference(self.FIRST[x])-{self.epsilon})>0
                            if cond:
                                cambio = True
                                add = self.FIRST[y].copy()
                                add -= {self.epsilon}
                                self.FP[no_prod] |= add
                                self.FIRST[x] |= add

                            if not(self.FIRST[y].__contains__(self.epsilon)):
                                break 
        #fin

        for i in range(1,len(self.producciones)):
            derecha = self.dictionary[i][1]
            self.FP[i] = self.first_prod(derecha)
            print('first de '+str(derecha)+' es '+str(self.FP[i]))