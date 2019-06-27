import requests
import json
import csv
import pprint

pp = pprint.PrettyPrinter(indent=2)

def getNodes( filename = 'goslim_generic.json' ):
  GO_URL = 'http://current.geneontology.org/ontology/subsets/' + filename
  headers = {
    'Accept': 'application/json'
  }

  try:
    r = requests.get( GO_URL, headers=headers )
    response = r.json() #dict
    graph = response['graphs'][0]
    nodes = graph['nodes']
    return nodes
  except Exception as e:
    print( 'Error: {error}'.format( error=e ) )
  finally:
    print( 'HTTP Code: %s' % (r.status_code,) )


def findByKey( lst, key, val ):
  output=None
  for l in lst:
    if l[key] == val:
      output = l['val']
      break
  return output


def pickNodeFields( node, namespaces ):
  synonyms = []
  definition = ''
  id = node['id']

  if 'type' not in node or node['type'] != "CLASS": return
  if 'meta' not in node or 'lbl' not in node: return

  lbl = node['lbl']
  meta = node['meta']
  if 'basicPropertyValues' not in meta: return

  basicPropertyValues = meta['basicPropertyValues']
  namespace = findByKey( basicPropertyValues, 'pred', 'http://www.geneontology.org/formats/oboInOwl#hasOBONamespace' )
  if namespace not in namespaces: return

  if 'synonyms' in meta:
    synonyms = [ s['val'] for s in meta['synonyms'] ]
  if 'definition' in meta:
    definition = meta['definition']['val']

  return {
    'id': id,
    'definition': definition,
    'label': lbl,
    'synonyms': synonyms,
    'namespace': namespace
  }

def categorizeByNamespace( nodes, namespaces=['cellular_component', 'biological_process'] ):
  output={
    'biological_process': [],
    'cellular_component': []
  }
  for node in nodes:
    fields = pickNodeFields( node, namespaces )
    if fields:
      output[fields['namespace']].append( fields )
  return output


def dictToCSVFile( dataDict ):
  keys = dataDict.keys()
  quote = '"'
  for key in keys:
    csv_file = key + '.csv'
    dataList = dataDict[key]
    fieldnames = ['id', 'definition', 'label', 'synonyms']
    try:
      with open(csv_file, 'w') as csvfile:
          writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quotechar=quote, quoting=csv.QUOTE_MINIMAL )
          writer.writeheader()
          for data in dataList:
            pickedData = { picked: data[picked] for picked in fieldnames }
            pickedData['synonyms'] = ','.join( pickedData['synonyms'] )
            writer.writerow( pickedData )
    except IOError:
      print("I/O error")

def main():
  nodes = getNodes()
  categorized = categorizeByNamespace( nodes )
  dictToCSVFile( categorized )

main()

