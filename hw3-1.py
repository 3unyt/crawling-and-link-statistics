from elasticsearch import Elasticsearch
import xmltodict

"""
CS6200 Homework3.1 Practise Elasticsearch
Prerequisite: elasticsearch must be running
 * download elasticsearch from https://www.elastic.co/ and unzip
 * goto the elasticsearch folder (eg. /elasticsearch-7.10.0)
 * run 'bin/elasticsearch'
 * goto http://localhost:9200/ and you will see something like this:
    {
    "name" : "sunyutingsMBP2",
    "cluster_name" : "elasticsearch",
    "cluster_uuid" : "iCKyUAZAQ4KdZrtzJZ-zSg",
    "version" : {
        "number" : "7.10.0",
        "build_flavor" : "default",
        "build_type" : "tar",
        "build_hash" : "51e9d6f22758d0374a0f3f5c6e8f3a7997850f96",
        "build_date" : "2020-11-09T21:30:33.964949Z",
        "build_snapshot" : false,
        "lucene_version" : "8.7.0",
        "minimum_wire_compatibility_version" : "6.8.0",
        "minimum_index_compatibility_version" : "6.0.0-beta1"
    },
    "tagline" : "You Know, for Search"
    }
"""

def read_xml(file_name:str):
    """Improvement: add title to contents"""
    with open(file_name) as f:
        data_dict = xmltodict.parse(f.read())
        f.close()
    
    records = data_dict['ROOT']['RECORD']
    """
    record.keys()
    odict_keys(['PAPERNUM', 'RECORDNUM', 'MEDLINENUM', 
    'AUTHORS', 'TITLE', 'SOURCE', 'MAJORSUBJ', 'MINORSUBJ', 
    'ABSTRACT', 'REFERENCES', 'CITATIONS'])
    """

    for record in records:
        content = record['TITLE']
        content += record.get('ABSTRACT', '')
        content += record.get('EXTRACT', '')
        res = es.index(index='cfc', id=record['RECORDNUM'], body={"record":content})

    print("Finish indexing for", file_name)
    return res

def search_query(query, size):
    body = {
        "from":0,
        "size": size,
        "query": {
            "match": {
                "record":query
            }
        }
    }

    res = es.search(index="cfc", body=body)
    print("Top", size, "results for query:", query )
    for each in res['hits']['hits']:
        print(each['_id'], each['_score'])
    return res

if __name__=="__main__":
    es = Elasticsearch()

    files = ['cf74.xml','cf75.xml','cf76.xml','cf77.xml','cf78.xml','cf79.xml']
    
    if not es.indices.exists(index='cfc'):
        for f in files:
            read_xml('./cfc-xml/'+f)
        print("Index 'cfc' exists:", es.indices.exists(index='cfc'))
    else:
        print("Index 'cfc' already exists: Skip Indexing")
    
    sample_query = "Can one distinguish between the effects of mucus hypersecretion and infection on the submucosal glands of the respiratory tract in CF?"
    search_query(sample_query, 20)

    
        

