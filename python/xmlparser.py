import xml.etree.ElementTree as ET
import config as cf
import sys
import os
from datetime import datetime

if len(sys.argv) < 2:
    print 'Missing filename'
    sys.exit()
filename = sys.argv[1]
ET.register_namespace("", "http://www.gexf.net/1.2draft") 
tree = ET.parse(filename)  
namespaces={'xmlns': 'http://www.gexf.net/1.2draft'}
root = tree.getroot()

def parseLabel(edgeid,source,target,label,actionstart,actionend):
    edgevals = label.split("+")
    edgetype = edgevals[0].split("_")[0]
    
    sourcenode = nodes.find("*/[@id='" + source +"']");
    targetnode = nodes.find("*/[@id='" + target +"']");
    sourceattr = nodes.find("*/[@id='" + source +"']/*/*[@for='1']")
    targetattr = nodes.find("*/[@id='" + target +"']/*/*[@for='1']")

    sourcetype = sourceattr.attrib['value']
    targettype = targetattr.attrib['value']
    attrs = {"start":actionstart,"end":actionend}
    if sourcenode.find("spells") == None:
        spells = sourcenode.makeelement("spells",{})
        sourcenode.append(spells)
    else:
        spells = sourcenode.find("spells")
    
    spell = spells.makeelement("spell",attrs)
    spells.append(spell)
        
    if targetnode.find("spells") == None:
        spells = targetnode.makeelement("spells",{})
        targetnode.append(spells)
    else:
        spells = targetnode.find("spells")
        
    spell = spells.makeelement("spell",attrs)
    spells.append(spell)
    
    if sourcetype == "listing" or targettype == "listing":
        edgetype = edgetype+ "_listing"
    elif sourcetype == "story" or targettype == "story": 
        edgetype = edgetype+ "_story"
    elif edgetype == "tag": 
        edgetype = edgetype + "_commoner" #This is just to be clear that the tag refers to that of a commoner    
    if edgetype == "comment":
       original_comment = edges.findall("*/[@label='"+label+"']")
       print 'found ',len(original_comment)
       if len(original_comment) == 1: #This happens when a comment is received on a story but somehow the 
        return None
       for edge in original_comment:
            if edge.attrib['id'] != edgeid: #Then we've found the correct edge
                targettype = nodes.find("*/[@id='" + edge.attrib['target'] +"']/*/*[@for='1']").attrib['value']
                print targettype
                if targettype == "listing":
                    edgetype = edgetype+ "_listing"
                elif targettype == "story":
                    edgetype = edgetype+ "_story"
                break
    return attrdict[edgetype]


root[0].set('mode', 'dynamic')  
root[0].set('timeformat', 'date')  
nodeattrs = root[0].find('xmlns:attributes',namespaces)
nodes = root[0].find('xmlns:nodes',namespaces)
edges = root[0].find('xmlns:edges',namespaces)

nodeattrs.set('mode','static')
#Add the node and edge attribute values
attrib = {'class':'node','mode':'dynamic'}
dnodeattrs = root[0].makeelement('attributes',attrib)
attrib = {'class':'edge','mode':'dynamic'}
root[0].insert(1,dnodeattrs)
edgeattrs = root[0].makeelement('attributes',attrib)
root[0].insert(2,edgeattrs)
count = 5

mindate = datetime(3333,10,1)
maxdate = datetime(1,1,1)
existingedges = {}
attrdict = {}

for key in cf.interaction_keys:
    attrib = {'id':str(count),'type':'string','title':key} 
    attr = edgeattrs.makeelement('attribute',attrib)
    dnodeattrs.append(attr)
    edgeattrs.append(attr)
    attrdict[key] = str(count)
    count +=1

edgestodelete = []   
for elem in edges:  
    label = elem.attrib['label']
    edgevals = label.split("+")    
    actionstart = edgevals[1]
    actionend = edgevals[2] if len(edgevals) > 2 else actionstart
    actionstart = actionstart.split('=')[1]
    actionend = actionend.split('=')[1]
    
    parseddate = datetime.strptime(actionstart,"%Y/%m/%d")
    if mindate > parseddate:
        mindate = parseddate
    if maxdate < parseddate:
        maxdate = parseddate
    edgeid = elem.attrib['source'] + '-' + elem.attrib['target']
    altedgeid = elem.attrib['target'] + '-' + elem.attrib['source']
    if edgeid not in existingedges and altedgeid not in existingedges:
        spells = elem.makeelement('spells',{})
        elem.append(spells)
    else:
        if edgeid in existingedges:
            spells = existingedges[edgeid].find('spells')
        else:
            spells = existingedges[altedgeid].find('spells')
            
    attrib = {'start':actionstart,'end':actionend}
    spell = spells.makeelement('spell',attrib)
    spells.append(spell)
    
    sourceid = elem.attrib['source']
    targetid = elem.attrib['target']
    edgetype = parseLabel(elem.attrib['id'],sourceid,targetid,label,actionstart,actionend)
    
    if edgeid not in existingedges and altedgeid not in existingedges:
        attvalues = elem.makeelement('attvalues', {})
        elem.append(attvalues)
    else:
        if edgeid in existingedges:
            attvalues = existingedges[edgeid].find('attvalues')
        else:
            attvalues = existingedges[altedgeid].find('attvalues')
            
    #list = '[' + elem.attrib['source'] + ',' + elem.attrib['target'] + ']'
    #Here I think it's best if we store just the source node as the value of the edge
    attrib = {'value': elem.attrib['source'],'for':edgetype,'start':actionstart,'end':actionend}
    attvalue = attvalues.makeelement('attvalue',attrib)
    attvalues.append(attvalue)
    
    sourceattrs = nodes.find("*/[@id='" + sourceid +"']/*")
    targetattrs = nodes.find("*/[@id='" + targetid +"']/*")
    if edgetype != None:
        sourceattrs.append(attvalue)
        targetattrs.append(attvalue)
    #Happens when for whatever reason, only one edge exists for a particular comment
    if edgetype == None:
        print 'getting rid of ',elem.attrib['id']
        edgestodelete.append(elem)
    elif edgeid not in existingedges and altedgeid not in existingedges:
        existingedges[edgeid] = elem
    else:
        edgestodelete.append(elem)

for dupliedge in edgestodelete:
    print 'removing edge ',dupliedge.attrib['id'],' from edges'
    edges.remove(dupliedge) 
root[0].set('start',datetime.strftime(mindate,"%Y/%m/%d"))
root[0].set('end',datetime.strftime(maxdate,"%Y/%m/%d"))
filename = os.path.splitext(filename)[0]
tree.write(filename+"parsed.gexf")  

