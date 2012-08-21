from django.template import Library

register = Library()

# import the logging library and get an instance of the logger
import logging
logger = logging.getLogger(__name__)

def remove_from_list(query_dict_list, value):
  """ Filter takes a list (from a query_dict) and removes the specified value
      from it if that value is in the query_dict. """
         
  temp = list(query_dict_list)
  value = str(value)
  if value in temp:
    
    # Find the index of the value and pop it off
    index = temp.index(value)
    temp.pop(index)
  
  return temp

def encode_list(query_dict_list, name):
  """ Convert a list of items into query string type format. """
  
  output = ""
  for item in query_dict_list:
    output += "{}={}&".format(name, item)
    
  return output

def remove_and_reencode(query_dict, keys):
    """ Filter that accepts a QueryDict and a comma-separated string of keys. For every key in the list
        which actually appears in the provided QueryDict, this filter removes that key
        and returns the results of re-encoding the url based on the changed query_dict, without the keys.
        The original query_dict is not modified. 
        
        Usage: q|remove_and_urlencode:'deck,page'
    """
    
    # Turn the comma-separated string into a list of keys
    key_list = keys.rsplit(',')
    temp = query_dict.copy()    
    
    for key in key_list:
        if key in query_dict:
            del temp[key]
            
    return temp.urlencode()
  
register.filter(remove_and_reencode)
register.filter(remove_from_list)
register.filter(encode_list)