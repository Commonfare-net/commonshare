import sys
import os
import csv
import re
import fileinput
import xml.etree.ElementTree as ET
from datetime import datetime
from io import StringIO
from flask import Flask,jsonify,request

import makegraphs
import config as cf

#This is a Flask web app
app = Flask(__name__)


def addNodeSpell(node,attrs):
    """Add spell element to a node element

    :param node: string node ID to add spell to
    :param attrs: dictionary of attributes of this spell  

    """
    namespaces={'xmlns': 'http://www.gexf.net/1.2draft'}
    
    if node.find('xmlns:spells',namespaces) != None:
        spells = node.find('xmlns:spells',namespaces)        
    elif node.find('spells') != None:
        spells = node.find('spells')
    else:
        spells = node.makeelement("spells",{})
        node.append(spells)
    
    spell = spells.makeelement("spell",attrs)
    spells.append(spell)

    
def updateTimestamps(tag,timestamp):
    if 'id' in tag.attrib:
        tag.attrib['for'] = tag.attrib['id']
        del tag.attrib['id']
    if timestamp is not None:
        tag.attrib['start'] = cf.stamp_to_str(float(timestamp))
        tag.attrib['end'] = cf.stamp_to_str(float(timestamp))
        return
    if 'start' in tag.attrib:
        try:
            timestamp = float(tag.attrib['start'])
            tag.attrib['start'] = cf.stamp_to_str(timestamp)
        except ValueError as e:
            return
    if 'end' in tag.attrib:
        try:
            timestamp = float(tag.attrib['end'])                        
            tag.attrib['end'] = cf.stamp_to_str(timestamp)
        except ValueError:
            return
            
@app.route('/parse')
def parse(gexffile):    

    """Entry method to begin parsing the GEXF file

    This is the method called through the Flask API to begin parsing the
    GEXF file of all commonfare.net interactions. Once the GEXF is in the
    correct format, it is passed to methods in the makegraphs.py module to
    output JSON data for visualisation purposes
    """
    if gexffile is None:
        filename = os.environ['GEXF_INPUT']
    else:
        filename = gexffile

    #The ElementTree API has no way to grab the namespace directly
    #so this resorts to manual file IO to change it to 1.2draft
    newtext = ('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2"'+
    ' xsi="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd">\n')
    x = fileinput.FileInput(filename, inplace=1)
    for line in x:
        #Replace the initial line defining the namespaces
        if line.startswith("<gexf"):
            line = newtext
        #Remove visualisation meta-info 
        elif re.search('<(\S*):',line) is not None:
            continue
        sys.stdout.write(line)
    x.close()
    
    tree = ET.parse(filename)  
    root = tree.getroot()
    ET.register_namespace("", "http://www.gexf.net/1.2draft") 
    namespaces={'xmlns': "http://www.gexf.net/1.2draft"}
    
    #Remove the 'meta' tag, it's not necesary
    meta = root.find('xmlns:meta',namespaces)
    if meta is not None:
        root.remove(meta)
    graph = root.find('xmlns:graph',namespaces)
    graph.set('mode', 'dynamic')  
    graph.set('timeformat', 'date')  
    

    #First, find all existing attributes
    attributes = graph.findall('xmlns:attributes',namespaces)
    static_edge_attributes = []
    static_edge_parent_tag = None
    for x in attributes:
        #Then find attributes belonging to edges
        if x.attrib['class'] == 'edge':
            static_edge_parent_tag = x
            for att in x.findall('xmlns:attribute',namespaces):
                #They all need to be strings so that the initiator
                #node ID can be appended onto them later
                att.attrib['type'] = 'string'
                att.attrib['mode'] = 'dynamic'
                static_edge_attributes.append(att)
                
    #All static attributes become dynamic so remove this parent tag
    if static_edge_parent_tag is not None:
        graph.remove(static_edge_parent_tag)

    #Add a parent tag for dynamic edge attributes
    attrib = {'class':'edge','mode':'dynamic'}
    dynamic_edge_attributes = graph.makeelement('attributes',attrib)
    graph.insert(1,dynamic_edge_attributes)
    
    #First add all the old static edge attributes
    for x in static_edge_attributes:
        dynamic_edge_attributes.append(x)
        
    #Edge attribute that represents which node made an action 
    attrib = {'id':'init','type':'string','title':'initiator'} 
    attr = dynamic_edge_attributes.makeelement('attribute',attrib)
    dynamic_edge_attributes.append(attr)

    #Correct formatting of nodes
    nodes = graph.find('xmlns:nodes',namespaces)
    for n in nodes:
        attvalues = n.findall('xmlns:attvalues',namespaces)
        #Need to merge multiple sets of attvalues
        if len(attvalues) > 1: 
            for attval in attvalues[1]:
                attvalues[0].append(attval)
            n.remove(attvalues[1])
        #Convert timestamps to date strings for attvalues/spells
        if len(attvalues) > 0:
            for attval in attvalues[0]:
                updateTimestamps(attval,None)       
        spells = n.find('xmlns:spells',namespaces)
        if spells is not None:
            for spell in spells:
                updateTimestamps(spell,None)
        
    edges = graph.find('xmlns:edges',namespaces)
    edgestodelete = []
    mindate = datetime(3333,10,1)
    maxdate = datetime(1,1,1)
    existingedges = {}

    #Here finds what edges to delete
    for elem in edges:  
        edgetype = None
        if 'label' in elem.attrib:
            label = elem.attrib['label']
        if 'id' in elem.attrib:
            edgeid = elem.attrib['id']
        source = elem.attrib['source']
        target = elem.attrib['target']
        if 'timestamp' in elem.attrib:
            timestamp = elem.attrib['timestamp']
        else:
            timestamp = None
              
        #Same as with nodes - merge multiple attvalues
        attvalues = elem.findall('xmlns:attvalues',namespaces)
        if len(attvalues) > 1:
            for attval in attvalues[1]:
                attvalues[0].append(attval)
            elem.remove(attvalues[1])
        if len(attvalues) > 0:
            for attval in attvalues[0]:
                updateTimestamps(attval,timestamp)
                #Append initiator node's ID to attvalue
                attval.attrib['value'] = (elem.attrib['source'] + 
                "/" + attval.attrib['value'])

        #Delete self-looping edge and continue
        if source == target:
            edgestodelete.append(elem)
            continue
                
        edgeid = source + '-' + target
        altedgeid = target + '-' + source

        attvalues = elem.find('xmlns:attvalues',namespaces)

        #This is an edge not seen before 
        if edgeid not in existingedges and altedgeid not in existingedges:
            #Add spells and attvalues if the edge doesn't have them
            if elem.find('xmlns:spells') == None:
                spells = elem.makeelement('spells',{})
                elem.append(spells)
            else:
                spells = elem.find('xmlns:spells')
            if attvalues is None: 
                attvalues = elem.makeelement('attvalues', {})
                elem.append(attvalues)
        #This is an edge that existed in the reverse direction         
        else:
            alt_edge_attvalues = attvalues
            old_edge_id = edgeid if edgeid in existingedges else altedgeid
            spells = existingedges[old_edge_id].find('spells')
            attvalues = existingedges[old_edge_id].find('xmlns:attvalues')
            if attvalues == None:
                attvalues = existingedges[old_edge_id].find('attvalues')
            if alt_edge_attvalues != None:
                for att in alt_edge_attvalues:
                    attvalues.append(att)
                   
        if edgeid not in existingedges and altedgeid not in existingedges:
            existingedges[edgeid] = elem
        else: #Remove duplicate edges
            edgestodelete.append(elem)
            
        if timestamp is not None: #Edge contains 'timestamp' attribute
            start = timestamp
            end = timestamp
        else:
            if len(spells) > 0:
                for spell in spells:
                    updateTimestamps(spell,None)
                    parseddate = cf.to_date(spell.attrib['start'])
                    if mindate > parseddate:
                        mindate = parseddate
                    if maxdate < parseddate:
                        maxdate = parseddate
                    attrib = {'value': source,'for':'init','start':spell.attrib['start'],'end':spell.attrib['end']}           
                    attvalue = attvalues.makeelement('attvalue',attrib)
                    attvalues.append(attvalue)
                    updateTimestamps(attvalue,timestamp)    
            continue
            
        #Add the 'spell' of this action (start date and end date)
        attrib = {'start':start,'end':end}
        spell = spells.makeelement('spell',attrib)
        #updateTimestamps(spell,timestamp)
        spells.append(spell)
        
        #Store more info in the 'attvalue' - initiator of action and its type
        if edgetype is not None:
            attrib = {'value': source+'-'+target,'for':edgetype,'start':start,'end':end}           
            attvalue = attvalues.makeelement('attvalue',attrib)
            attvalues.append(attvalue)
        #else: #If we don't have different action types, we can at least store who instigated this action
        attrib = {'value': source,'for':'init','start':start,'end':end}           
        attvalue = attvalues.makeelement('attvalue',attrib)
        attvalues.append(attvalue)
        updateTimestamps(attvalue,timestamp)
            
        #Find the nodes connected by this edge and add info on the action 
        sourceattrs = nodes.find("*/[@id='" + source +"']/*")
        targetattrs = nodes.find("*/[@id='" + target +"']/*")

        updateTimestamps(spell,timestamp)
        attrs = {"start":spell.attrib['start'],"end":spell.attrib['end']}
        source = nodes.find("*/[@id='"+elem.attrib['source']+"']")
        target = nodes.find("*/[@id='"+elem.attrib['target']+"']")            
        addNodeSpell(source,attrs)
        addNodeSpell(target,attrs)
        parseddate = cf.to_date(spell.attrib['start'])
        if mindate > parseddate:
            mindate = parseddate
        if maxdate < parseddate:
            maxdate = parseddate
    
    for e in edgestodelete:
        if e in edges:
            edges.remove(e)

    #Set date of first and last interaction in root tag of GEXF file
    #If mindate or maxdate is None then this means we've got a static network
    if mindate is not None and mindate != datetime(3333,10,1):
        graph.set('start',cf.to_str(mindate))
        graph.set('end',cf.to_str(maxdate))
    filename = os.path.splitext(filename)[0]
    parsedfilename = filename + "parsed.gexf"
    tree.write(parsedfilename)  
    print 'done parsing'
    
    #Now make the JSON graphs for visualisation
    makegraphs.init(parsedfilename,'default.txt')
    
    return jsonify({'success':True})

#Run as a Flask web app
if __name__ == "__main__":
    if len(sys.argv) < 2:
        app.run(debug=True,host=os.environ.get('HTTP_HOST', '0.0.0.0'),
        port=int(os.environ.get('HTTP_PORT', '5000')))
    else:
        parse(sys.argv[1]);

