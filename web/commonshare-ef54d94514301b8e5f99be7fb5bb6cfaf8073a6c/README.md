# commonshare
Python scripts for simulating Commonfare data, calculating commonshare, and visualisation

Requirements:
NetworkX 2.1 (and the random names generator for running the simulation). Install with the following commands:
pip install networkx==2.1
pip install names

Contents:
json/...
Contains JSON output files to be used by the D3.js visualisation

gexf/...
Contains the GEXF graph files generated by the Python simulation

python/

- config.py: Contains key constants used in the simulation. Values in here can be adjusted to determine how many users are generated, the number of actions per day, and how many days the simulation runs for. It now also contains constants to allow adjustment of collusion detection.

- dynetworkx.py: Contains adjusted core_number method from the 'core.py' file of NetworkX. Additional methods have been implemented to calculate the weighted, directed core number values at particular points in time. Also contains an implemented collusion detection algorithm. 

- graphclasses.py: Base classes that represent nodes (currently users and stories)

- kcore.py: Uses the methods in dynetworkx.py to calculate the core number of graph nodes for each month of the simulated year, write these back into the GEXF, and finally, output as JSON files. It also contains a method to visualize this data in Plotly. 

- phrases.py: Generates story 'names' by picking four random words from a dictionary

- simulation.py: Main class. Run 'python simulation.py' from the Python directory to start a simulation, and call the methods in kcore.py to calculate core values and plot charts on Plotly.

- unusedmethods.py: Methods previously used for weighted k-core calculation that are no longer used.

public.html: Contains a network visualization of the simulated data. The visualised month can be toggled with a drop-down menu. Because this accesses external JSON files, it will not run locally and must be hosted on a web server. It can be seen working at:
personal.html: Will contain visualizations for an individual user's dashboard
admin.html: Will allow full access to all information for the admin dashboard

https://djr53.host.cs.st-andrews.ac.uk/commonfare/public.html