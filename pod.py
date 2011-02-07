import re
from numpy import array

def parseOrphaDesc() :
    
    path = "OrphanetData/OrphanetProduct4_descript.Txt"
    
    data = array(re.split('\t',open(path).read()))
    
    # First split of the data:
    #   0: Orpha number
    #   1: Disease name
    #   2: Abstract + Table name
    arr_len = len(data)
    orpha_nums       = data[range(4,arr_len,3)]
    disease_names    = data[range(5,arr_len,3)]
    abstracts        = data[range(6,arr_len,3)]
    
    # Remove the table name ('PatRes')
    abstracts = [x.split('\n')[0] for x in abstracts]
    
    # Second split of the data:
    #   3: Author
    #   4: Genes
    author = [re.search(r'(\*Authors?:)(.*)(\*)',a) for a in abstracts]
    
    
    author2 = [re.search(r'(\*)(.*)(\*)',a) for a in abstracts]
    a1 = [a.group(0) for a in author if a]
#    a2 = [a.group(0) for a in author2 if a]
#    print [a for a in a2 if a not in a1]
    print [a for a in a1 if len(a)>100]
#    print [x.group(0) for x in author if x]
    
    # test all arrays
    print len([x for x in orpha_nums if not x])
    print len([x for x in disease_names if not x])
    print len([x for x in abstracts if not x])
    print len([x for x in author if x])
