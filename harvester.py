import os
import json
import traceback
import requests


def sortDict(inDict):
    retDict = {}
    for w in sorted(inDict, key=inDict.get, reverse=True):
        retDict[w] = inDict[w]
    return retDict

path = os.getcwd()
path = os.path.join(path, 'Data')
try:
    os.mkdir(path)
except:
    pass

bibList = ['SpWea','GeoRL','JGR','JGRA','JGRE','LRSP','STP','P&SS',
        'Ap&SS','SoPh','RvGSP','SSRv','AcAau','AcA','SLSci','SpReT',
        'AdAnS','AdA&A','AASP','AdAp','AdAtS','AdGeo','AdSpR','ASPRv',
        'AurPh','JComp','JPCom','Cmplx','LRCA','ApL', 'FrASS', 'E&SS']

token = 'Ir9y98vfhhErqd0F0uGWFjlJCP36L8noiYvnylF6'

totalFound = 0
papers = {"Found": totalFound, "Papers": []}
stats = {}
                
#Send requests.
for code in bibList:
    url = "https://api.adsabs.harvard.edu/v1/search/query?q=bibstem:{} year:2010-2022&fl=bibcode,author,title,citation,abstract".format(code)
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {0}'.format(token)}
    
    response = requests.get(url, headers = headers)
  
    if response.status_code == 200:
        try:
            data = json.loads(response.content.decode('utf-8'))
        except:
            print("Loading JSON failed.")
            
        if len(str(data['response']['docs'])) == 0:
                continue
        stats[code] = int(data['response']['numFound'])
        totalFound = totalFound + int(data['response']['numFound'])
        
        for paper in data['response']['docs']:
            papers["Found"] = totalFound
            papers["Papers"].append(paper)

    else:
        print("Query for {} journals failed.".format(code))

print("Writing data to file.")

with open('{path}\\{fileName}.json'.format(path = path, fileName = 'AllData'), "w", encoding = "utf-8") as outFile:
    outFile.write("{")
    outFile.write(json.dumps(papers, indent=3, sort_keys = True)[1:-1])
    outFile.write("}\n")

stats = sortDict(stats)

with open('{path}\\{fileName}.txt'.format(path = path, fileName = 'Stats'), "w", encoding = "utf-8") as statFile:
    statFile.write("|==============[ Statistics ]==============|\n\n")
    for el in stats:
        statFile.write(str(el) + ": " + str(stats[el]) + '\n')


print("\nTotal found: ", totalFound)
print("\nDone!\n")
