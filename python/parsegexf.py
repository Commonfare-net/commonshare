import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime
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
    if node.find("spells") == None:
        spells = node.makeelement("spells",{})
        node.append(spells)
    else:
        spells = node.find("spells")
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


@app.route('/parse')
def parse(*gexffile):    

    """Entry method to begin parsing the GEXF file

    This is the method called through the Flask API to begin parsing the
    GEXF file of all commonfare.net interactions. Once the GEXF is in the
    correct format, it is passed to methods in the makegraphs.py module to
    output JSON data for visualisation purposes
    """
    if len(gexffile) == 0:
    #if gexffile is None:
        filename = os.environ['GEXF_INPUT']
    else:
        filename = gexffile[0]
        print 'filename is ',gexffile
    ET.register_namespace("", "http://www.gexf.net/1.2draft") 
    tree = ET.parse(filename)  
    namespaces={'xmlns': 'http://www.gexf.net/1.2draft'}
    root = tree.getroot()
    root[0].set('mode', 'dynamic')  
    root[0].set('timeformat', 'date')  

    #Get the 'static' node attributes (those unchanging over time)
    nodeattrs = root[0].find('xmlns:attributes',namespaces)
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

    nodes = root[0].find('xmlns:nodes',namespaces)

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
    dnodeattrs = root[0].makeelement('attributes',attrib)
    attrib = {'class':'edge','mode':'dynamic'}
    edgeattrs = root[0].makeelement('attributes',attrib)
    root[0].insert(1,dnodeattrs)
    root[0].insert(2,edgeattrs)

    #New attribute IDs start at 6 because the platform ID attribute is 5
    count = 6

    d = {}
    #For each dynamic attribute in the config, add it to both nodes and edges
    for key in cf.interaction_keys:
        attrib = {'id':str(count),'type':'string','title':key} 
        attr = edgeattrs.makeelement('attribute',attrib)
        dnodeattrs.append(attr)
        edgeattrs.append(attr)
        d[key] = str(count)
        count +=1
    d[None] = None
    #Here we figure out edges that need to be deleted
    edges = root[0].find('xmlns:edges',namespaces)
    edgestodelete = []
    mindate = datetime(3333,10,1)
    maxdate = datetime(1,1,1)
    existingedges = {}

    for elem in edges:  
        label = elem.attrib['label']
       
        source = elem.attrib['source']
        target = elem.attrib['target']
        edgeid = elem.attrib['id']

        #Figure out what kind of edge it is based on its label        
        (e,start,end) = parseLabel(nodes,edges,edgeid,source,target,label)
        edgetype = d[e]
        parseddate = cf.to_date(start)
        if mindate > parseddate:
            mindate = parseddate
        if maxdate < parseddate:
            maxdate = parseddate
        #Sometimes 'parseLabel' changes the source ID 
        source = elem.attrib['source']
        
        #Delete self-looping edges
        if source == target:
            edgestodelete.append(elem)
            continue
        
        #Delete Pietro's Basic Income transactions
        if (source == '1' or target == '1') and edgetype == d['transaction']:
            edgestodelete.append(elem)
            continue
       
        edgeid = source + '-' + target
        altedgeid = target + '-' + source
        
        #Get the 'spells' and 'attvalues' of this edge, or create them
        if edgeid not in existingedges and altedgeid not in existingedges:
            spells = elem.makeelement('spells',{})
            elem.append(spells)
            attvalues = elem.makeelement('attvalues', {})
            elem.append(attvalues)
        else:
            if edgeid in existingedges:
                spells = existingedges[edgeid].find('spells')
                attvalues = existingedges[edgeid].find('attvalues')
            else:
                spells = existingedges[altedgeid].find('spells')
                attvalues = existingedges[altedgeid].find('attvalues')
        
        #Add the 'spell' of this action (start date and end date)
        attrib = {'start':start,'end':end}
        spell = spells.makeelement('spell',attrib)
        spells.append(spell)
        
        #Store more info in the 'attvalue' - initiator of action and its type
        attrib = {'value': source+'-'+target,'for':edgetype,'start':start,'end':end}
        attvalue = attvalues.makeelement('attvalue',attrib)
        attvalues.append(attvalue)

        #Find the nodes connected by this edge and add info on the action 
        sourceattrs = nodes.find("*/[@id='" + source +"']/*")
        targetattrs = nodes.find("*/[@id='" + target +"']/*")
        if edgetype != None:
            sourceattrs.append(attvalue)
            targetattrs.append(attvalue)
     
        if edgetype == None:
            edgestodelete.append(elem)
        elif edgeid not in existingedges and altedgeid not in existingedges:
            existingedges[edgeid] = elem
        else: #Remove duplicate edges
            edgestodelete.append(elem)

    for e in edgestodelete:
        if e in edges:
            edges.remove(e) 

    #Set date of first and last interaction in root tag of GEXF file
    root[0].set('start',cf.to_str(mindate))
    root[0].set('end',cf.to_str(maxdate))
    filename = os.path.splitext(filename)[0]
    parsedfilename = filename + "parsed.gexf"
    tree.write(parsedfilename)  
    print 'done parsing'
    
    #Now make the JSON graphs for visualisation
    makegraphs.init(parsedfilename)
    
    return jsonify({'success':True})

#Run as a Flask web app
if __name__ == "__main__":
    if len(sys.argv) < 2:
        app.run(debug=True,host=os.environ.get('HTTP_HOST', '0.0.0.0'),port=int(os.environ.get('HTTP_PORT', '5000')))
    else:
        parse(sys.argv[1]);

