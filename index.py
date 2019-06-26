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

def pickNodeFields( node, aspects ):
  hasOBONamespace_pred = "http://www.geneontology.org/formats/oboInOwl#hasOBONamespace"
  id = node['id']

  if 'type' not in node or node['type'] != "CLASS" or 'meta' not in node or 'lbl' not in node: return
  
  meta = node['meta']
  lbl = node['lbl']
  
  if 'basicPropertyValues' not in meta: return
  
  basicPropertyValues = meta['basicPropertyValues']
  for propertyDict in basicPropertyValues:
    if propertyDict['pred'] in hasOBONamespace_pred:
      aspect = propertyDict['val']
      if aspect in aspects: 
        return {
          'id': id,
          'label': lbl,
          'aspect': aspect 
        }

def categorizeByAspect( nodes, aspects=['cellular_component', 'biological_process'] ):
  output={
    'biological_process': [],
    'cellular_component': []
  }
  for node in nodes:
    fields = pickNodeFields( node, aspects )
    if fields:
      output[fields['aspect']].append( fields )
      # print( 'aspect: {aspect}\nlabel: {label}'.format(aspect=fields['aspect'], label=fields['label']) )
  return output


def dictToCSVFile( dataDict ):
  keys = dataDict.keys()
  for key in keys:
    csv_file = key + '.csv'
    dataList = dataDict[key]
    fieldnames = ['label', 'id'] 
    try:
      with open(csv_file, 'w') as csvfile:
          writer = csv.DictWriter(csvfile, fieldnames=fieldnames )
          writer.writeheader()
          for data in dataList:
            pickedData = { picked: data[picked] for picked in fieldnames }
            writer.writerow( pickedData )
    except IOError:
      print("I/O error") 

def main():
  nodes = getNodes()
  categorized = categorizeByAspect( nodes )
  # jsonData = json.dumps(categorized)
  dictToCSVFile( categorized )
  
main()

