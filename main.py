from operator import itemgetter
import xml.etree.ElementTree as ET
import time

tree = ET.parse("data.xml")
root = tree.getroot()

stopwords = [  # NAO PRECISO MAIS DISSO KK (SERA?)
  'this', 'that', 'is', 'at', 'as', 'of', 'when', 'where', 'if', 'of', 'out',
  'in', 'with', 'without', 'besides', 'i', 'me', 'myself', 'they', 'them',
  'themselves', 'you', 'your', 'yourself', 'yourselves', 'our', 'ourselves',
  'yours', "you're", 'he', 'him', 'his', 'she', 'her', 'hers', 'himself',
  'herself', 'who', 'else', 'it', 'its', 'itself', 'their', 'theirs', 'what',
  'whom', 'whose', 'which', 'these', 'those', 'am', 'are', 'was', 'a', 'an',
  'the', 'were', 'and', 'but', 'because', 'until', 'while', 'by', 'for'
]


def preProcessing(root):  # RETORNA O INDICE COM TODAS AS PAGINAS
  countPage = 1
  indice = dict()

  for page in root:
    print(countPage)
    id = page.find("id").text
    pageTitle = page.find("title").text

    # ADICIONA UMA PAGINA AO INDICE
    indice[id] = {
      "titulo": pageTitle
    }  # TEXTO EH A CHAVE E 0 EH O NUM DE OCORRENCIAS

    palavras = indice[id]

    # TITULO
    title = page.find("title").text.lower()

    for palavra in title.split():

      if len(palavra) <= 3:
        continue
      else:
        count = palavras.get(palavra, 0)
        palavras[palavra] = count + 10

    # TEXTO
    text = page.find("text").text.lower()

    for palavra in text.split():

      if len(palavra) <= 3:
        continue
      else:
        count = palavras.get(palavra, 0)
        palavras[palavra] = count + 1

    countPage += 1
  return indice


#================================================================================================================================================

start_time = time.time()
indice = preProcessing(root)
print("--- %s seconds to pre-process ---" %
      (time.time() - start_time))  # TEMPO DE PRE-PROCESSAMENTO
"""
for pageId, wordDict in indice.items():
  for word, occur in wordDict.items():
    print("ID da pagina: {}, Palavra: {}, Ocorrencias: {}".format(pageId, word, occur))
"""
while True:
  palavras = input("Insira a(s) palavra(s) a ser(em) buscada(s)\n").split()

  start_time = time.time()
  verbetes = []

  for pageId, wordDict in indice.items():
    pontuacoes = [0, 0]
    count = 0
    pts = 0

    # PARA CADA PALAVRA INSERIDA
    for palavra in palavras:
      qtd_texto = 0
      qtd_titulo = 0

      # PULA A STOPWORD
      if len(palavra) <= 3:
        continue
      else:
        palavra = palavra.lower()

        qtd_texto += wordDict.get(palavra, 0)

      pontuacoes[count] = qtd_texto
      count += 1

    # CALCULO DA PONTUACAO DOS VERBETES
    totalOcorr = pontuacoes[0] + pontuacoes[1]

    if totalOcorr == 0: totalOcorr = 1

    peso1 = pontuacoes[0] / totalOcorr
    peso2 = pontuacoes[1] / totalOcorr

    if peso1 == peso2 == 0: peso1 = 1  # AO MENOS 1 VARIAVEL PRECISA SER > 0

    # SE A DIFERENCA DE PESOS FOR MUITO GRANDE, O MAIOR PESO EH REDUZIDO E O MENOR EH AUMENTADO --> BALANCEAMENTO DE PESOS
    if len(palavras) == 2 and (peso1 >= .7 or peso2 >= .7):
      reducaoMaiorPeso = .5 - min(peso2, peso1)
      if peso1 > peso2:
        peso1 -= reducaoMaiorPeso
        peso2 += reducaoMaiorPeso
      else:
        peso2 -= reducaoMaiorPeso
        peso1 += reducaoMaiorPeso

    peso1 *= 1.25  # PESO DA PRIMEIRA PALAVRA EH AUMENTADO EM 25%

    # MEDIA PONDERADA
    pts = ((pontuacoes[0] * peso1) + (pontuacoes[1] * peso2)) / (peso1 + peso2)

    verbetes.append({"id": pageId, "pts": pts, "titulo": wordDict["titulo"]})

  verbetes_ordenados = sorted(verbetes, key=itemgetter('pts'), reverse=True)

  print("\n15 MELHORES RESULTADOS:\n")
  for i in range(0, 15):
    print("ID: {} | Titulo: {} | Pts: {} |".format(
      verbetes_ordenados[i]["id"], verbetes_ordenados[i]["titulo"],
      verbetes_ordenados[i]["pts"]))
    print()
    
  print("--- %s seconds to search ---" % (time.time() - start_time)) # TEMPO DE BUSCA

  # for verbete in verbetes_ordenados:
  # print(verbete)
  # print()
