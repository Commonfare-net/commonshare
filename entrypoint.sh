#!/bin/sh

# get the task to run from the env variable
# passed to docker
if [ "$TASK" = "parse" ]
then
  python parsegexf.py $GEXF_INPUT
elif [ "$TASK" = "pagerank" ]
then
  python pagerank.py $PAGERANK_FILE $STORY_ID $USER_ID
else
  echo "ERROR - Unknown task"
  exit 1
fi
