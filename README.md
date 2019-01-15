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


## Docker image
A very basic Docker image is available to run the python scripts `parsegexf.py` and `pagerank.py`.  
No service is running within the docker image at the time of writing but it sets up a python environment with all the dependencies and it runs either of the scripts when the user runs the image.  

Input and output data is exchanged through the files in `./data` directory which is mounted as a volume.

### Building 
To build this image make sure you have Docker installed in your host.
It that is the case you just run:

```
$ docker build -t commonfare/commonshare-python .
```

If you now check docker images available in your host machine you would notice one named `commonfare/commonshare-python`.

```
$ docker images
...
commonfare/commonshare-python         latest              323a3b42764f        30 minutes ago      297MB
...
```

### Running
As mentioned above this image runs either of the following python scripts and then it stops:

 - `paresegexf.py` which takes as input a file in GEXF format and produces as output a series of files in `./data/output/` directory.
  - `pagerank.py` which takes as input a story id and a user id and calculates the recommended stories for such user based on the input story.

**Parameters and environment variables**  
The following environment variables are used as parameters and can be set when calling the docker image:

 - `TASK` - can be either `parse` or `pagerank` depending on which task you want to be performed. _Default: `parse`_
 - `GEXF_INPUT` - is the gexf input file used which will be parsed when running the `parse` task. _Default: `./data/input/latest.gexf`
 - `PAGERANK_FILE` - is the input file used when calculating the recommendations through the `pagerank` task. _Default: `./data/output/recommenderdata.gexf`
 - `STORY_ID` - input story used for the pagerank 
 - `USER_ID` - input user used for the pagerank


A few examples are provided in the sections below to better clarify how to use this docker image.

#### Parse GEXF input file
Use the default GEXF input file `./data/input/latest.gexf`. `TASK=parse` can be also omitted as it is the default.
```
# The following command will use the default input GEXF file at ./data/input/latest.gexf
# TAKS=parse can be also omitted as it is the default

$ docker run -it --rm -v "$PWD/data":/usr/src/app/data -e TASK=parse commonfare/commonshare-python
```

Specify a different input file via the `GEXF_INPUT` environment variable.
```
$ docker run -it --rm -v "$PWD/data":/usr/src/app/data -e GEXF_INPUT=./data/input/input3.gexf commonfare/commonshare-python
```

#### Page Rank
Calculate recommended stories.  
> **NOTE:** at the time of writing the IDs refer to the identifiers of the _nodes_ in the gexf file and _not_ to the identifiers of users and stories in the commonfare platform.
```
$ docker run -it --rm -v "$PWD/data":/usr/src/app/data -e TASK=pagerank -e STORY_ID=7534 -e USER_ID=165 commonfare/commonshare-python
```