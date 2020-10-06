# -*- coding: utf-8 -*-

def load_dico(file, dico):
    with open(file, 'r') as f:
        for line in f:
            if (line[0] != '#'):
                element = (line.rstrip()).split(" = ")
                cle = element[1]
                data = eval(element[0] + "('" + element[2] + "')")
                dico.setdefault(cle, data)
                dico[cle] = data
                
def save_dico(path, **dico):
    with open(path, 'w') as f:
        for cle in dico:
            t=(str(type(dico[cle]))).split("'")
            line= t[1] + ' = ' + cle + ' = ' + str(dico[cle])
            print(line, file=f)