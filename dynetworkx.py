import math
import config as cf
from datetime import datetime

def check_collusion(G,n1,n2,n2_weight,starttime,endtime):
    if G.has_edge(n1,n2) == False:
        return False
    edge = G[n1][n2]
    edgeweight = 0
    frequency = 0
    for action_key in cf.interaction_keys:
        for action in edge[action_key]:
            if (starttime < datetime.strptime(action[1],"%d/%m/%y") < endtime) or (starttime < datetime.strptime(action[2],"%d/%m/%y") < endtime):
                #print 'node_id is',node_id,'and createactions[0] is',createactions[0]
                if str(action[0]) == str(n1):
                    edgeweight = edgeweight + cf.weights[action_key][0]
                    frequency = frequency + 1
    #print 'freq',n1,'-',n2,'=',frequency,'and % is',((edgeweight/n2_weight)*100)
    if frequency > cf.FREQUENCY_THRESHOLD and ((edgeweight/n2_weight)*100) > cf.PERCENTAGE_THRESHOLD:
        return True
    return False

''' Not  using these ones right now
    
def nodeweight_directed_depreciating(G,node_id,starttime,endtime):
    #Here finds the weight corresponding to the interactions at the particular point in time
    edges = G.edges(node_id,data=True)
    edgeweights = []
    for (u,v,c) in edges:
        overallweight = 0
        for action_key in cf.interaction_keys:
            #Here instead, we need to iterate over the actions 'read', 'commented' and 'shared' and see who did them. Impact will have to be for vis purposes in Gephi only
            times_occurred = 0
            for action in c[action_key]:
                if (starttime < action[1] < endtime) or (starttime < action[2] < endtime):
                    #print 'node_id is',node_id,'and createactions[0] is',createactions[0]
                    if str(action[0]) == str(node_id):
                        #print 'yes node',node_id,'created this'
                        overallweight = overallweight + (cf.weights[action_key][0]/math.pow(cf.DEPRECIATION,times_occurred))     
                    else:
                        overallweight = overallweight + (cf.weights[action_key][1]/math.pow(cf.DEPRECIATION,times_occurred))
                    times_occurred = times_occurred + 1
        if overallweight > 0:
            edgeweights.append(int(overallweight))
    if len(edgeweights) == 0:
        return 1
    mean = sum(edgeweights)/len(edgeweights)
    #print 'weights are ',weights
    #normalize weights to mean
    norm = [(float(i)/mean)/(float(min(edgeweights))/mean) for i in edgeweights]
    #print 'sum of norm ',sum(norm)
    return sum(norm)

#A bit wordy but should work
def nodeweight_directed_ignore_indirect_links(G,node_id,starttime,endtime):
    #Here finds the weight corresponding to the interactions at the particular point in time
    edges = G.edges(node_id,data=True)
    edgeweights = []
    for (u,v,c) in edges:
        overallweight = 0
        #Check if this is a user--user edge
        if G.nodes[u]['type'] == 'user' and G.nodes[v]['type'] == 'user':
            #Then only take direct actions into account
            for action_key in cf.direct_interaction_keys:
                for action in c[action_key]:
                    if (starttime < action[1] < endtime) or (starttime < action[2] < endtime):
                        #print 'node_id is',node_id,'and createactions[0] is',createactions[0]
                        if str(action[0]) == str(node_id):
                            #print 'yes node',node_id,'created this'
                            overallweight = overallweight + (cf.weights[action_key][0])     
                        else:
                            overallweight = overallweight + (cf.weights[action_key][1])
        else:
            for action_key in cf.interaction_keys:
                #Here instead, we need to iterate over the actions 'read', 'commented' and 'shared' and see who did them. Impact will have to be for vis purposes in Gephi only
                for action in c[action_key]:
                    if (starttime < action[1] < endtime) or (starttime < action[2] < endtime):
                        #print 'node_id is',node_id,'and createactions[0] is',createactions[0]
                        if str(action[0]) == str(node_id):
                            #print 'yes node',node_id,'created this'
                            overallweight = overallweight + (cf.weights[action_key][0])     
                        else:
                            overallweight = overallweight + (cf.weights[action_key][1])
        if overallweight > 0:
            edgeweights.append(int(overallweight))
    if len(edgeweights) == 0:
        return 1
    mean = sum(edgeweights)/len(edgeweights)
    #print 'weights are ',weights
    #normalize weights to mean
    norm = [(float(i)/mean)/(float(min(edgeweights))/mean) for i in edgeweights]
    #print 'sum of norm ',sum(norm)
    return sum(norm)

'''    
#DJR modified this again to return the graph with the unnecessary bits removed        
def nodeweight_directed(G,node_id,starttime,endtime):
    #Here finds the weight corresponding to the interactions at the particular point in time
    edges = G.edges(node_id,data=True)
    edgeweights = []
    for (u,v,c) in edges:
        overallweight = 0
        for action_key in cf.interaction_keys:
            #Here instead, we need to iterate over the actions 'read', 'commented' and 'shared' and see who did them. Impact will have to be for vis purposes in Gephi only
            for action in c[action_key]:
                if (starttime < datetime.strptime(action[1],"%d/%m/%y") < endtime) or (starttime < datetime.strptime(action[2],"%d/%m/%y") < endtime):
                    #print 'node_id is',node_id,'and createactions[0] is',createactions[0]
                    if str(action[0]) == str(node_id):
                        #print 'yes node',node_id,'created this'
                        overallweight = overallweight + cf.weights[action_key][0]     
                    else:
                        overallweight = overallweight + cf.weights[action_key][1]
                else:
                    c[action_key].remove(action) #Hopefully this gets rid of it
        if overallweight > 0:
            edgeweights.append(int(overallweight))
    if len(edgeweights) == 0:
        return (G,1)
    mean = sum(edgeweights)/len(edgeweights)
    if node_id == cf.colluding_nodes[0] or node_id == cf.colluding_nodes[1]:
        print 'weights are ',edgeweights
    #normalize weights to mean
    norm = [(float(i)/mean)/(float(min(edgeweights))/mean) for i in edgeweights]
    #print 'sum of norm ',sum(norm)
    return (G,sum(norm))
'''
def nodeweight_undirected(G,node_id,starttime,endtime):
    #Here finds the weight corresponding to the interactions at the particular point in time
    edges = G.edges(node_id,data=True)
    edgeweights = []
    for (u,v,c) in edges:
        overallweight = 0
        for action_key in cf.interaction_keys:
            for action in c[action_key]:
                if (starttime < action[1] < endtime) or (starttime < action[2] < endtime):
                        overallweight = overallweight + cf.weights[action_key][0]      
            if overallweight > 0:
                edgeweights.append(int(overallweight))
    if len(edgeweights) == 0:
        return 1
    mean = sum(edgeweights)/len(edgeweights)
    #print 'weights are ',weights
    #normalize weights to mean
    norm = [(float(i)/mean)/(float(min(edgeweights))/mean) for i in edgeweights]
    #print 'sum of norm ',sum(norm)
    return sum(norm)    
'''    
#DJR Modified this method to return the modified graph for spitting out JSON
def core_number_weighted(G,starttime,endtime,directed,ignore_indirect):

    if G.is_multigraph():
        raise nx.NetworkXError(
                'MultiGraph and MultiDiGraph types not supported.')

    if G.number_of_selfloops()>0:
        raise nx.NetworkXError(
                'Input graph has self loops; the core number is not defined.',
                'Consider using G.remove_edges_from(G.selfloop_edges()).')

    if G.is_directed():
        import itertools
        def neighbors(v):
            return itertools.chain.from_iterable([G.predecessors_iter(v),
                                                  G.successors_iter(v)])
    else:
        neighbors=G.neighbors
        
    degrees=G.degree()
    nodeweights = {}
    degrees = dict(G.degree())
    if directed:
        if ignore_indirect:
            for k,v in degrees.items():
                degrees[k] = int(math.sqrt(math.ceil(int(v) * nodeweight_directed_ignore_indirect_links(G,k,starttime,endtime))))  
              
        else:
            for k,v in degrees.items():
                (G,directed_weight) = nodeweight_directed(G,k,starttime,endtime)
                degrees[k] = int(math.sqrt(math.ceil(int(v) * directed_weight)))
               # print 'directed weight of',k,'is',directed_weight
                if directed_weight > cf.REPUTATION_THRESHOLD:
                    nodeweights[k] = directed_weight
    else:
        for k,v in degrees.items():
            degrees[k] = int(math.sqrt(math.ceil(int(v) * nodeweight_undirected(G,k,starttime,endtime))))  

    activenodes = list(nodeweights.keys())
    for i in activenodes:
        for j in activenodes:
            if (i != j) and check_collusion(G,i,j,nodeweights[j],starttime,endtime) and check_collusion(G,j,i,nodeweights[i],starttime,endtime):
                print i,'and',j,'might be colluding'
                
    nodes=sorted(degrees,key=degrees.get)
    bin_boundaries=[0]
    curr_degree=0
    for i,v in enumerate(nodes):
        if degrees[v]>curr_degree:
            bin_boundaries.extend([i]*(degrees[v]-curr_degree))
            curr_degree=degrees[v]
    node_pos = dict((v,pos) for pos,v in enumerate(nodes))
    # initial guesses for core is degree
    core=degrees
    nbrs=dict((v,set(neighbors(v))) for v in G)
    for v in nodes:
        for u in nbrs[v]:
            if core[u] > core[v]:
                nbrs[u].remove(v)
                pos=node_pos[u]
                bin_start=bin_boundaries[core[u]]
                node_pos[u]=bin_start
                node_pos[nodes[bin_start]]=pos
                nodes[bin_start],nodes[pos]=nodes[pos],nodes[bin_start]
                bin_boundaries[core[u]]+=1
                core[u]-=1
    return (G,core)
    
# Copyright (C) 2013-2018 by
#
# Authors: Aric Hagberg <hagberg@lanl.gov>
#          Dan Schult <dschult@colgate.edu>
#          Pieter Swart <swart@lanl.gov>
# All rights reserved.
# BSD license.
# Based on GraphML NetworkX GraphML reader
"""Read and write graphs in GEXF format.

GEXF (Graph Exchange XML Format) is a language for describing complex
network structures, their associated data and dynamics.

This implementation does not support mixed graphs (directed and
undirected edges together).

Format
------
GEXF is an XML format.  See https://gephi.org/gexf/format/schema.html for the
specification and https://gephi.org/gexf/format/basic.html for examples.
"""
import itertools
import time

import networkx as nx
from networkx.utils import open_file, make_str
try:
    from xml.etree.cElementTree import Element, ElementTree, SubElement, tostring
except ImportError:
    try:
        from xml.etree.ElementTree import Element, ElementTree, SubElement, tostring
    except ImportError:
        pass

__all__ = ['write_gexf', 'read_gexf', 'relabel_gexf_graph', 'generate_gexf']


def write_gexf(G, path, encoding='utf-8', prettyprint=True, version='1.2draft'):
    """Write G in GEXF format to path.

    "GEXF (Graph Exchange XML Format) is a language for describing
    complex networks structures, their associated data and dynamics" [1]_.

    Node attributes are checked according to the version of the GEXF
    schemas used for parameters which are not user defined,
    e.g. visualization 'viz' [2]_. See example for usage.

    Parameters
    ----------
    G : graph
       A NetworkX graph
    path : file or string
       File or file name to write.
       File names ending in .gz or .bz2 will be compressed.
    encoding : string (optional, default: 'utf-8')
       Encoding for text data.
    prettyprint : bool (optional, default: True)
       If True use line breaks and indenting in output XML.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> nx.write_gexf(G, "test.gexf")

    # visualization data
    >>> G.nodes[0]['viz'] = {'size': 54}
    >>> G.nodes[0]['viz']['position'] = {'x' : 0, 'y' : 1}
    >>> G.nodes[0]['viz']['color'] = {'r' : 0, 'g' : 0, 'b' : 256}


    Notes
    -----
    This implementation does not support mixed graphs (directed and undirected
    edges together).

    The node id attribute is set to be the string of the node label.
    If you want to specify an id use set it as node data, e.g.
    node['a']['id']=1 to set the id of node 'a' to 1.

    References
    ----------
    .. [1] GEXF File Format, https://gephi.org/gexf/format/
    .. [2] GEXF viz schema 1.1, https://gephi.org/gexf/1.1draft/viz
    """
    writer = GEXFWriter(encoding=encoding, prettyprint=prettyprint,
                        version=version)
    writer.add_graph(G)
    writer.write(path)



def generate_gexf(G, encoding='utf-8', prettyprint=True, version='1.2draft'):
    """Generate lines of GEXF format representation of G.

    "GEXF (Graph Exchange XML Format) is a language for describing
    complex networks structures, their associated data and dynamics" [1]_.

    Parameters
    ----------
    G : graph
       A NetworkX graph
    encoding : string (optional, default: 'utf-8')
       Encoding for text data.
    prettyprint : bool (optional, default: True)
       If True use line breaks and indenting in output XML.
    version : string (default: 1.2draft)
       Version of GEFX File Format (see https://gephi.org/gexf/format/schema.html).
       Supported values: "1.1draft", "1.2draft"


    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> linefeed = chr(10) # linefeed=\n
    >>> s = linefeed.join(nx.generate_gexf(G))  # doctest: +SKIP
    >>> for line in nx.generate_gexf(G):  # doctest: +SKIP
    ...    print line

    Notes
    -----
    This implementation does not support mixed graphs (directed and undirected
    edges together).

    The node id attribute is set to be the string of the node label.
    If you want to specify an id use set it as node data, e.g.
    node['a']['id']=1 to set the id of node 'a' to 1.

    References
    ----------
    .. [1] GEXF File Format, https://gephi.org/gexf/format/
    """
    writer = GEXFWriter(encoding=encoding, prettyprint=prettyprint,
                        version=version)
    writer.add_graph(G)
    for line in str(writer).splitlines():
        yield line


def read_gexf(path, node_type=None, relabel=False, version='1.2draft'):
    print 'HELLO!?!?'
    """Read graph in GEXF format from path.

    "GEXF (Graph Exchange XML Format) is a language for describing
    complex networks structures, their associated data and dynamics" [1]_.

    Parameters
    ----------
    path : file or string
       File or file name to write.
       File names ending in .gz or .bz2 will be compressed.
    node_type: Python type (default: None)
       Convert node ids to this type if not None.
    relabel : bool (default: False)
       If True relabel the nodes to use the GEXF node "label" attribute
       instead of the node "id" attribute as the NetworkX node label.
    version : string (default: 1.2draft)
       Version of GEFX File Format (see https://gephi.org/gexf/format/schema.html).
       Supported values: "1.1draft", "1.2draft"

    Returns
    -------
    graph: NetworkX graph
        If no parallel edges are found a Graph or DiGraph is returned.
        Otherwise a MultiGraph or MultiDiGraph is returned.

    Notes
    -----
    This implementation does not support mixed graphs (directed and undirected
    edges together).

    References
    ----------
    .. [1] GEXF File Format, https://gephi.org/gexf/format/
    """
    reader = GEXFReader(node_type=node_type, version=version)
    if relabel:
        G = relabel_gexf_graph(reader(path))
    else:
        G = reader(path)
    return G



class GEXF(object):
    versions = {}
    d = {'NS_GEXF': "http://www.gexf.net/1.1draft",
         'NS_VIZ': "http://www.gexf.net/1.1draft/viz",
         'NS_XSI': "http://www.w3.org/2001/XMLSchema-instance",
         'SCHEMALOCATION': ' '.join(['http://www.gexf.net/1.1draft',
                                     'http://www.gexf.net/1.1draft/gexf.xsd']),
         'VERSION': '1.1'}
    versions['1.1draft'] = d
    d = {'NS_GEXF': "http://www.gexf.net/1.2draft",
         'NS_VIZ': "http://www.gexf.net/1.2draft/viz",
         'NS_XSI': "http://www.w3.org/2001/XMLSchema-instance",
         'SCHEMALOCATION': ' '.join(['http://www.gexf.net/1.2draft',
                                     'http://www.gexf.net/1.2draft/gexf.xsd']),
         'VERSION': '1.2'}
    versions['1.2draft'] = d

    types = [(int, "integer"),
             (float, "float"),
             (float, "double"),
             (bool, "boolean"),
             (list, "string"),
             (dict, "string")]

    try:  # Python 3.x
        blurb = chr(1245)  # just to trigger the exception
        types.extend([
            (int, "long"),
            (str, "liststring"),
            (str, "anyURI"),
            (str, "string")])
    except ValueError:  # Python 2.6+
        types.extend([
            (long, "long"),
            (str, "liststring"),
            (str, "anyURI"),
            (str, "string"),
            (unicode, "liststring"),
            (unicode, "anyURI"),
            (unicode, "string")])

    xml_type = dict(types)
    python_type = dict(reversed(a) for a in types)

    # http://www.w3.org/TR/xmlschema-2/#boolean
    convert_bool = {
        'true': True, 'false': False,
        'True': True, 'False': False,
        '0': False, 0: False,
        '1': True, 1: True
    }

    def set_version(self, version):
        d = self.versions.get(version)
        if d is None:
            raise nx.NetworkXError('Unknown GEXF version %s.' % version)
        self.NS_GEXF = d['NS_GEXF']
        self.NS_VIZ = d['NS_VIZ']
        self.NS_XSI = d['NS_XSI']
        self.SCHEMALOCATION = d['NS_XSI']
        self.VERSION = d['VERSION']
        self.version = version


class GEXFWriter(GEXF):
    # class for writing GEXF format files
    # use write_gexf() function
    def __init__(self, graph=None, encoding='utf-8', prettyprint=True,
                 version='1.2draft'):
        try:
            import xml.etree.ElementTree as ET
        except ImportError:
            raise ImportError('GEXF writer requires '
                              'xml.elementtree.ElementTree')
        self.prettyprint = prettyprint
        self.encoding = encoding
        self.set_version(version)
        self.xml = Element('gexf',
                           {'xmlns': self.NS_GEXF,
                            'xmlns:xsi': self.NS_XSI,
                            'xsi:schemaLocation': self.SCHEMALOCATION,
                            'version': self.VERSION})

        ET.register_namespace('viz', self.NS_VIZ)

        # counters for edge and attribute identifiers
        self.edge_id = itertools.count()
        self.attr_id = itertools.count()
        # default attributes are stored in dictionaries
        self.attr = {}
        self.attr['node'] = {}
        self.attr['edge'] = {}
        self.attr['node']['dynamic'] = {}
        self.attr['node']['static'] = {}
        self.attr['edge']['dynamic'] = {}
        self.attr['edge']['static'] = {}

        if graph is not None:
            self.add_graph(graph)

    def __str__(self):
        if self.prettyprint:
            self.indent(self.xml)
        s = tostring(self.xml).decode(self.encoding)
        return s

    def add_graph(self, G):
        # set graph attributes
        if G.graph.get('mode') == 'dynamic':
            mode = 'dynamic'
        else:
            mode = 'static'
        # Add a graph element to the XML
        if G.is_directed():
            default = 'directed'
        else:
            default = 'undirected'
        name = G.graph.get('name', '')
        graph_element = Element('graph', defaultedgetype=default, mode=mode,
                                name=name)
        self.graph_element = graph_element
        self.add_meta(G, graph_element)
        self.add_nodes(G, graph_element)
        self.add_edges(G, graph_element)
        self.xml.append(graph_element)

    def add_meta(self, G, graph_element):
        # add meta element with creator and date
        meta_element = Element('meta')
        SubElement(meta_element, 'creator').text = 'NetworkX {}'.format(nx.__version__)
        SubElement(meta_element, 'lastmodified').text = time.strftime('%d/%m/%Y')
        graph_element.append(meta_element)

    def add_nodes(self, G, graph_element):
        nodes_element = Element('nodes')
        for node, data in G.nodes(data=True):
            node_data = data.copy()
            node_id = make_str(node_data.pop('id', node))
            kw = {'id': node_id}
            label = make_str(node_data.pop('label', node))
            kw['label'] = label
            try:
                pid = node_data.pop('pid')
                kw['pid'] = make_str(pid)
            except KeyError:
                pass
            # add node element with attributes
            node_element = Element('node', **kw)
            # add node element and attr subelements
            default = G.graph.get('node_default', {})
            node_data = self.add_parents(node_element, node_data)
            if self.version == '1.1':
                node_data = self.add_slices(node_element, node_data)
            else:
                node_data = self.add_spells(node_element, node_data)
            node_data = self.add_viz(node_element, node_data)
            node_data = self.add_attributes('node', node_element,
                                            node_data, default)
            nodes_element.append(node_element)
        graph_element.append(nodes_element)

    def add_edges(self, G, graph_element):
        print 'OOOHAHALHE'    
        def edge_key_data(G):
            # helper function to unify multigraph and graph edge iterator
            if G.is_multigraph():
                for u, v, key, data in G.edges(data=True, keys=True):
                    edge_data = data.copy()
                    edge_data.update(key=key)
                    edge_id = edge_data.pop('id', None)
                    if edge_id is None:
                        edge_id = next(self.edge_id)
                    yield u, v, edge_id, edge_data
            else:
                for u, v, data in G.edges(data=True):
                    edge_data = data.copy()
                    edge_id = edge_data.pop('id', None)
                    if edge_id is None:
                        edge_id = next(self.edge_id)
                    yield u, v, edge_id, edge_data
        edges_element = Element('edges')
        for u, v, key, edge_data in edge_key_data(G):
            kw = {'id': make_str(key)}
            #try:
            #    edge_weight = edge_data.pop('weight')
            #    kw['weight'] = make_str(edge_weight)
            #except KeyError:
            #    pass
            try:
                edge_type = edge_data.pop('type')
                kw['type'] = make_str(edge_type)
            except KeyError:
                pass
            try:
                start = edge_data.pop('start')
                kw['start'] = make_str(start)
                self.alter_graph_mode_timeformat(start)
            except KeyError:
                pass
            try:
                end = edge_data.pop('end')
                kw['end'] = make_str(end)
                self.alter_graph_mode_timeformat(end)
            except KeyError:
                pass
            source_id = make_str(G.nodes[u].get('id', u))
            target_id = make_str(G.nodes[v].get('id', v))
            edge_element = Element('edge',
                                   source=source_id, target=target_id, **kw)
            default = G.graph.get('edge_default', {})
            if self.version == '1.1':
                edge_data = self.add_slices(edge_element, edge_data)
            else:
                edge_data = self.add_spells(edge_element, edge_data)
            edge_data = self.add_viz(edge_element, edge_data)
            edge_data = self.add_attributes('edge', edge_element,
                                            edge_data, default)
            edges_element.append(edge_element)
        graph_element.append(edges_element)

    def add_attributes(self, node_or_edge, xml_obj, data, default):
        # Add attrvalues to node or edge
        attvalues = Element('attvalues')
        if len(data) == 0:
            return data
        mode = 'static'
        for k, v in data.items():
            # rename generic multigraph key to avoid any name conflict
            if k == 'key':
                k = 'networkx_key'
            val_type = type(v)
            if isinstance(v, list):
                # dynamic data
                for val, start, end in v:
                    val_type = type(val)
                    if start is not None or end is not None:
                        mode = 'dynamic'
                        self.alter_graph_mode_timeformat(start)
                        self.alter_graph_mode_timeformat(end)
                        break
                attr_id = self.get_attr_id(make_str(k), self.xml_type[val_type],
                                           node_or_edge, default, mode)
                for val, start, end in v:
                    e = Element('attvalue')
                    e.attrib['for'] = attr_id
                    e.attrib['value'] = make_str(val)
                    if start is not None:
                        e.attrib['start'] = make_str(start)
                    if end is not None:
                        e.attrib['end'] = make_str(end)
                    attvalues.append(e)
            else:
                # static data
                mode = 'static'
                attr_id = self.get_attr_id(make_str(k), self.xml_type[val_type],
                                           node_or_edge, default, mode)
                e = Element('attvalue')
                e.attrib['for'] = attr_id
                if isinstance(v, bool):
                    e.attrib['value'] = make_str(v).lower()
                else:
                    e.attrib['value'] = make_str(v)
                attvalues.append(e)
        xml_obj.append(attvalues)
        return data

    def get_attr_id(self, title, attr_type, edge_or_node, default, mode):
        # find the id of the attribute or generate a new id
        try:
            return self.attr[edge_or_node][mode][title]
        except KeyError:
            # generate new id
            new_id = str(next(self.attr_id))
            self.attr[edge_or_node][mode][title] = new_id
            attr_kwargs = {'id': new_id, 'title': title, 'type': attr_type}
            attribute = Element('attribute', **attr_kwargs)
            # add subelement for data default value if present
            default_title = default.get(title)
            if default_title is not None:
                default_element = Element('default')
                default_element.text = make_str(default_title)
                attribute.append(default_element)
            # new insert it into the XML
            attributes_element = None
            for a in self.graph_element.findall('attributes'):
                # find existing attributes element by class and mode
                a_class = a.get('class')
                a_mode = a.get('mode', 'static')
                if a_class == edge_or_node and a_mode == mode:
                    attributes_element = a
            if attributes_element is None:
                # create new attributes element
                attr_kwargs = {'mode': mode, 'class': edge_or_node}
                attributes_element = Element('attributes', **attr_kwargs)
                self.graph_element.insert(0, attributes_element)
            attributes_element.append(attribute)
        return new_id

    def add_viz(self, element, node_data):
        viz = node_data.pop('viz', False)
        if viz:
            color = viz.get('color')
            if color is not None:
                if self.VERSION == '1.1':
                    e = Element('{%s}color' % self.NS_VIZ,
                                r=str(color.get('r')),
                                g=str(color.get('g')),
                                b=str(color.get('b')))
                else:
                    e = Element('{%s}color' % self.NS_VIZ,
                                r=str(color.get('r')),
                                g=str(color.get('g')),
                                b=str(color.get('b')),
                                a=str(color.get('a')))
                element.append(e)

            size = viz.get('size')
            if size is not None:
                e = Element('{%s}size' % self.NS_VIZ, value=str(size))
                element.append(e)

            thickness = viz.get('thickness')
            if thickness is not None:
                e = Element('{%s}thickness' % self.NS_VIZ, value=str(thickness))
                element.append(e)

            shape = viz.get('shape')
            if shape is not None:
                if shape.startswith('http'):
                    e = Element('{%s}shape' % self.NS_VIZ,
                                value='image', uri=str(shape))
                else:
                    e = Element('{%s}shape' % self.NS_VIZ, value=str(shape))
                element.append(e)

            position = viz.get('position')
            if position is not None:
                e = Element('{%s}position' % self.NS_VIZ,
                            x=str(position.get('x')),
                            y=str(position.get('y')),
                            z=str(position.get('z')))
                element.append(e)
        return node_data

    def add_parents(self, node_element, node_data):
        parents = node_data.pop('parents', False)
        if parents:
            parents_element = Element('parents')
            for p in parents:
                e = Element('parent')
                e.attrib['for'] = str(p)
                parents_element.append(e)
            node_element.append(parents_element)
        return node_data

    def add_slices(self, node_or_edge_element, node_or_edge_data):
        slices = node_or_edge_data.pop('slices', False)
        if slices:
            slices_element = Element('slices')
            for start, end in slices:
                e = Element('slice', start=str(start), end=str(end))
                slices_element.append(e)
            node_or_edge_element.append(slices_element)
        return node_or_edge_data

    def add_spells(self, node_or_edge_element, node_or_edge_data):    
        spells = node_or_edge_data.pop('spells', False)
        if spells:
            spells_element = Element('spells')
            for start, end in spells:
                e = Element('spell')
                if start is not None:
                    e.attrib['start'] = make_str(start)
                    self.alter_graph_mode_timeformat(start)
                if end is not None:
                    e.attrib['end'] = make_str(end)
                    self.alter_graph_mode_timeformat(end)
                spells_element.append(e)
            node_or_edge_element.append(spells_element)
        return node_or_edge_data

    def add_weights(self, node_or_edge_element, node_or_edge_data):
        print 'hello'
        
    def alter_graph_mode_timeformat(self, start_or_end):
        # if 'start' or 'end' appears, alter Graph mode to dynamic and set timeformat
        if self.graph_element.get('mode') == 'static':
            if start_or_end is not None:
                if isinstance(start_or_end, str):
                    timeformat = 'date'
                elif isinstance(start_or_end, float):
                    timeformat = 'double'
                elif isinstance(start_or_end, int):
                    timeformat = 'long'
                else:
                    raise nx.NetworkXError(
                        'timeformat should be of the type int, float or str')
                self.graph_element.set('timeformat', timeformat)
                self.graph_element.set('mode', 'dynamic')

    def write(self, fh):
        # Serialize graph G in GEXF to the open fh
        if self.prettyprint:
            self.indent(self.xml)
        document = ElementTree(self.xml)
        document.write(fh, encoding=self.encoding, xml_declaration=True)

    def indent(self, elem, level=0):
        # in-place prettyprint formatter
        i = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


class GEXFReader(GEXF):
    # Class to read GEXF format files
    # use read_gexf() function
    def __init__(self, node_type=None, version='1.2draft'):
        try:
            import xml.etree.ElementTree
        except ImportError:
            raise ImportError('GEXF reader requires '
                              'xml.elementtree.ElementTree.')
        self.node_type = node_type
        # assume simple graph and test for multigraph on read
        self.simple_graph = True
        self.set_version(version)

    def __call__(self, stream):
        self.xml = ElementTree(file=stream)
        g = self.xml.find('{%s}graph' % self.NS_GEXF)
        if g is not None:
            return self.make_graph(g)
        # try all the versions
        for version in self.versions:
            self.set_version(version)
            g = self.xml.find('{%s}graph' % self.NS_GEXF)
            if g is not None:
                return self.make_graph(g)
        raise nx.NetworkXError('No <graph> element in GEXF file.')

    def make_graph(self, graph_xml):
        # start with empty DiGraph or MultiDiGraph
        edgedefault = graph_xml.get('defaultedgetype', None)
        if edgedefault == 'directed':
            G = nx.MultiDiGraph()
        else:
            G = nx.MultiGraph()

        # graph attributes
        graph_name = graph_xml.get('name', '')
        if graph_name != '':
            G.graph['name'] = graph_name
        graph_start = graph_xml.get('start')
        if graph_start is not None:
            G.graph['start'] = graph_start
        graph_end = graph_xml.get('end')
        if graph_end is not None:
            G.graph['end'] = graph_end
        graph_mode = graph_xml.get('mode', '')
        if graph_mode == 'dynamic':
            G.graph['mode'] = 'dynamic'
        else:
            G.graph['mode'] = 'static'

        # timeformat
        self.timeformat = graph_xml.get('timeformat')
        if self.timeformat == 'date':
            self.timeformat = 'string'

        # node and edge attributes
        attributes_elements = graph_xml.findall('{%s}attributes' % self.NS_GEXF)
        # dictionaries to hold attributes and attribute defaults
        node_attr = {}
        node_default = {}
        edge_attr = {}
        edge_default = {}
        for a in attributes_elements:
            attr_class = a.get('class')
            if attr_class == 'node':
                na, nd = self.find_gexf_attributes(a)
                node_attr.update(na)
                node_default.update(nd)
                G.graph['node_default'] = node_default
            elif attr_class == 'edge':
                ea, ed = self.find_gexf_attributes(a)
                edge_attr.update(ea)
                edge_default.update(ed)
                G.graph['edge_default'] = edge_default
            else:
                raise  # unknown attribute class

        # Hack to handle Gephi0.7beta bug
        # add weight attribute
        ea = {'weight': {'type': 'double', 'mode': 'static', 'title': 'weight'}}
        ed = {}
        edge_attr.update(ea)
        edge_default.update(ed)
        G.graph['edge_default'] = edge_default

        # add nodes
        nodes_element = graph_xml.find('{%s}nodes' % self.NS_GEXF)
        if nodes_element is not None:
            for node_xml in nodes_element.findall('{%s}node' % self.NS_GEXF):
                self.add_node(G, node_xml, node_attr)

        # add edges
        edges_element = graph_xml.find('{%s}edges' % self.NS_GEXF)
        if edges_element is not None:
            for edge_xml in edges_element.findall('{%s}edge' % self.NS_GEXF):
                self.add_edge(G, edge_xml, edge_attr)

        # switch to Graph or DiGraph if no parallel edges were found.
        if self.simple_graph:
            if G.is_directed():
                G = nx.DiGraph(G)
            else:
                G = nx.Graph(G)
        return G

    def add_node(self, G, node_xml, node_attr, node_pid=None):
        # add a single node with attributes to the graph

        # get attributes and subattributues for node
        data = self.decode_attr_elements(node_attr, node_xml)
        data = self.add_parents(data, node_xml)  # add any parents
        if self.version == '1.1':
            data = self.add_slices(data, node_xml)  # add slices
        else:
            data = self.add_spells(data, node_xml)  # add spells
        data = self.add_viz(data, node_xml)  # add viz
        data = self.add_start_end(data, node_xml)  # add start/end

        # find the node id and cast it to the appropriate type
        node_id = node_xml.get('id')
        if self.node_type is not None:
            node_id = self.node_type(node_id)

        # every node should have a label
        node_label = node_xml.get('label')
        data['label'] = node_label

        # parent node id
        node_pid = node_xml.get('pid', node_pid)
        if node_pid is not None:
            data['pid'] = node_pid

        # check for subnodes, recursive
        subnodes = node_xml.find('{%s}nodes' % self.NS_GEXF)
        if subnodes is not None:
            for node_xml in subnodes.findall('{%s}node' % self.NS_GEXF):
                self.add_node(G, node_xml, node_attr, node_pid=node_id)

        G.add_node(node_id, **data)

    def add_start_end(self, data, xml):
        # start and end times
        ttype = self.timeformat
        node_start = xml.get('start')
        if node_start is not None:
            data['start'] = self.python_type[ttype](node_start)
        node_end = xml.get('end')
        if node_end is not None:
            data['end'] = self.python_type[ttype](node_end)
        return data

    def add_viz(self, data, node_xml):
        # add viz element for node
        viz = {}
        color = node_xml.find('{%s}color' % self.NS_VIZ)
        if color is not None:
            if self.VERSION == '1.1':
                viz['color'] = {'r': int(color.get('r')),
                                'g': int(color.get('g')),
                                'b': int(color.get('b'))}
            else:
                viz['color'] = {'r': int(color.get('r')),
                                'g': int(color.get('g')),
                                'b': int(color.get('b')),
                                'a': float(color.get('a', 1))}

        size = node_xml.find('{%s}size' % self.NS_VIZ)
        if size is not None:
            viz['size'] = float(size.get('value'))

        thickness = node_xml.find('{%s}thickness' % self.NS_VIZ)
        if thickness is not None:
            viz['thickness'] = float(thickness.get('value'))

        shape = node_xml.find('{%s}shape' % self.NS_VIZ)
        if shape is not None:
            viz['shape'] = shape.get('shape')
            if viz['shape'] == 'image':
                viz['shape'] = shape.get('uri')

        position = node_xml.find('{%s}position' % self.NS_VIZ)
        if position is not None:
            viz['position'] = {'x': float(position.get('x', 0)),
                               'y': float(position.get('y', 0)),
                               'z': float(position.get('z', 0))}

        if len(viz) > 0:
            data['viz'] = viz
        return data

    def add_parents(self, data, node_xml):
        parents_element = node_xml.find('{%s}parents' % self.NS_GEXF)
        if parents_element is not None:
            data['parents'] = []
            for p in parents_element.findall('{%s}parent' % self.NS_GEXF):
                parent = p.get('for')
                data['parents'].append(parent)
        return data

    def add_slices(self, data, node_or_edge_xml):
        slices_element = node_or_edge_xml.find('{%s}slices' % self.NS_GEXF)
        if slices_element is not None:
            data['slices'] = []
            for s in slices_element.findall('{%s}slice' % self.NS_GEXF):
                start = s.get('start')
                end = s.get('end')
                data['slices'].append((start, end))
        return data

    def add_spells(self, data, node_or_edge_xml):
        spells_element = node_or_edge_xml.find('{%s}spells' % self.NS_GEXF)
        if spells_element is not None:
            data['spells'] = []
            ttype = self.timeformat
            for s in spells_element.findall('{%s}spell' % self.NS_GEXF):
                start = self.python_type[ttype](s.get('start'))
                end = self.python_type[ttype](s.get('end'))
                data['spells'].append((start, end))
        return data
    
    #DJR 2018
    def add_weights(self, data, node_or_edge_xml):
        attr_element = node_or_edge_xml.find('{%s}attvalues' % self.NS_GEXF)
        data['weights'] = []
        ttype = self.timeformat         
        if attr_element is not None:
            # loop over <attvalue> elements
            for a in attr_element.findall('{%s}attvalue' % self.NS_GEXF):
                key = a.get('for')  # for is required
                value = a.get('value')
                if a.get('start') is not None:                
                    start = self.python_type[ttype](a.get('start'))
                    end = self.python_type[ttype](a.get('end'))
                    data['weights'].append((start,end,value))                
        return data
   
    def add_edge(self, G, edge_element, edge_attr):
        # add an edge to the graph

        # raise error if we find mixed directed and undirected edges
        edge_direction = edge_element.get('type')
        if G.is_directed() and edge_direction == 'undirected':
            raise nx.NetworkXError(
                'Undirected edge found in directed graph.')
        if (not G.is_directed()) and edge_direction == 'directed':
            raise nx.NetworkXError(
                'Directed edge found in undirected graph.')

        # Get source and target and recast type if required
        source = edge_element.get('source')
        target = edge_element.get('target')
        if self.node_type is not None:
            source = self.node_type(source)
            target = self.node_type(target)

        data = self.decode_attr_elements(edge_attr, edge_element)
        data = self.add_start_end(data, edge_element)

        if self.version == '1.1':
            data = self.add_slices(data, edge_element)  # add slices
        else:
            data = self.add_spells(data, edge_element)  # add spells
            data = self.add_weights(data, edge_element)
        # GEXF stores edge ids as an attribute
        # NetworkX uses them as keys in multigraphs
        # if networkx_key is not specified as an attribute
        edge_id = edge_element.get('id')
        if edge_id is not None:
            data['id'] = edge_id

        # check if there is a 'multigraph_key' and use that as edge_id
        multigraph_key = data.pop('networkx_key', None)
        if multigraph_key is not None:
            edge_id = multigraph_key

        #weight = edge_element.get('weight')
        #if weight is not None:
        #    data['weight'] = float(weight)

        edge_label = edge_element.get('label')
        if edge_label is not None:
            data['label'] = edge_label

        if G.has_edge(source, target):
            # seen this edge before - this is a multigraph
            self.simple_graph = False
        G.add_edge(source, target, key=edge_id, **data)
        if edge_direction == 'mutual':
            G.add_edge(target, source, key=edge_id, **data)

    def decode_attr_elements(self, gexf_keys, obj_xml):
        # Use the key information to decode the attr XML
        attr = {}
        # look for outer '<attvalues>' element
        attr_element = obj_xml.find('{%s}attvalues' % self.NS_GEXF)
        if attr_element is not None:
            # loop over <attvalue> elements
            for a in attr_element.findall('{%s}attvalue' % self.NS_GEXF):
                key = a.get('for')  # for is required
                try:  # should be in our gexf_keys dictionary
                    title = gexf_keys[key]['title']
                except KeyError:
                    raise nx.NetworkXError('No attribute defined for=%s.' % key)
                atype = gexf_keys[key]['type']
                value = a.get('value')
                if atype == 'boolean':
                    value = self.convert_bool[value]
                else:
                    value = self.python_type[atype](value)
                if gexf_keys[key]['mode'] == 'dynamic':
                    # for dynamic graphs use list of three-tuples
                    # [(value1,start1,end1), (value2,start2,end2), etc]
                    ttype = self.timeformat
                    start = self.python_type[ttype](a.get('start'))
                    end = self.python_type[ttype](a.get('end'))
                    if title in attr:
                        attr[title].append((value, start, end))
                    else:
                        attr[title] = [(value, start, end)]
                else:
                    # for static graphs just assign the value
                    attr[title] = value
        return attr

    def find_gexf_attributes(self, attributes_element):
        # Extract all the attributes and defaults
        attrs = {}
        defaults = {}
        mode = attributes_element.get('mode')
        for k in attributes_element.findall('{%s}attribute' % self.NS_GEXF):
            attr_id = k.get('id')
            title = k.get('title')
            atype = k.get('type')
            attrs[attr_id] = {'title': title, 'type': atype, 'mode': mode}
            # check for the 'default' subelement of key element and add
            default = k.find('{%s}default' % self.NS_GEXF)
            if default is not None:
                if atype == 'boolean':
                    value = self.convert_bool[default.text]
                else:
                    value = self.python_type[atype](default.text)
                defaults[title] = value
        return attrs, defaults


def relabel_gexf_graph(G):
    """Relabel graph using "label" node keyword for node label.

    Parameters
    ----------
    G : graph
       A NetworkX graph read from GEXF data

    Returns
    -------
    H : graph
      A NetworkX graph with relabed nodes

    Raises
    ------
    NetworkXError
        If node labels are missing or not unique while relabel=True.

    Notes
    -----
    This function relabels the nodes in a NetworkX graph with the
    "label" attribute.  It also handles relabeling the specific GEXF
    node attributes "parents", and "pid".
    """
    # build mapping of node labels, do some error checking
    try:
        mapping = [(u, G.nodes[u]['label']) for u in G]
    except KeyError:
        raise nx.NetworkXError('Failed to relabel nodes: '
                               'missing node labels found. '
                               'Use relabel=False.')
    x, y = zip(*mapping)
    if len(set(y)) != len(G):
        raise nx.NetworkXError('Failed to relabel nodes: '
                               'duplicate node labels found. '
                               'Use relabel=False.')
    mapping = dict(mapping)
    H = nx.relabel_nodes(G, mapping)
    # relabel attributes
    for n in G:
        m = mapping[n]
        H.nodes[m]['id'] = n
        H.nodes[m].pop('label')
        if 'pid' in H.nodes[m]:
            H.nodes[m]['pid'] = mapping[G.nodes[n]['pid']]
        if 'parents' in H.nodes[m]:
            H.nodes[m]['parents'] = [mapping[p] for p in G.nodes[n]['parents']]
    return H



# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import xml.etree.cElementTree
    except:
        raise SkipTest('xml.etree.cElementTree not available.')


# fixture for nose tests
def teardown_module(module):
    import os
    try:
        os.unlink('test.gexf')
    except:
        pass