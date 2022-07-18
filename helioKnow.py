import sys
import json
import math
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
#del neededCites

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

#Adding the papers as nodes to the graph, with the #of cites as an attribute.
for paper in citeRank:
    graph.add_node(str(paper), weight=citeRank[paper], size = citeRank[paper])

for paper in citeLinks:
    for cite in citeLinks[paper]:
        graph.add_edge(paper, cite)


degCent = nx.degree_centrality(graph)
subCent = nx.subgraph_centrality(graph)
betCent = nx.betweenness_centrality(graph)

with open("Degree Centrality.txt", "w", encoding="utf-8") as statFile:
    statFile.write("|==============[ Degree Centrality ]==============|\n")
    for node in degCent:
        statFile.write(str(node) + ": " + str(degCent[node]) + '\n')
        
with open("Subgraph Centrality.txt", "w", encoding="utf-8") as statFile:
    statFile.write("|==============[ Subgraph Centrality ]==============|\n")
    for node in subCent:
        statFile.write(str(node) + ": " + str(subCent[node]) + '\n')

with open("Betweenness Centrality.txt", "w", encoding="utf-8") as statFile:
    statFile.write("|==============[ Betweenness Centrality ]==============|\n")
    for node in betCent:
        statFile.write(str(node) + ": " + str(betCent[node]) + '\n')
        
paperDeg = {}
for paper in citeRank:
    paperDeg[paper] = 0
    try:
        paperDeg[paper] += citeRank[paper]
        paperDeg[paper] += len(citeLinks[paper]) 
    except(KeyError):
        pass

paperDeg = sortDict(paperDeg)

with open("Bibcode Degrees.txt", "w", encoding="utf-8") as statFile:
    statFile.write("|==============[ Bibcode Degrees ]==============|\n")
    for paper in paperDeg:
        statFile.write(str(paper) + ": " + str(paperDeg[paper]) + '\n')

degDict = {}
for bibcode in paperDeg:
    if paperDeg[bibcode] not in degDict:
        degDict[paperDeg[bibcode]] = 1
    else:
        degDict[paperDeg[bibcode]] += 1
    
#degDict = sortDict(degDict)
with open("Degree Distribution.txt", "w", encoding="utf-8") as statFile:
    statFile.write("|==============[ Degree Distribution ]==============|\n")
    for paper in degDict:
        statFile.write(str(paper) + ": " + str(degDict[paper]) + '\n')

#Plotting centrality
fig, (ax1,ax2,ax3) = plt.subplots(1, 3)
cenX = []
degY = []

betY = []
subY = []

for point in citeRank:
    cenX.append(citeRank[point])
    degY.append(degCent[point])

for point in citeRank:
    betY.append(betCent[point])

for point in citeRank:
    subY.append(subCent[point])    

ax1.bar(x = cenX, height = degY, color = 'r')
ax1.set_xlabel('Num. of Citations')
ax1.set_title('Degree Centrality')

ax2.bar(x = cenX, height = betY, color = 'b')
ax2.set_xlabel('Num. of Citations')
ax2.set_title('Betweenness Centrality')

ax3.bar(x = cenX, height = subY, color = 'm')
ax3.set_xlabel('Num. of Citations')
ax3.set_title('Subgraph Centrality')

plt.show()
logX = []
logY = []
for el in list(degDict):
    logX.append(math.log(el,10))
for el in list(degDict.keys()):
    logY.append("{:.2f}".format(math.log(el,10)))
    
fig, ax4 = plt.subplots()
ax4.bar(range(len(degDict)), logX, tick_label = logY)
ax4.set_title("Log Log Degree distribution")

plt.show()
              
nx.draw(graph)
plt.show()

print("Done!")
