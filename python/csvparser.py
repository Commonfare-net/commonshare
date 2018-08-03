import networkx as nx
import dynetworkx as dx
import time
import math
import random
from datetime import datetime
from datetime import date
import config as cf
import json
import csv
from networkx.readwrite import json_graph
from collections import Counter
import os
import copy
import ast
import sys
import xml.etree.ElementTree as ET
from dateutil.relativedelta import *
import operator
G=nx.Graph()
interaction_types = {
        '8':'create_tweet',
        '2':'retweet',
        '1':'favourite',
        '4':'comment'
        }
mindate = datetime(3333,10,1)
maxdate = datetime(1,1,1)
def readFile():
    global G
    global mindate
    global maxdate
    image_creators = {}
    with open('pedagoo.csv', 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        sortedlist = sorted(csvreader, key=operator.itemgetter(2), reverse=True)
        for row in sortedlist:
            if len(row) == 0:
                break
            teacher = row[0]
            image = row[1]
            split_image = row[1].split('_')
            date_part = split_image[len(split_image)-2]
            if date_part.isdigit() == False:
                date_part = split_image[len(split_image)-1] #Sometimes happens, just to be safe
                print row[1]
            new_date = date_part[:2] + '/' + date_part[2:4] + '/' + date_part[4:]
            try:
                parseddate = datetime.strptime(new_date,"%d/%m/%y")
            except ValueError:
                print new_date
            if mindate > parseddate:
                mindate = parseddate
            if maxdate < parseddate:
                maxdate = parseddate
            if teacher not in G:
                G.add_node(teacher,type='teacher',name=str(teacher),spells=[(new_date,None)])
                for x in interaction_types:
                    G.nodes[teacher][interaction_types[x]] = []
            if image not in G:
                G.add_node(image,type='image',name=str(row[3]),spells=[(new_date,None)])
                for x in interaction_types:
                    G.nodes[image][interaction_types[x]] = []
            type = interaction_types[row[2][0]]
            if type == 'create_tweet':
                image_creators[image] = teacher
            else:
                creator = image_creators[image]
                if G.has_edge(teacher,creator) == False:
                    G.add_edge(teacher,creator)
                    for x in interaction_types:
                        G[teacher][creator][interaction_types[x]] = []
                    G[teacher][creator]['spells'] = []  
                    
                G[teacher][creator][type].append(([teacher,creator],new_date,None))
                G[teacher][creator]['spells'].append((new_date,None))
                G.nodes[teacher][type].append(([teacher,creator],new_date,None))
                G.nodes[creator][type].append(([teacher,creator],new_date,None))                    
            
            if G.has_edge(teacher,image) == False:
                G.add_edge(teacher,image)
                for x in interaction_types:
                    G[teacher][image][interaction_types[x]] = []
                G[teacher][image]['spells'] = []
                           
            G[teacher][image][type].append(([teacher,image],new_date,None))
            G[teacher][image]['spells'].append((new_date,None))
            G.nodes[teacher][type].append(([teacher,image],new_date,None))
            G.nodes[image][type].append(([teacher,image],new_date,None))

    filename = "gexf/teacherdata.gexf"
    print 'filename is ',filename
    nx.write_gexf(G, filename)            
readFile()
ET.register_namespace("", "http://www.gexf.net/1.2draft") 
tree = ET.parse("gexf/teacherdata.gexf")  
namespaces={'xmlns': 'http://www.gexf.net/1.2draft'}
root = tree.getroot()
root[0].set('start',datetime.strftime(mindate,"%d/%m/%y"))
root[0].set('end',datetime.strftime(maxdate,"%d/%m/%y"))
tree.write('gexf/pedagoodata.gexf')  