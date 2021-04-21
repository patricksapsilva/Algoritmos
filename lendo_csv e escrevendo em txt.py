from igraph import *
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

#Lendo o arquivo csv.
texto = open("grafo.csv", 'r',encoding='utf=8')
conteudo = texto.read()

#Escrevendo o arquivo txt.
arquivo = open('arq01.txt','w')
arquivo.write(conteudo)






