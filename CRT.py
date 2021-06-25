import requests
import networkx as nx
import xml.etree.ElementTree as xml
import matplotlib.pyplot as plt
import graphviz  as gra
import numpy as np
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize 

''' CLASSE QUE DEFINE UM VERTICE '''
class Vertice():
    def __init__(self, name='', id='', ocorrencia='', frequencia='', texto='', relacoes=[]):
        self.name = name.lower()
        self.nameStemming = self.parseStemming(name.lower())
        self.id = id
        self.ocorrencia = ocorrencia
        self.frequencia = frequencia
        self.texto = texto
        self.relacoes = relacoes
        self.conexoes = ''



    def parseStemming(self, word):
      ps = PorterStemmer()
      w = ps.stem(word)
      
      if w == '':
        w = word
      
      return w
        
    def __str__(self):
        return self.name

''' CLASSE QUE DEFINE UM GRAFO COMPLETO '''
class Grafo():
    def __init__(self, grafoName='Grafo'):
        self.grafoName = grafoName
        self.vertices = []
        self.grafoG = None
        self.xml = ''
        
    def printGrafo(self):
        G = nx.Graph()
        
        for v in self.vertices:            
            G.add_node(v.name, size=10)

        for v in self.vertices:
            #G.add_node(v.name)
            if len(v.relacoes) > 0:
                for r in v.relacoes:
                    #G.add_node(r.name)  
                    G.add_edge(v.name, r.name, weight=v.ocorrencia)
        
        self.grafoG = G
        
        
        pos = nx.spring_layout(G)
        #nx.draw_networkx_nodes(G, pos, node_size= 100)
        #nx.draw_networkx_edges(G, pos, width=1)
        #nx.draw_networkx_labels(G, font_size=10,font_family='sans-serif')
        nx.draw_spring(G, with_labels=True, node_color='g', node_size=500)                
        plt.suptitle(self.grafoName)
        plt.show()

        
    def generateGrafoFromXML(self, textXML):
        self.xml = textXML
        xmldoc = xml.fromstring(textXML)        
               
        for nodo in xmldoc:    
            _id = None
            _ocor = 0.0
            _freq = 0
            _text = ''
            _rel = []
            name = nodo.get('name')            
            if nodo.find('id') != None:
                _id = int(nodo.find('id').text)
                
            if nodo.find('ocorrencia') != None:
                _ocor = float(nodo.find('ocorrencia').text)
        
            if nodo.find('frequencia') != None:
                _freq = int(nodo.find('frequencia').text)
        
            if nodo.find('texto') != None:
                _text = nodo.find('texto').text
            
            if nodo.find('relacoes') != None:                 
                relacoes = nodo.findall('relacoes')
                _rel = []
                for re in relacoes:
                    ver = Vertice(name=re.get('name'))
                    ver.id = re.find('name_ID').text
                    #ver.name = re.get('name')
                    ver.conexoes = int(re.find('conexoes').text)
                    _rel.append(ver)
            
            if _id != None: 
                v = Vertice(name, _id, _ocor, _freq, _text, _rel)            
                self.vertices.append(v)    
            
    def coeficienciaRelevancia(self, grafo):
        #Contando quantos node/vertice tem na pergunta
        if len(self.vertices) == 0:
            return 0
        
       
        #Contado os termos da pergunta que aparecem na resposta.                
        sumTerm = 0
        jaExiste = []
        for p in self.vertices:
            for r in grafo.vertices:
                #print('Pergunta: '+p.nameStemming+'   Resposta:'+r.nameStemming)             
                if (p.nameStemming in r.nameStemming) :
                  if (r.nameStemming in jaExiste) == False:                    
                    jaExiste.append(r.nameStemming)
                    sumTerm += 1
        print('Quantidade de termos que tem na PERGUNTA e aparecem na resposta: '+str(sumTerm))
                

        
        #Montando um array em que existe de pares da PERGUNTA que tem RELAÇÕES        
        pRelacoes = []        
        pSemRelacoes = [] 
        for p in self.vertices:
            if len(p.relacoes) > 0: 
                for pp in p.relacoes:                    
                    pRelacoes.append(np.sort(np.array([p.nameStemming, pp.nameStemming])))
            else:
                pSemRelacoes.append(p)
        print('Quantidade de termos da PERGUNTA com relações: '+str(len(pRelacoes)))

        #Montando um array em que existe de pares da RESPOSTA que tem RELAÇÕES        
        rRelacoes = []        
        rSemRelacoes = []
        for r in grafo.vertices:
            if len(r.relacoes) > 0: 
                for rr in r.relacoes:                    
                    rRelacoes.append(np.sort(np.array([r.nameStemming, rr.nameStemming])))
            else:
                rSemRelacoes.append(r)
        print('Quantidade de termos da RESPOSTA com relações: '+str(len(rRelacoes)))
        
        #comparando as RELAÇÕES da pergunta e da respostas que são iguais
        sumRel = 0                
        for i in pRelacoes:
            for r in rRelacoes:                
                if np.array_equal(i, r):                     
                    sumRel +=1
                    break
                
        #comparando os TERMOS sem relações da pergunta e da respostas que são iguais
        sumSemRel = 0
        for i in pSemRelacoes:
            for r in rSemRelacoes:  
                if np.array_equal(i, r):                
                    sumSemRel +=1
                    break                                     
       
    
        NC = sumTerm
        NA = (sumRel + sumsemrel)
        CRT = (NC+NA)
        
        return CRT

PTBR = '1'
ENG = '2'
lang = PTBR
output = '-x' #saída XML
#output = '-b' #somente termos, sem as conexões
#output = '-n' #termos e as frequencia

#Aqui é passado o texto da pergunta do tópico.
p1 = ''

#Aqui é passado o texto da resposta do tópico. 
r1 = ''


def sobek(text, lang):
    r = requests.post('http://sobek.ufrgs.br/V2/webservice/sobek.php',
                      data={'entrada':'-l '+lang+' '+output+' -t '+text})
        
    return r.text
   


pergunta = Grafo('Pergunta')
pergunta.generateGrafoFromXML(sobek(p1, lang))  
#pergunta.printGrafo()  

resposta = Grafo('Resposta')
resposta.generateGrafoFromXML(sobek(r1, lang))
#resposta.printGrafo()


print('Coeficiência de Relevância: '+
      str(pergunta.coeficienciaRelevancia(resposta)))
