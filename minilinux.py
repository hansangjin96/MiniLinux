from tree import *
import win_function as f
import linux_function as linux
import save as s
import time
import platform
from collections import deque



def cur_Path(cur_Node):
    Y = cur_Node.string().split('|')
    if cur_Node.name == '/':
        Y_path = '/'.join(Y)
    else:
        Y_path = '/'.join(Y)[1:]
    return Y_path[1:-1]



def main():

    root = Node('/')
    root.timer = f._gettime()
    cur_Node = root
    mode = 0
    while(1):
        try:
            Path = cur_Path(cur_Node)
            commandline=input('os@os:~'+Path+'$ ').split()
            if commandline[0]=='exit':
                break

            elif commandline[0]=='ls':
                f._listdir(commandline, cur_Node)

            elif commandline[0]=='cd':
                if commandline[1] == '-':
                    cur_Node = root
                else:
                    cur_Node = f._change_direct(commandline, cur_Node)

            elif commandline[0]=='mkdir':
                if platform.system() == 'Windows':
                    f._makedirect(commandline, cur_Node, mode)
                if platform.system() == 'Linux':
                    linux._makedirect(commandline, cur_Node, mode)

            elif commandline[0]=='pwd':
                f._pwd(commandline, cur_Node)

            elif commandline[0]=='cat':
                f._cat(commandline, cur_Node)

            elif commandline[0]=='rm':
                if platform.system() == 'Windows':
                    f._removefile(commandline, cur_Node, mode)
                if platform.system() == 'Linux':
                    cur_Node = linux._removefile(commandline, cur_Node, mode)

            elif commandline[0]=='rmdir':
                if platform.system() == 'Windows':
                    f._removedirectory(commandline, cur_Node, mode)
                if platform.system() == 'Linux':
                    cur_Node = linux._removedirectory(commandline, cur_Node, mode)


            elif commandline[0]=='chmod':
                f._chmod(commandline, cur_Node)

            
            elif commandline[0]=='ps':
                if mode == 1:
                    mode = 0
                    if platform.system() == 'Windows':
                        print('ps mode off :: you can\'t see threads work')
                    if platform.system() == 'Linux':
                        print('ps mode off :: you can\'t see processes work')
                elif mode == 0:
                    mode = 1
                    if platform.system() == 'Windows':
                        print('ps mode on :: you can see threads work')
                    if platform.system() == 'Linux':
                        print('ps mode on :: you can see processes work')

            elif commandline[0]=='save':
                s.save(root)

            elif commandline[0]=='load':
                check = input('do you want load past linux? [Y]')
                if check.lower() == 'y' or check.lower() == 'yes':
                    stk = deque()
                    for i in range(10):
                        stk.append(deque())
                    fopen = open('test.txt', mode = 'rt')
                    file = fopen.read().split('=====\n')[:-1]
                    fopen.close()
                    length = len(file)
                    cur_node = Node('temp')
                    p_depth = 0
                    for temp in file:
                        l=temp.split('\n')[:-1]
                        if cur_node.name != '/':
                            past_node = cur_node
                        cur_return=s.makenode(l,stk)
                        cur_depth = int(cur_return[0])
                        cur_node = cur_return[1]
                        if cur_depth == 0:
                            root = stk[0].popleft()
                        if cur_depth != p_depth and cur_depth != 0:
                            p_depth = cur_depth
                            cur_node.parent = stk[cur_depth-1].popleft()

                        elif cur_depth == p_depth and cur_depth != 0:
                            cur_node.parent = stk[cur_depth-1].popleft()


                    cur_Node = root



            else:
                print('wrong command')

        except IndexError:
            index= 'for no command'














if __name__ == "__main__":
        main()
