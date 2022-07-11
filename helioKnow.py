import sys
import json
#import logging
import requests
#import argparse
import networkx as nx
import matplotlib.pyplot as plt

def sortDict(inDict):
    retDict = {}
    for w in sorted(inDict, key=inDict.get, reverse=True):
        retDict[w] = inDict[w]
    return retDict

#Metrics
noCite = 0
foundCite = 0
paperCount = 0

#Fetching papers
neededCites = []
bibString = 'bibcode\n'
apiKey = 'Ir9y98vfhhErqd0F0uGWFjlJCP36L8noiYvnylF6'

#Graph
citeRank = {}
citeLinks = {}
graph = nx.Graph()

#File/data loading
try:
    print("Attempting to open file now")
    dataFile = open('W4Matches.json', 'r', encoding="utf-8")
    matchedPapers = json.load(dataFile)
    dataFile.close()
    print("Done loading and parsing file.\n\n")
except:
    sys.exit("Data load failed, JSON syntax failure.")

#Gathering needed citations and analyzing data
for paper in matchedPapers['Matched_Papers']:
    paperCount += 1
    try:
        for citation in paper['citation']:
            #Build links
            if paper['bibcode'] not in citeLinks:
                citeLinks[paper['bibcode']] = [citation]
            else:
                citeLinks[paper['bibcode']].append(citation)
                
            #Build count (centrality)
            if citation not in citeRank:
                citeRank[citation] = 1
            else:
                citeRank[citation] += 1
        
            #Add to fetch papers
            if citation not in neededCites:
                neededCites.append(citation)
            else:
                pass
    except KeyError:
        noCite += 1

#Forming bibcode list for query (and removing extra \n) at end
for bibcode in neededCites:
    bibString = bibString + bibcode + '\n'
bibString = bibString[:-2]

#Fetching papers
req = requests.post("https://api.adsabs.harvard.edu/v1/search/bigquery",
                 params={"q":"*:*", "wt": "json", "fl": "bibcode,author,title,citation,abstract", "fq":"{!bitset}","rows":len(neededCites)},
                 headers={'Authorization': 'Bearer ' + apiKey},
                 data=bibString)


adsPapers = json.loads(req.content.decode('utf-8'))
del neededCites

#Level 1 citation analysis     
print("Accesssing fetched ADS papers.")
for paper in adsPapers['response']['docs']:
    try:
        for citation in paper['citation']:
            
            #Build links
            if paper['bibcode'] not in citeLinks:
                citeLinks[paper['bibcode']] = [citation]
            else:
                citeLinks[paper['bibcode']].append(citation)
            #Build count (centrality)
            if citation not in citeRank:
                citeRank[citation] = 1
            else:
                citeRank[citation] += 1
    except:
        pass

citeRank = sortDict(citeRank)

'''
#Testing
with open("AAA.txt", 'w', encoding="utf-8") as out:
    out.write("-=============== [CiteRank] ===============-\n")
    for el in citeRank:
        out.write(str(el) + ": " + str(citeRank[el]) + "\n")
    out.write("-=============== [CiteLink] ===============-\n")
    for el in citeLinks:
        out.write(str(el) + ": " + str(citeLinks[el]) + "\n")
'''

#Adding the papers as nodes to the graph, with the #of cites as an attribute.
for paper in citeRank:
    graph.add_node(str(paper), weight=citeRank[paper], size = citeRank[paper])

for paper in citeLinks:
    for cite in citeLinks[paper]:
        graph.add_edge(paper, cite)

nx.draw(graph)
plt.show()

print("Done!")



