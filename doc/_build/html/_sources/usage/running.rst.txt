===================
Running commonshare
===================
This section describes how to generate commonshare values for data of different types. Note that these all assume you are running from the command line.
If you are instead running commonshare within a Docker container, refer to the section on :ref:`Running from Docker`.

commonfare.net data
=================================

1. Place your GEXF file in the ``data/input`` directory.
2. On the command line, navigate to the ``python`` directory and run ``python parsegexf.py ../data/input/<YOUR_GEXF_FILENAME>``
3. When this is completed, the following will appear in the ``data/output`` directory:

    a. ``graphdata/`` - Contains JSON files for every two weeks of commonfare.net interactions, with commonshare values (``1.json...X.json``). Also contains an aggregated file of all interactions (``0.json``)
    b. ``userdata/x.json`` - Contains a file for every Commoner, named ``<COMMONER_ID>.json``, containing their interaction history
    c. ``recommenderdata.gexf`` - Contains a trimmed version of the original GEXF, used for generating story recommendations

The next step is :doc:`visualising the data <deployment>`

simulated data
============================

Functions are also available to simulate commonfare.net data. These can be found in the ``python/simulation`` directory. You can make use of these as follows:
 
1. Run ``python simulation.py`` from the ``python/simulation`` directory
2. This will leave the file ``simulateddata.gexf`` in the ``data/input`` directory.
3. Switch back to the parent directory and run ``python makegraphs.py ../data/input/simulateddata.gexf``

This will generate the files and folders as described above. 

You can adjust simple parameters for the simulation from ``config.py``, including the number of initial users, tags, simulation days, actions per day, and colluding users. See :doc:`here <parameters>` for information on adjusting parameters. 

other GEXF graph data
===============================
Since GEXF data from other sources does not include many of the features of commonfare.net data, functions to parse and generate
JSON from such data exist in the ``python_generic`` directory. The process is very similar to that for commonfare.net

1. Place your GEXF in the ``data/input`` directory as before.

2. From the ``python_generic`` directory, run ``python parsegexf.py ../data/input/<YOUR_GEXF_FILENAME>`` 

3. When this is completed, the following will appear in the ``data/output`` directory (note that this time they are within the ``generic`` directory):

    a. ``generic/graphdata/`` - Contains JSON files for every two weeks of commonfare.net interactions, with commonshare values (``1.json...X.json``). Also contains an aggregated file of all interactions (``0.json``)
    b. ``generic/userdata/x.json`` - Contains a file for every Commoner, named ``<COMMONER_ID>.json``, containing their interaction history

As the recommender works on the principle that there are both user and story nodes, this is not likely to be the case for generic data
so the ``recommenderdata.gexf`` file is not generated in this case. 

non-GEXF graph data
==================================
Through the use of `Gephi <https://gephi.org/>`_, graph data files in a variety of formats can be easily converted to GEXF. 
The file format must match one of `Gephi's supported formats <https://gephi.org/users/supported-graph-formats/>`_.
Simply open the file with Gephi, then navigate to ``File > Export > Graph file...`` which presents a dialogue to save the file in .gexf format. 

.. image:: geph.png
    :scale: 50 % 
    
The process is then exactly the same as above. 