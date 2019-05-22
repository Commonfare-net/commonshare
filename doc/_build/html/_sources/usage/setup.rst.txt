======================
Setting up commonshare
======================

All commonshare code is available from the GitHub repository. You can download the source directly from `here <https://github.com/Commonfare-net/commonshare>`_
(make sure you have selected the branch **master**) or clone it from the command line with ``git clone https://github.com/Commonfare-net/commonshare``.
If you download it as a zip file, change the directory name from **commonshare-master** to **commonshare**.   

You will need the `latest version of Python <https://www.python.org/downloads/>`_ on your system, as well as **pip** for installing external packages (pip should come with 
the latest version of Python. For instructions on installing it manually, see `here <https://pip.pypa.io/en/stable/installing/>`_.

To install the necessary packages, run the following commands::

    pip install networkx==2.2
    pip install scipy names python-dateutil python-louvain flask
    
* `networkx <https://networkx.github.io/>`_- Python library for network analysis
* `scipy <https://www.scipy.org/>`_- Python library of scientific data analysis functions
* `names <https://pypi.org/project/names/>`_- Handy random name generator for running the network simulator 
* `python-dateutil <https://pypi.org/project/python-dateutil/>`_- Package for providing extra date/time functions
* `python-louvain <https://pypi.org/project/python-louvain/>`_- Python implementation of the Louvain community detection algorithm 
* `flask <http://flask.pocoo.org/>`_- Flask is a microframework for Python that allows its methods to be exposed through a web API 

Once these are installed, you are ready to :doc:`run commonshare <running>`