from collections import namedtuple

# !WARNING!
# Because of how the ScreenEA() works place the cursor in nida to the first
#addr of the func you want to search for. 

#Bigger is not always better
depth = 10

#The function you want to see getting called
offset_you_are_targeting = "1400001121" #example

#The function you want to ingnore 
#Give the starting offset ,add them in LOWER case
offsets_to_ingnore = ["1400001121","1400001122","1400001123"] #example

offset_you_are_targeting = offset_you_are_targeting.lower()



funcs = dict()
node = namedtuple("node","next func_name prev head")

def ignore(key):
    key = key.lower()[2:-1]
    if (key not in offsets_to_ingnore):
        return False;
    return True;
        
     

def printPath(node_me,hidden_name):
    path = ""
    offset = node_me[3][2:-1]
    node_me = node_me[2]
    while (node_me[2] != 0):
        path = ("->" + node_me[1]) + "+"+ offset + path
        offset = node_me[3][2:-1]
        node_me = node_me[2]

    path = node_me[1] + "+" + offset + path
    if (len(hidden_name) > 0):
      print "Path: " + path +"->"+hidden_name
      return

    print "Path: " + path

def createTree(nodePrev, depth, function_addr):
    if (depth == 0):
        return
    function_addr = int(function_addr[:-1],16) 
    dictionary =  nodePrev[0]
    ea = function_addr 

    for (startea,endea) in Chunks(ea):
        for head in Heads(startea,endea): 
            if (GetMnem(head) == "call"):
                key = hex(GetOperandValue(head,0))
                name = str(GetFunctionName(int(key[:-1],16)))

                if (ignore(key)): continue 
                if (key.lower().find(offset_you_are_targeting) != -1 or name != ""):
                  offset = hex(head - function_addr)
                  dictionary[key] = node(dict(),name,nodePrev,offset)
                  #if (name.lower().find("malloc") != -1):  #int("0x140795111",16) == int(key[:-1],16) ): 
                  if (key.find(offset_you_are_targeting) != -1):
                    
                    printPath(dictionary[key],"__imp_maloc")
                    continue 
                  createTree(dictionary[key], depth-1, key)



newSeenFuncs = []

#GetAddress Currently diplayed on screen
ea = hex(ScreenEA()) 
name = str(GetFunctionName(int(ea[:-1],16)))
funcs[ea] = node(dict(),name,0,ea)

print "[?] Starting"
createTree(funcs[ea],depth,ea);
print "[?] Thats all no more"
