======================
Adjusting parameters
======================
From ``config.py`` in the ``python`` directory, a number of parameters can be adjusted to determine users' commonshare, as well as thresholds for collusion and
community detection. This section gives a brief overview of the parameters that can be adjusted (default values in parentheses).

* Simulation constants

  * ``DAYS`` (365) - number of simulated days of commonfare.net
  * ``TAGS`` (10) - number of tags that objects can be assigned
  * ``INITIAL_USERS`` (40) - number of users that interact during the simulation
  * ``ACTIONS_PER_DAY`` (8) - number of actions that take place on each simulated day
  * ``SHOULD_COLLUDE`` (True) - ``True`` or ``False`` to represent whether collusive activity should be simulated 
  * ``NUM_COLLUDERS`` (2) - number of users who collude together (must be less than ``INITIAL_USERS``!)

* Collusion constants

  * ``FREQUENCY_THRESHOLD`` (5) - minimum number of actions taken by a user in the time window to be a potential colluder (this prevents every single user being checked, including those with no activity)
  
  * ``PERCENTAGE_THRESHOLD`` (33) - percentage of total edge weight that each user contributes to the other to flag them as potential colluders. In the example below, each of the two colluding users receives 12/14 = 86% of their total weight from their actions with each other.
  
  .. image:: colly.png
    :scale: 40 %
    :align: center

* ``SPACING`` ('biweekly') - size of time window. Can be 'biweekly', 'weekly' or 'monthly'
* ``COMMUNITY_SIM`` (0.3) - Threshold `Jaccard similarity coefficient <https://www.statisticshowto.datasciencecentral.com/jaccard-index/>`_ for dynamic community detection. Higher thresholds yield more probable communities, but risk missing less obvious communities.
* ``INTERACTIONS`` - A dictionary mapping interactions to a list *[interaction type, source weight, target weight]* The interaction type should remain constant, but weights can be adjusted. For example, ``"create_story": ['story',3,1]`` means the interaction `create_story` is of type `story`, has a weight of 3 to its source (the creator) and 1 to its target (the story).
