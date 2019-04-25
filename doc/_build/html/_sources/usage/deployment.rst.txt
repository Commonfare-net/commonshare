=====================
Deploying commonshare
=====================
On commonfare.net, commonshare is deployed from within a Docker container. This section provides instructions on how to use commonshare in this way, but also how
to deploy and test it with a simple free web server, courtesy of Google's Firebase. 

(Of course, if you have your own server space, there is no requirement to use Firebase.)

Running from Firebase
----------------------
1. Sign into `Firebase <https://firebase.google.com/>`_ (you'll need a Google account) and click on the **Add project** button.
 
.. image:: fb1.png
    :scale: 40 %
    
2. Give your project a name, then click **Hosting** on the sidebar, and then **Get started** on the presented page. 

.. image:: fb2.png
    :scale: 40 %
.. image:: fb7.png
    :scale: 62 %
    
3. Follow the presented instructions. If you don't have the Node.js comand line tool installed on your system, follow the given link (or click `here <https://nodejs.org/en/>`_) to download and install it.

.. image:: fb3.png
    :scale: 40 %  
.. image:: fb4.png
    :scale: 40 %
    
4. On entering ``firebase init`` you will be presented with various options. When asked which features you want to setup, select
``Hosting: Configure and deploy Firebase Hosting sites`` using the down arrow and space bar, then press Enter.   
    
.. image:: fb5.png
    :scale: 70 % 
    
5. When asked what you want to use as your public directory, hit Enter to default to the directory ``public``.
6. When asked if you want to configure as a single-page app, enter 'N'

7. When it's finished setting up, copy the directory containing the commonshare code into the generated ``public`` directory.

8. Run ``firebase deploy``.

.. image:: fb6.png
    :scale: 70 % 
    
After a few minutes, you'll have a deployed instance of commonshare for viewing the visualisations. 

Note the ``Hosting URL`` provided on successful deployment. The main dashboard can be accessed from::

    <Hosting URL>/commonshare/html/admin_dashboard.html

From here, you can also access the individual visualisations for each Commoner, or manually from::

    <Hosting URL>/commonshare/html/personal_viz.html?userid=<ID of your user>

You can also optionally add ``&lang=it`` or ``&lang=hr`` to this URL to view the Italian or Croatian version respectively.
 
Running from Docker
--------------------
A very basic Docker image is available to run the Python scripts ``parsegexf.py`` and ``pagerank.py``, the methods of which are exposed through a simple web API, as described below.  

Input and output data is exchanged through the files in ``./data`` directory which is mounted as a volume.

.. important::
   To run from Docker, the ``GRAPHDIR`` and ``USERDIR`` directories in ``config.py`` must have the beginning of their paths changed from ``../data/output`` to ``data/output``.  

Building
^^^^^^^^^

To build this image, make sure you have `Docker <https://www.docker.com/get-started>`_ installed in your host.
If that is the case, run the following command::

    $ docker build -t commonfare/commonshare-python .

Check the Docker images available in your host machine to confirm its creation::

    $ docker images
    ...
    commonfare/commonshare-python         latest              323a3b42764f        30 minutes ago      297MB
    ...

Running
^^^^^^^^

This Docker image runs the Flask app, which exposes a simple API for running the following two Python scripts:

* ``parsegexf.py`` which takes as input a file in GEXF format and produces as output a series of files in ``./data/output/`` directory.
* ``pagerank.py`` which takes as input a story id and a user id and calculates the recommended stories for such user based on the input story.

**Parameters and environment variables**
  
The following environment variables are used as parameters and can be set when calling the docker image:

* `TASK` - can be either `parse` or `pagerank` depending on the task to be performed. (Default: `parse`)
* `GEXF_INPUT` - GEXF input file to be parsed when running the `parse` task. (Default: `./data/input/latest.gexf`)
* `PAGERANK_FILE` - GEXF output file for calculating recommendations through the `pagerank` task. (Default: `./data/output/recommenderdata.gexf`)
* `STORY_ID` - input story ID used for the `pagerank` task
* `USER_ID` - input user ID used for the `pagerank` task


Some examples are provided in the sections below to clarify how to use this Docker image.

The following command will start the service, connecting port 5000 of the Docker container (Flask default) to port 5000 of your machine::

    $ docker run -it --rm -p 5000:5000 -v "$PWD/data":/usr/src/app/data commonfare/commonshare-python

Specify a different input file via the `GEXF_INPUT` environment variable::

    $ docker run -it --rm -p 5000:5000 -v "$PWD/data":/usr/src/app/data -e GEXF_INPUT=./data/input/input3.gexf commonfare/commonshare-python


Docker compose
^^^^^^^^^^^^^^^

If you like docker-compose, you can build and run using::

    $ docker-compose build
    $ docker-compose up

Testing running status
^^^^^^^^^^^^^^^^^^^^^^^

To run parsegexf.py, use the following URL::

    #This will return a simple JSON object {success: true} on successful completion (note this takes a few minutes)
    http://127.0.0.1:5000/parse

...and to run pagerank.py::

    #This will return a JSON array of three IDs corresponding to stories that the user specified by *userid* should be recommended on reading story *storyid* If the story or user ID cannot be found, [0,0,0] will be returned instead.
    http://127.0.0.1:5000/recommend/*storyid*/*userid*

