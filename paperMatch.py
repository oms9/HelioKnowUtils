import re
import sys
import csv
import json
import spacy
import logging
import argparse

sp = spacy.load('en_core_web_sm')
LOG = logging.getLogger('HelioMatch')
logging.basicConfig(level=logging.INFO)

def analyzeBib(paperCode):
    '''Function to analyze the bibcode of a paper'''
    biblist = ['SpWea','GeoRL','JGR','JGRA','JGRE','LRSP','STP','P&SS',
            'Ap&SS','SoPh','RvGSP','SSRv','AcAau','AcA','SLSci','SpReT',
            'AdAnS','AdA&A','AASP','AdAp','AdAtS','AdGeo','AdSpR','ASPRv',
            'AurPh','JComp','JPCom','Cmplx','LRCA','ApL', 'FrASS', 'E&SS']

    bibCode = re.findall("[A-Za-z!\"#$%&'()*+, \-/:;<=>?@[\\]^_`{|}~]+]*[0-9]*", paperCode)
    bibCode = bibCode[0]

    if bibCode in biblist: 
        LOG.debug("Matched bibcode: {}".format(paperCode))
        return True
    else:
        return False

def analyzeTxt(paperAbstract, paperTitle, wordsList, threshHold):
    '''Function to analyze the abstract of a paper'''
    global paperCount
    matches = {}
    totalMatches = 0
    abs = sp(paperAbstract)
    tit = sp(paperTitle)
    
    '''
    #Phrase matching
    
    for word in wordsList:
        if word in paperAbstract or word in paperTitle:
            LOG.debug("Matched phrase '{}' in paper# {}".format(word, paperCount))
            if word not in matches:
                matches[word] = 1
            else:
                matches[word] += 1
    '''

    #Abstract matching
    for word in abs:
        if isAcronym(word.text):
            continue
        else:
            word = word.lemma_
            if word in wordsList:
                LOG.debug("Matched '{}' in paper# {}'s abstract.".format(word, paperCount))
                if word not in matches:
                    matches[word] = 1
                else:
                    matches[word] += 1

    #Title matching
    for word in tit:
        if isAcronym(word.text):
            continue
        else:
            word = word.lemma_
            if word in wordsList:
                LOG.debug("Matched '{}' in paper# {}'s Title.".format(word, paperCount))
                if word not in matches:
                    matches[word] = 1
                else:
                    matches[word] += 1


    #Tally matches and final decision
    for el in matches:
        totalMatches = totalMatches + matches[el]

    if totalMatches >= threshHold:
        LOG.debug("Paper word match success for paper#: {}".format(paperCount))
        return True

    return False


def isAcronym(inWord):
    capCount = 0

    if inWord.isupper():
        return True
        
    for letter in inWord:
        if letter.isupper():
            capCount += 1
            
    if ((capCount / len(inWord)) * 100) >= 50:
        LOG.debug("Word {} detected as acronym".format(inWord))
        return True
    
    return False


def savePaper(match, outFile):
    '''This function will dump a single paper to a specified JSON file'''
    global paperCount
    try:
        json.dump(match, outFile, indent=2, ensure_ascii=False)
        outFile.write(',\n')
        LOG.debug("Saved paper#: {} successfully.".format(paperCount))
        return 1
    except:
        return -1


if __name__ == '__main__': 

    ap = argparse.ArgumentParser(description='Extracts papers about Heliophysics topics from ADS Data')

    ap.add_argument('-i', '--inFile', type=str, help='Data file to analyze', required=True)
    ap.add_argument('-d', '--debug', default = False, action = 'store_true', help='Turn on debugging messages')
    ap.add_argument('-o', '--outFile', type=str, default = 'matchedPapers.json', help='Save files to path\\fileName')
    ap.add_argument('-w', '--wordCount', type=int, default = 7, help='Number of words to consider a paper heliophysics based if mode 2 or 3 are selected, defaults to 7')
    ap.add_argument('-m', '--mode', type=int, default = 1, help='Mode selection to match papers\n"1" - for bibcode only (default)\n"2" - for bibcode AND abstract\n"3" - for bibcode OR abstract')

    args = ap.parse_args()

    failures = 0
    matchCount = 0
    progPrint = True

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        LOG.setLevel(logging.DEBUG)
        progPrint = False
    #Opening data file.
    try:
        file = open("{}".format(args.inFile), 'r', encoding="utf-8")
        print("\nLoading data file, please wait.")
        LOG.debug("Provided file name: '{}'".format(str(args.inFile)))
    except:
        LOG.debug("Provided file name (Failed): '{}'".format(args.inFile))
        sys.exit("File load failed, check input file.")

    #Load data file into JSON dict.
    try:
        docs = json.load(file)
        file.close()
        print("Done loading and parsing file.")
    except:
        sys.exit("Data load failed, JSON syntax failure.")

    #Preparing output file.
    out = open("{}.json".format(args.outFile), 'w', encoding="utf-8")
    out.write('{\n  "Matched_Papers": [\n')


    #   Mode 1 - Bibcode only           #
    if args.mode == 1:
        LOG.debug("MODE 1 SELECTED")
        #Analyze papers.
        print("\nAnalyzing papers:")
        paperCount = 1
        for paper in docs['docs']:
            try:
                #LOG.debug("Loaded paper: {}".format(str(paperCount)))
                if analyzeBib(paper['bibcode']):
                    savePaper(paper, out)
                    matchCount += 1
                else:
                    pass
                if progPrint:
                    prog = round((paperCount / docs['numFound']) * 40)
                    print('[' + ('=' * prog) + ('-' * (40 - prog)) + ']\t' + str(paperCount) + 
                          " out of " + str(docs['numFound']) + " papers (" + str(round((paperCount / docs['numFound']) * 100)) + "%)", end='\r')
                paperCount += 1
            except (KeyError):
                failures += 1
                paperCount += 1

    #   Mode 2 - Bibcode AND abstract   #
    elif args.mode == 2:
        LOG.debug("MODE 2 SELECTED")
        with open('nonUniqueTerms.csv', 'r') as termFile:
            termFile.readline()
            terms = []
            for a, b, c in csv.reader(termFile, delimiter = ','):
               # a = sp(a)
                #a = a.lemma_
                #print(a)
                terms.append(a)
                
        #Analyze papers.
        print("\nAnalyzing papers:")
        paperCount = 1
        for paper in docs['docs']:
            try:
                #LOG.debug("Loaded paper: {}".format(str(paperCount)))
                if analyzeBib(paper['bibcode']) and analyzeTxt(paper['abstract'], paper['title'][len(paper['title'])-1], terms, args.wordCount):
                    savePaper(paper, out)
                    matchCount += 1
                    
                if progPrint:
                    prog = round((paperCount / docs['numFound']) * 40)
                    print('[' + ('=' * prog) + ('-' * (40 - prog)) + ']\t' + str(paperCount) +
                          " out of " + str(docs['numFound']) + " papers (" + str(round((paperCount / docs['numFound']) * 100)) + "%)", end='\r')
                paperCount += 1
            except (KeyError):
                failures += 1
                paperCount += 1

    #   Mode 3 - Bibcode OR abstract   #
    elif args.mode == 3:
        LOG.debug("MODE 3 SELECTED")
        with open('nonUniqueTerms.csv', 'r') as termFile:
            termFile.readline()
            terms = []
            for a, b, c in csv.reader(termFile, delimiter = ','):
                terms.append(a)
        #Analyze papers.
        print("\nAnalyzing papers:")
        paperCount = 1
        for paper in docs['docs']:
            try:
                #LOG.debug("Loaded paper: {}".format(str(paperCount)))
                if analyzeBib(paper['bibcode']) or analyzeTxt(paper['abstract'], paper['title'][0], terms, args.wordCount):
                    savePaper(paper, out)
                    matchCount += 1
                    
                if progPrint:
                    prog = round((paperCount / docs['numFound']) * 40)
                    print('[' + ('=' * prog) + ('-' * (40 - prog)) + ']\t' + str(paperCount) +
                          " out of " + str(docs['numFound']) + " papers (" + str(round((paperCount / docs['numFound']) * 100)) + "%)", end='\r')
                paperCount += 1
            except (KeyError):
                failures += 1
                paperCount += 1
                
    #Failure to select mode
    else:
        sys.exit("Mode selection failed.")

# END anaylsis, finalize file and exit.    
    out.seek(out.tell() - 3)
    out.truncate()
    out.write('\n]\n}')
    out.close()
    print("\n\nMatched", matchCount, "papers out of", paperCount - 1)
    print("Number of corrupted papers encountered:", failures)
    sys.exit("\nAll done!\n")
