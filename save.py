
from tree import *


def save(node):
    f = open('test.txt', mode = 'wt',encoding='utf-8')
    for l in PreOrderIter(node):
        f.write(l.name+'\n')
        f.write(str(len(l._path)-1)+'\n')
        f.write('|'.join(l.txt)+'\n')               
        f.write(l.timer+'\n')
        f.write(str(l.mode)+'\n')
        f.write(str(l.id)+'\n')
        f.write(str(l.size)+'\n')
        f.write(str(len(l.children))+'\n')
        f.write('====='+'\n')
    f.close()
    print('save complete')


def makenode(l,stk):
    node=Node(l[0])
    if len(l[2]):
        node.txt=l[2].split('|')
    node.timer=l[3]
    node.mode=l[4]
    node.id=l[5]
    node.size=l[6]
    if node.name == '/':
        stk[int(l[1])].append(node)
    for i in range(int(l[7])):
        stk[int(l[1])].append(node)
    return [l[1], node]
