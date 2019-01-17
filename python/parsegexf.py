import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from flask import Flask,jsonify,request
from pagerank import pagerank_api

import makegraphs
import config as cf

app = Flask(__name__)

app.register_blueprint(pagerank_api)

def replace_comment_source(edgeid,label,sourcenode,targetnode):
    '''Replace comment sender/receiver edge with story/writer edge
    
    When a commoner leaves a comment on a story, 2 edges exist:
    1) A comment sender - story edge
    2) A comment sender - comment receiver edge
    This replaces the sender-receiver with a story-receiver edge
    
    :param edgeid: ID of comment sender/receiver edge in GEXF 
    :param label: label of comment sender/receiver edge in GEXF
    :param sourcenode: Source node of edge
    :param targetnode: Target node of edge
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
    if sourcenode != targetnode:
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
    
    
def parseLabel(nodes,edgeid,source,target,label):
    """Get edge type, start and end dates from label
    
    This method:
    1) Adds edge spells to source and target nodes
    2) Finds the type, start and end date of edge from its label
    Labels have the following format:
    'conversation_13+date_start=2018/06/23+date_end=2018/06/26'

    :param edgeid: string ID of edge in GEXF
    :param source: string ID of node that is source of this edge
    :param target: string ID of node that is target of this edge 
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
    if edgetype == 'transaction' and (source=='1' or target=='1'):
        return (d['transaction'],start,end)
    
    #The type of source/target node determines the type of edge
    sourcenode = nodes.find("*/[@id='" + source +"']");
    targetnode = nodes.find("*/[@id='" + target +"']");
    sourceattr = nodes.find("*/[@id='" + source +"']/*/*[@for='1']")
    targetattr = nodes.find("*/[@id='" + target +"']/*/*[@for='1']")

    sourcetype = sourceattr.attrib['value']
    targettype = targetattr.attrib['value']
    attrs = {"start":start,"end":end}
    
    #Add spell to nodes corresponding to start/end date of this edge
    addNodeSpell(sourcenode,attrs)
    addNodeSpell(targetnode,attrs)

    if sourcetype == "listing" or targettype == "listing":
        edgetype = edgetype+ "_listing"
    elif sourcetype == "story" or targettype == "story": 
        edgetype = edgetype+ "_story"
    elif edgetype == "tag": 
        edgetype = edgetype + "_commoner"        
    if edgetype == "comment": #'comment' edge between two commoners
        edgetype = replace_comment_source(edgeid,label,sourcenode,targetnode)
            
    return (edgetype,start,end)



#if len(sys.argv) < 2:
#    print 'Missing filename'
#    sys.exit()

@app.route('/')
def hello():
    print 'this is working'
    return 'this works yo'

@app.route('/parse')
def parse():    
	filename = os.environ['GEXF_INPUT']
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

	nodetype_id = nodeattrs.find("*/[@title='type']").attrib['id']
	nodename_id = nodeattrs.find("*/[@title='name']").attrib['id']
	nodetitle_id = nodeattrs.find("*/[@title='title']").attrib['id']

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

	    nodetype = attvals.find("*/[@for='"+str(nodetype_id)+"']").get('value')
	    #Replace all apostrophes in story/commoner names 
	    if nodetype == 'story' or nodetype == 'listing':
		nodetitle = attvals.find("*/[@for='"+str(nodetype_id)+"']")
		nodetitle.set('value',nodetitle.get('value').replace("'",""))
	    else:
		nodename = attvals.find("*/[@for='"+str(nodename_id)+"']")
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
	   
	    sourceid = elem.attrib['source']
	    targetid = elem.attrib['target']
	    edgeid = elem.attrib['id']

	    #Figure out what kind of edge it is based on its label        
	    (edgeindex,start,end) = parseLabel(nodes,edgeid,sourceid,targetid,label)
	    edgetype = d[edgeindex]
	    parseddate = cf.to_date(start)
	    if mindate > parseddate:
		mindate = parseddate
	    if maxdate < parseddate:
		maxdate = parseddate
	    #Sometimes 'parseLabel' changes the source ID 
	    sourceid = elem.attrib['source']
	    
	    #Delete self-looping edges
	    if sourceid == targetid:
		edgestodelete.append(elem)
		continue
	    
	    #Delete Pietro's Basic Income transactions
	    if (sourceid == '1' or targetid == '1') and edgetype == d['transaction']:
		edgestodelete.append(elem)
		continue
	   
	    #Can't use sourceid as sometimes 
	    edgeid = sourceid + '-' + targetid
	    altedgeid = targetid + '-' + sourceid
	    
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
	    attrib = {'value': sourceid,'for':edgetype,'start':start,'end':end}
	    attvalue = attvalues.makeelement('attvalue',attrib)
	    attvalues.append(attvalue)

	    #Find the nodes connected by this edge and add info on the action 
	    sourceattrs = nodes.find("*/[@id='" + sourceid +"']/*")
	    targetattrs = nodes.find("*/[@id='" + targetid +"']/*")
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
	makegraphs.init(parsedfilename)
	return jsonify({'success':True})

if __name__ == "__main__":
    app.run(debug=True,host=os.environ.get('HTTP_HOST', '0.0.0.0'),port=int(os.environ.get('HTTP_PORT', '5000')))

