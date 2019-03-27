# commonshare
Python scripts for simulating Commonfare data, calculating commonshare, calculating recommendations, and visualisation

Requirements:

Python 2.x, NetworkX 2.2, Louvain community detection, (and the random names generator if running the simulation). Install with the following commands:
```bash
pip install networkx==2.2
pip install scipy python-louvain names
```

<h3>Important Contents:</h3>

<b>python/</b>

- parsegexf.py: Main class for parsing GEXF file, which then calls kcore.py to calculate commonshare and output JSON files.

- config.py: Contains key constants used in the simulation. Values in here can be adjusted to determine how many users are generated, the number of actions per day, and how many days the simulation runs for. It now also contains constants to allow adjustment of collusion detection.

- dynetworkx.py: Contains adjusted core_number method from the 'core.py' file of NetworkX. Additional methods have been implemented to calculate the weighted, directed core number values at particular points in time. Also contains an implemented collusion detection algorithm.

- kcore.py: Uses the methods in dynetworkx.py to calculate Commonshare values for each node in the graph every two weeks. Outputs JSON files, described below.

- pagerank.py: Contains an implementation of the 'Personalised PageRank' algorithm used in the story recommender (details below) 

Classes for simulation (in the <b>/simulation</b> directory):
- graphclasses.py: Base classes that represent entities in the simulation
- listinggenerator.py: Generates listing names by picking an adjective and a noun from requisite dictionaries
- phrases.py: Generates story 'names' in the simulation by picking four random words from a dictionary
- simulation.py: Run 'python simulation.py' from the python/simulation directory to generate simulated data (this gets stored in data/input/simulateddata.gexf)

<b>data/output/</b>

- <b>graphdata/biweekly/...</b>: Contains graph-based JSON files representing every two weeks of Commonfare interactions, with Commonshare values calculated for each node (1.json ... X.json)
    Also contains a cumulative graph-based JSON file of every interaction made in Commonfare since its initiation (0.json)

- <b>userdata/...</b>: Contains a file for every user, named <USER_ID>.json, which represents their entire interaction history

- recommenderdata.gexf: Contains a cleaned version of the original GEXF, used for generating story recommendations

### Instructions for use

1. Put GEXF file in the `data/input` directory
2. Change directory to `python/` and run `python parsegexf ../data/input/<YOUR_FILE_NAME>`
3. JSON files will be output into the `data/output` directory as described above