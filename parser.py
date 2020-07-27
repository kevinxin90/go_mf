import networkx as nx
import obonet
import os
from collections import defaultdict

def load_data(data_folder):
    url = "http://current.geneontology.org/ontology/go-basic.obo"
    graph = obonet.read_obo(url)
    for item in graph.nodes():
        if item.startswith("GO:") and graph.nodes[item]['namespace'] == "molecular_function":
            rec = graph.nodes[item]
            rec["_id"] = item
            if rec.get("is_a"):
                rec["parents"] = [parent for parent in rec.pop("is_a") if parent.startswith("GO:")]
            if rec.get("xref"):
                xrefs = defaultdict(set)
                for val in rec.get("xref"):
                    if ":" in val:
                        prefix, id = val.split(':', 1)
                        if prefix in ["http", "https"]:
                            continue
                        if prefix.lower() in ['biocyc', 'kegg_pathway', 'kegg_reaction', 'metacyc', 'reactome']:
                            xrefs[prefix.lower()].add(id)
                        else:
                            xrefs[prefix.lower()].add(val)
                for k, v in xrefs.items():
                    xrefs[k] = list(v)
                rec.pop("xref")
                rec["xrefs"] = dict(xrefs)
            rec["children"] = [child for child in graph.predecessors(item) if child.startswith("GO:")]
            rec["ancestors"] = [ancestor for ancestor in nx.descendants(graph, item) if ancestor.startswith("GO:")]
            rec["descendants"] = [descendant for descendant in nx.ancestors(graph,item) if descendant.startswith("GO:")]
            if rec.get("created_by"):
                rec.pop("created_by")
            if rec.get("creation_date"):
                rec.pop("creation_date")
            if rec.get("relationship"):
                for rel in rec.get("relationship"):
                    predicate, val = rel.split(' ')
                    prefix = val.split(':')[0]
                    rec[predicate] = {prefix.lower(): val}
                rec.pop("relationship")
            yield rec
