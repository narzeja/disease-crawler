import re
from numpy import array

def parseOrphaDesc() :
    """ Not gonna document a method we wont we resuing.
    
    Note that the 4 returned lists are in same order and might 
    contain None-values if no information was found on particular 
    entries.
    """
    
    path = "OrphanetData/OrphanetProduct4_descript.Txt"
    
    data = array(re.split('\t',open(path).read()))
    
    # First split of the data:
    #   0: Orpha number
    #   1: Disease name
    #   2: Abstract + table name
    arr_len = len(data)
    orpha_nums       = data[range(4,arr_len,3)]
    disease_names    = data[range(5,arr_len,3)]
    abstracts        = data[range(6,arr_len,3)]
    
    # Remove the table name ('PatRes')
    abstracts = [x.split('\n')[0] for x in abstracts]
    
    # Second split of the data:
    #   3: Author
    authors = []
    new_abstracts = []
    for abstract in abstracts:
        m = re.search(r'(\*Authors?:)(.*)(\*)',abstract)
        if m:
            authors.append(m.group(2))
            new_abstracts.append(abstract[:m.start()]+abstract[m.end():])
        else:
            authors.append(None)
            new_abstracts.append(abstract)
    abstracts = new_abstracts
    
    return orpha_nums, disease_names, abstracts, authors
