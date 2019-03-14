import sys
import os
import csv
import re
import fileinput
import xml.etree.ElementTree as ET
from datetime import datetime
from io import StringIO
from flask import Flask,jsonify,request
from pagerank import pagerank_api

import makegraphs
import config as cf

#This is a Flask web app
app = Flask(__name__)

#Also includes Flask methods from pagerank.py
app.register_blueprint(pagerank_api)

def replace_source(nodes,edges,edgeid,label,source,target):
    '''Replace comment sender/receiver edge with story/writer edge
    
    When a commoner leaves a comment on a story, 2 edges exist:
    1) A comment sender - story edge
    2) A comment sender - comment receiver edge
    This replaces the sender-receiver with a story-receiver edge
    
    :param nodes: all nodes of the GEXF graph
    :param edges: all edges of the GEXF grpah
    :param edgeid: ID of comment sender/receiver edge in GEXF 
    :param label: label of comment sender/receiver edge in GEXF
    :param source: Source node of edge
    :param target: Target node of edge
    :returns: string edge type (comment_story or comment_listing)
    '''
    original_comment = edges.findall("*/[@label='"+label+"']")
    if len(original_comment) == 1:
        return None #If no original story-commoner edge 
           
    for edge in original_comment:
        if edge.attrib['id'] == edgeid:
            #This is the commoner-commoner edge
            commoner_commoner_edge = edge                    
        if edge.attrib['id'] != edgeid: 
            #This is the story-commoner edge
            targettype = nodes.find("*/[@id='" 
            + edge.attrib['target'] 
            + "']/*/*[@for='1']").attrib['value']
            if targettype == "listing":
                edgetype = "comment_listing"
            elif targettype == "story":
                edgetype = "comment_story"
            object_target = edge.attrib['target']
    #Replace the sender-receiver edge with a story-receiver edge
    if source != target:
        commoner_commoner_edge.set('source',object_target)

    return edgetype
        
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
    
    
def parseLabel(nodes,edges,edgeid,sourceid,targetid,label):

    """Get edge type, start and end dates from label
    
    This method:
    1) Adds edge spells to source and target nodes
    2) Finds the type, start and end date of edge from its label
    Labels have the following format:
    'conversation_13+date_start=2018/06/23+date_end=2018/06/26'
    
    :param nodes: all nodes of the GEXF graph
    :param edges: all edges of the GEXF grpah
    :param edgeid: string ID of edge in GEXF
    :param sourced: string ID of node that is source of this edge
    :param targetid: string ID of node that is target of this edge 
    :param label: string label of edge in GEXF 
    :returns: 3-tuple containing edge type, start and end date 
    """
    edgevals = label.split("+")    
    start = edgevals[1]
    end = edgevals[2] if len(edgevals) > 2 else start
    start = start.split('=')[1]
    end = end.split('=')[1]

    
    edgetype = edgevals[0].split("_")[0]

    #Ensure Basic Income transactions don't end up in node spells
    if edgetype == 'transaction' and (sourceid == '1' or targetid == '1'):
        return ('transaction',start,end)
    
    #The type of source/target node determines the type of edge
    source = nodes.find("*/[@id='" + sourceid +"']");
    target = nodes.find("*/[@id='" + targetid +"']");
    sattr = nodes.find("*/[@id='" + sourceid +"']/*/*[@for='1']")
    tattr = nodes.find("*/[@id='" + targetid +"']/*/*[@for='1']")

    sourcetype = sattr.attrib['value']
    targettype = tattr.attrib['value']
    attrs = {"start":start,"end":end}
    
    #Add spell to nodes corresponding to start/end date of this edge
    addNodeSpell(source,attrs)
    addNodeSpell(target,attrs)


    if sourcetype == "listing" or targettype == "listing":
        edgetype = edgetype+ "_listing"
    elif sourcetype == "story" or targettype == "story": 
        edgetype = edgetype+ "_story"
    elif edgetype == "tag": 
        edgetype = edgetype + "_commoner"  
    if edgetype == "comment": #'comment' edge between two commoners
        edgetype = replace_source(nodes,edges,edgeid,label,source,target)

    return (edgetype,start,end)

    
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
    newtext = '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2" xsi="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd">\n'
    x = fileinput.FileInput(filename, inplace=1)
    for line in x:
        if line.startswith("<gexf"):
            line = newtext
        elif re.search('<(\S*):',line) is not None: #Get rid of dodgy namespaces
            continue
        sys.stdout.write(line)
    x.close()
    
    tree = ET.parse(filename)  
    root = tree.getroot()

    ET.register_namespace("", "http://www.gexf.net/1.2draft") 
    namespaces={'xmlns': "http://www.gexf.net/1.2draft"}
    
    #Remove the 'meta' tag if it exists for consistency
    meta = root.find('xmlns:meta',namespaces)
    if meta is not None:
        root.remove(meta)
    graph = root.find('xmlns:graph',namespaces)
    graph.set('mode', 'dynamic')  
    graph.set('timeformat', 'date')  
    
    nodes = graph.find('xmlns:nodes',namespaces)

    if cf.ADD_VIZ_STUFF: #All this stuff is commonfare-specific
        #Get the 'static' node attributes (those unchanging over time)
        nodeattrs = graph.find('xmlns:attributes',namespaces)
        nodeattrs.set('mode','static')

        #Remove ID attribute as it is already in the GEXF
        nodeidattr = nodeattrs.find("*/[@title='id']")
        nodeid_id = None
        if nodeidattr is not None:
            nodeid_id = nodeidattr.attrib['id']
            nodeattrs.remove(nodeidattr)

        type_id = str(nodeattrs.find("*/[@title='type']").attrib['id'])
        name_id = nodeattrs.find("*/[@title='name']").attrib['id']
        title_id = nodeattrs.find("*/[@title='title']").attrib['id']


        #Make new ID attribute - the node's ID in the Commonfare platform
        attrib = {'id':'5','type':'string','title':'platform_id'} 
        attr = nodeattrs.makeelement('attribute',attrib)
        nodeattrs.append(attr)

        #For each node, remove the old ID attribute and add the platform ID
        for n in nodes:
            platform_id = n.get('label').split('_')[1]
            attvals = n.find('xmlns:attvalues',namespaces)
            
            if nodeid_id is not None:
                idattr = attvals.find("*/[@for='"+str(nodeid_id)+"']")
                attvals.remove(idattr)
            
            #Add the platform ID
            attrib = {'value': platform_id,'for':'5'}
            attvalue = attvals.makeelement('attvalue',attrib)
            attvals.append(attvalue)

            nodetype = attvals.find("*/[@for='" + type_id + "']").get('value')
            #Replace all apostrophes in story/commoner names 
            if nodetype == 'story' or nodetype == 'listing':
                nodetitle = attvals.find("*/[@for='"+str(title_id)+"']")
                nodetitle.set('value',nodetitle.get('value').replace("'",""))
            else:
                nodename = attvals.find("*/[@for='"+str(name_id)+"']")
                nodename.set('value',nodename.get('value').replace("'",""))
            
        #Add holders for dynamic node and edge attributes
        attrib = {'class':'node','mode':'dynamic'}
        dnodeattrs = graph.makeelement('attributes',attrib)
        attrib = {'class':'edge','mode':'dynamic'}
        edgeattrs = graph.makeelement('attributes',attrib)
        graph.insert(1,dnodeattrs)
        graph.insert(2,edgeattrs)
        attrib = {'id':'init','type':'string','title':'initiator'} 
        attr = edgeattrs.makeelement('attribute',attrib)
        edgeattrs.append(attr)
        #New attribute IDs start at 6 because the platform ID attribute is 5
        count = 6

        d = {}
        with open('config.txt', 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            row = spamreader.next()
            while row[0] != 'nodetypes':
                edge_type = row[0]
                edge_meta = row[1]
                in_weight = row[2]
                out_weight = row[3]
                cf.interaction_keys.append(edge_type)
                if edge_meta not in cf.meta_networks:
                    cf.meta_networks.append(edge_meta)
                cf.interaction_types[edge_type] = edge_meta
                cf.weights[edge_type] = [int(in_weight),int(out_weight)]
                print row
                row = spamreader.next()        
        #For each dynamic attribute in the config, add it to nodes and edges
        for key in cf.interaction_keys:
            attrib = {'id':str(count),'type':'string','title':key} 
            attr = edgeattrs.makeelement('attribute',attrib)
            dnodeattrs.append(attr)
            edgeattrs.append(attr)
            d[key] = str(count)
            count +=1
        d[None] = None
    else: #Generic stuff, not for commonfare data
        #First, find all existing attributes
        attributes = graph.findall('xmlns:attributes',namespaces)
        atties = []
        staticedgeattrib = None
        for x in attributes:
            if x.attrib['class'] == 'edge':# and x.attrib['mode'] == 'static':
                print 'found an edge attribute type'
                staticedgeattrib = x
                for att in x.findall('xmlns:attribute',namespaces):
                    att.attrib['type'] = 'string' #Has to be done
                    att.attrib['mode'] = 'dynamic' #I think this also has to be done
                    atties.append(att)
                #break
        if staticedgeattrib is not None:
            graph.remove(staticedgeattrib)
                
        attrib = {'class':'edge','mode':'dynamic'}
        edgeattrs = graph.makeelement('attributes',attrib)
        graph.insert(1,edgeattrs)
        attrib = {'id':'init','type':'string','title':'initiator'} 
        attr = edgeattrs.makeelement('attribute',attrib)
        edgeattrs.append(attr)
        for x in atties:
        
            edgeattrs.append(x)
        for n in nodes:
            attvalues = n.findall('xmlns:attvalues',namespaces)
            if len(attvalues) > 1: 
                for attval in attvalues[1]:
                    attvalues[0].append(attval)
                n.remove(attvalues[1])
            if len(attvalues) > 0:
                for attval in attvalues[0]:
                    updateTimestamps(attval,None)       
            spells = n.find('xmlns:spells',namespaces)
            if spells is not None:
                for spell in spells:
                    updateTimestamps(spell,None)
        
    #Here we figure out edges that need to be deleted
    edges = graph.find('xmlns:edges',namespaces)
    edgestodelete = []
    mindate = datetime(3333,10,1)
    maxdate = datetime(1,1,1)
    existingedges = {}

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
            #print 'timestamp is ',cf.stamp_to_str(float(elem.attrib['timestamp']))
            
        if cf.ADD_VIZ_STUFF:
        #Figure out what kind of edge it is based on its label        
            (e,start,end) = parseLabel(nodes,edges,edgeid,source,target,label)
            edgetype = d[e]
            parseddate = cf.to_date(start)
            if mindate > parseddate:
                mindate = parseddate
            if maxdate < parseddate:
                maxdate = parseddate
        else:
             
            attvalues = elem.findall('xmlns:attvalues',namespaces)
            if len(attvalues) > 1:
                for attval in attvalues[1]:
                    attvalues[0].append(attval)
                elem.remove(attvalues[1])
            if len(attvalues) > 0:
                for attval in attvalues[0]:
                    updateTimestamps(attval,timestamp)
                    #A lousy way of making it clear to whome the attribute belonged
                    attval.attrib['value'] = elem.attrib['source'] + "/" + attval.attrib['value']
        
        #Sometimes 'parseLabel' changes the source ID 
        source = elem.attrib['source']
        
        #Delete self-looping edges
        if source == target:
            edgestodelete.append(elem)
            continue
        
        if cf.ADD_VIZ_STUFF:
            #Delete Basic Income transactions
            if (source == '1' or target == '1') and edgetype == d['transaction']:
                edgestodelete.append(elem)
                print 'pietro',elem.attrib['id']
                continue
                
        edgeid = source + '-' + target
        altedgeid = target + '-' + source
        #Get the 'spells' and 'attvalues' of this edge, or create them
        attvalues = elem.find('xmlns:attvalues',namespaces)
        #print attvalues
        if edgeid not in existingedges and altedgeid not in existingedges:
            if elem.find('xmlns:spells') == None:
                spells = elem.makeelement('spells',{})
                elem.append(spells)
            else:
                spells = elem.find('xmlns:spells')
            if attvalues is None: 
                attvalues = elem.makeelement('attvalues', {})
                elem.append(attvalues)
                 
        else:
            oldattvalues = attvalues
            if edgeid in existingedges:
                spells = existingedges[edgeid].find('spells')
                attvalues = existingedges[edgeid].find('xmlns:attvalues')
                if attvalues == None:
                    attvalues = existingedges[edgeid].find('attvalues')
            else:
                spells = existingedges[altedgeid].find('spells')
                attvalues = existingedges[altedgeid].find('xmlns:attvalues')
                if attvalues == None:
                    attvalues = existingedges[altedgeid].find('attvalues')
            if oldattvalues != None:
                for att in oldattvalues:
                    #att.attrib['value'] = elem.attrib
                    attvalues.append(att)
                   
        #I think this needs to be done here for graphs that DON'T have a timestamp
        #but are bi-directional for whatever reason
        if edgeid not in existingedges and altedgeid not in existingedges:
            existingedges[edgeid] = elem
        else: #Remove duplicate edges
            edgestodelete.append(elem)
            
        #Dynamic data
        if cf.ADD_VIZ_STUFF == False: 
            if timestamp is not None:
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

        if cf.ADD_VIZ_STUFF == False:
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
                        
        #if edgetype != None and cf.ADD_VIZ_STUFF == True:
        #    sourceattrs.append(attvalue)
        #    targetattrs.append(attvalue)
        #elif edgetype == None and cf.ADD_VIZ_STUFF == True:
        if edgetype == None and cf.ADD_VIZ_STUFF == True:
            edgestodelete.append(elem)
            
            

    
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
        app.run(debug=True,host=os.environ.get('HTTP_HOST', '0.0.0.0'),port=int(os.environ.get('HTTP_PORT', '5000')))
    else:
        parse(sys.argv[1]);

