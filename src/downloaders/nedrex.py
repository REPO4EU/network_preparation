
import requests
import logging

def getEdges(iid_evidence, url):
    all_edges_reviewed_proteins = []
    upper_limit = 10000
    

    offset = 0
    
    # iid_evidence: list of evidence types to filter the edges by -> sadly, there is no documentation on the available evidence types
    
    # reviewed_proteins: setting this to True will only return edges where both proteins are reviewed
    # limit: number of edges to return, the max of this is defined in the pagination_max endpoint -> 10000
    body = {"reviewed_proteins": [True], "limit": upper_limit, "iid_evidence": iid_evidence}

    while True:
        # start with skipping no entries
        # skip: offset for pagination -> 0
        # In the body we will always adjust the skip/offset value to get the next set of edges
        body["skip"] = offset
        try:
            # POST request to the ppi endpoint with the body
            response = requests.post(
                url=f"{url}/ppi", json=body, headers={"content-type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            # collect all edges in a list
            all_edges_reviewed_proteins.extend(data)
            if len(data) < upper_limit:
                # This means that we have reached the end of the edges
                break
            # increase the offset by the upper limit to get the next set of edges
            offset += upper_limit
        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP request failed: {e}")
            return None
    return all_edges_reviewed_proteins
        
def createNedrexGraph(write_to_file=True, filename="ppi_only_reviewed_proteins.tsv", iid_evidence = ["exp"], url = "https://exbio.wzw.tum.de/repo4eu_nedrex_open/"):
    edges_review_proteins = getEdges(iid_evidence, url)
    logging.debug("Number of queried edges overall: ", len(edges_review_proteins))
    logging.debug("Example edge: ", edges_review_proteins[0])
    
    if write_to_file:
        # Optionally write the edges to a file in the format "memberOne,memberTwo" as an edge list.
        with open(filename, "w") as f:
            f.write("memberOne\tmemberTwo\tevidenceTypes\tdataSources\tmethods_score\tmethods\tsubcellularLocations\n")
            for edge in edges_review_proteins:
                f.write(str(edge["memberOne"]).lstrip(".uniprot") + "\t" + str(edge["memberTwo"]).lstrip(".uniprot") + "\t" + str(edge["evidenceTypes"]) +  "\t" + str(edge["dataSources"]) +  "\t" + str(edge["methods_score"]) +  "\t" + str(edge["methods"]) + "\t" + str(edge["subcellularLocations"]))
                f.write("\n")

def download(url, target):
    createNedrexGraph(filename=target, url=url)