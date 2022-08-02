# HelioKnow Utils
A contribution to the heliophysics KNOWledge Network (Helio-Know), Natural Language Processing and Knowledge Graphs of Heliophysics research.

## Introduction
The Helio-Know knowledge network is all about Natural Language Processing (NLP) and Knowledge Graphs about the literature in the field of Heliophysics. It aims to provide useful insight into the works published in the Heliophysics field. Constructing knowledge graphs can be difficult because human based tagging of papers was found to be inaccurate and often under-represents the value and content of the literature. There were also many other problems when processing the documents, like missing abstracts or multi-lingual titles when pulling a large body of documents and some text processing challenges like handling hyphen joined words, acronyms and punctuation, and matching plural to singular words.


Hence the creation of HelioKnow Utils, a collection of tools aimed at solving the aforementioned problems and easing the road to creating networks of HelioPhysics literature.

These tools are (in expected order of operation):

 1. harvester.py  -  A script to pull a large body of papers from the Astrophysics Data System (ADS).
 2. paperMatch.py  -  A script to filter the papers, keeping the Heliophysics related papers in a new file.
 3. helioKnow.py  -  A script to create the network from the papers and pull metrics and stats from the generated network.

# Getting Started
Before you start building networks and performing research, you must do the following:
 - Clone the repository: `git clone https://github.com/oms9/HelioKnowUtils`
 - Install the dependencies and download the necessary sub-modules.
 - Obtain an API key to use the ADS API.
 - Prepare a list of Heliophysics related terms, keywords or phrases to match papers against.

After cloning the repository, let's start with the dependencies since these can run in the background.

## Dependencies

In order to run these scripts you must have the following Python modules/libraries installed:

 - [Requests](https://requests.readthedocs.io/en/latest/user/install/#install) - `pip install requests`
 - [matplotlib](https://matplotlib.org/stable/users/installing/index.html) - `python -m pip install -U pip`
 - [Colorcet](https://colorcet.holoviz.org/) - `pip install colorcet`
 - [NetworkX](https://networkx.org/) - `pip install networkx[default]`
 - [NLTK](https://www.nltk.org/install.html) - `pip install nltk`
 - [NLTK's stop words](https://www.nltk.org/nltk_data/) - `python  -m  nltk.downloader stopwords` 🔹
 
🔹 If you run into trouble, try running: `python  -m  nltk.downloader all`

## Obtaining an API Key

Getting an API key is fairly simple.
First create an account at: https://ui.adsabs.harvard.edu/ <br>⚠️ **Please note the account requires email verification.** ⚠️
After login, you can generate an API key here: https://ui.adsabs.harvard.edu/user/settings/token

## Match keys/terms

In order to identify Heliophysics related papers, you first curate a list of Heliophysics related terms, keywords or phrases, they could be related to all Heliophysics or a specific sub-discipline.


The file **must** be named `matchKeys.txt`.
The formatting could just be 1 keyword/phrase separated by a newline character `\n`, for example:

```
solar wind
solar magnetic fields
helioseismology
sunspots
solar flares
delta sunspots
solar cycle
```


# Usage



## harvester
Open the file `harvester.py` and paste your API key into the `token` variable and verify which bibstems/journals you want to download from by modifying `bibList`. the default are:

    SpWea GeoRL JGR JGRA JGRE LRSP STP P&SS 
    Ap&SS SoPh RvGSP SSRv AcAau AcA SLSci SpReT 
    AdAnS AdA&A AASP AdAp AdAtS AdGeo AdSpR ASPRv 
    AurPh JComp JPCom Cmplx LRCA ApL FrASS E&SS
Lastly, provide the output file name by modifying the variable `fileName`

You can now run the script and it will download all the papers found from the years 2010 to 2022 and save the result.
## paperMatch

paperMatch is a command-line tool, it is recommended you run the script with the help flag, like so: `python paperMatch.py -h`

the `-i` flag is for specifying the input file name
the `-o` flag is for specifying the output file name
the `-w` flag determines the count of words that must match to consider the paper a match for Heliophysics
the `-m` flag is the mode of operation flag, it has 3 possible modes: (1, 2, 3)

 1. The first mode matches on bibstem only for each papers, eliminating archive papers
 2. The second mode matches both bibstem **AND** by analyzing the abstract and title of the paper for the specified number of matches set by the `-w` flag
 3. The third mode is exactly like the second with the exception of using **OR** during the matching, so bibcode OR word analysis can qualify a paper.

An example run command should look something like this:

    python paperMatch.py -i AllData.json -o W4Matches -w 4 -m 2
	
	
## helioKnow

Open the file `helioKnow.py`, specify the input file by modifying the `inFile` variable.
Paste your API key into the `adsAPIKey` variable.
Specify the number of iterations by modifying the `iterations` variable. 🔹

##### Iterations are the number of traversal the script should perform, A traversal is simply going up the citations chain 1 time, so if you have a source 	paper `A` that has been cited by paper `B`, and you want to know what papers cited paper `B` (and therefore being somewhat related to paper `A`), you have to traverse the chain of citations `1 time`.
🔹There is a limit of 20,000 papers per day that can be requested from ADS on a standard API key.

Specify whether you want to cache the data retrieved from any traversals by setting the `saveADSData` variable to either `True` or `False` 🔸

Specify whether to save the statistics/metrics of the generated network by setting the `saveStats` variable to either `True` or `False` 🔸

🔸Be careful because these two processes will automatically over-write the cache/metrics files if they exist.

You are now free to run the script and patiently await the results!

This is a computationally expensive process and it might take some time to run on consumer hardware.

# Acknowledgements 
This project would not have been possible without the excellent guidance of my experienced mentors, [**Dr. Ryan Mcgranaghan**](https://github.com/rmcgranaghan) and [**Dr. Brian A. Thomas**](https://github.com/brianthomas/)


# License
This work is licensed under the Apache License Version 2.0 (Jan 2004)
You can find a copy of this license in the repository as LICENSE.txt or it can be obtained here: https://www.apache.org/licenses/LICENSE-2.0

