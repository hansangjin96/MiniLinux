from tree import *
from win_semaph import *
import minilinux as t
import time
import threading
import logging



def _listdir(commandline, cur_Node):
    option = ['-al']
    if len(commandline) >= 2:
        if commandline[-1] in option:
            for child in cur_Node.children:
                print(child.id+child.getmode()+' '+'%6d'%child.getsize()+' '+child.timer+' '+child.name)
        else:
            print('invalid option')
    else:
        temp = []
        for child in cur_Node.children:
            temp.append(child.name)
        temp.sort()
        for i in temp:
            print(i,end='   ')
        print()




def _change_direct(commandline, cur_Node):
    if commandline[1] == '..':
        return cur_Node.parent

    for tempNode in cur_Node.children:
        if tempNode.name == commandline[1] and tempNode.id == 'd':
            return tempNode
    print('cd: '+ commandline[-1] + ': No such file or directory')
    return cur_Node



def _makedirect(commandline, cur_Node, mode):
    pool = ThreadPool(mode)
    sema = threading.Semaphore(3)

    for temp in commandline[1:]:
        tempexist = 0
        for child in cur_Node.children:
            if child.name == temp:
                tempexist = 1

        if tempexist == 1:
            print('mkdir: '+temp+': such directory of filename already exist')
        else:
            t = threading.Thread(target=_mkdir, name='th_mkdir: '+str(temp), args=(sema, pool,temp,cur_Node))

            t.start()

    time.sleep(0.1*len(commandline)+0.2)

def _mkdir(sema,pool,temp,cur_Node):
    with sema:
        if pool.mode == 1:
            logging.debug('Waiting to join the pool')
        name = threading.currentThread().getName()
        pool.makeActive(name)

        node = Node(temp, parent=cur_Node)
        node.timer = _gettime()
        time.sleep(0.1)
        pool.makeInactive(name)


def _pwd(commandline, cur_Node):
    print(t.cur_Path(cur_Node))

def _cat(commandline, cur_Node):
    if '>' in commandline:
        _catmake(commandline,cur_Node)

    elif '>>' in commandline:
        _catmerge(commandline,cur_Node)

    else:
        if commandline[1] == '-n':
            catmode = 'n'
            for temp in commandline[2:]:
                _catprint(temp,cur_Node,catmode)
        elif commandline[1] == '-e':
            catmode = 'e'
            for temp in commandline[2:]:
                _catprint(temp,cur_Node,catmode)
        else:
            catmode = 'z'
            for temp in commandline[1:]:
                _catprint(temp,cur_Node,catmode)


def _catmake(commandline, cur_Node):
    if commandline[1] == '>':
        for child in cur_Node.children:
            if child.name == commandline[-1] and child.id == '-':
                if child.getmode()[1] == 'w':
                    cur_Node.children.remove(child)
                elif child.getmode()[1] == '-':
                    print('file :'+commandline[-1]+' ::do not have write permissions.')
                    return


        tempNode = Node(commandline[2],parent = cur_Node)
        templine = []
        while(1):
            try:
                templine = input()
                if templine == '\x04':
                    tempNode.timer = _gettime()
                    tempNode.id = '-'
                    tempNode.mode = 644
                    break
                else:
                    tempNode.txt.append(templine)
            except EOFError:
                tempNode.timer = _gettime()
                tempNode.id = '-'
                tempNode.mode = 644
                break
            except KeyboardInterrupt:
                tempNode.timer = _gettime()
                tempNode.id = '-'
                tempNode.mode = 644
                break
    else:
        for child in cur_Node.children:
            if child.name == commandline[1]:
                if child.getmode()[0] == '-':
                    print('file :'+child.name+' ::do not have read permissions.')
                    return
            if child.name == commandline[-1] and child.id == '-':
                if child.getmode()[1] == 'w':
                    cur_Node.children.remove(child)
                elif child.getmode()[1] == '-':
                    print('file :'+commandline[-1]+' ::do not have write permissions.')
                    return

        tempNode = Node(commandline[-1],parent=cur_Node)
        tempNode.timer = _gettime()
        tempNode.id = '-'
        tempNode.mode = 644
        for temp in commandline[1:-2]:
            _catpaste(temp,tempNode,cur_Node)

def _catpaste(temp,tempNode,cur_Node):
    tempexist = 0
    temptxt = []
    for child in cur_Node.children:
        if child.name == temp and tempNode.name != temp:
            temptxt = child.txt
            tempexist = 1
    if tempexist == 0:
        print('cat: '+temp+': such file no exist')
        for child in cur_Node.children:
            if child.name == tempNode.name and child.id == '-':
                cur_Node.children.remove(child)
    else:
        tempNode.txt.extend(temptxt)


def _catmerge(commandline, cur_Node):
    if len(commandline)>4:
        print('invalid command')
    else:
        for child in cur_Node.children:
            if child.name == commandline[1]:
                temp1 = child
            if child.name == commandline[-1]:
                temp2 = child
        if not temp1:
            print('file'+commandline[1]+'not exist')
        elif not temp2:
            print('file'+commandline[-1]+'not exist')
        else:
            if temp1.getmode()[0] == 'r':
                if temp2.getmode()[1] == 'w':
                    temp2.txt.extend(temp1.txt)
                    temp2.timer = _gettime()
                elif temp2.getmode()[1] == '-':
                    print('file :'+temp2.name+' ::do not have write permissions.')
                    return
            else:
                print('file :'+temp1.name+' ::do not have read permissions.')



def _catprint(temp, cur_Node, catmode):
    tempexist = 0
    count = 0
    for child in cur_Node.children:
        if child.name == temp:
            if child.getmode()[0] == 'r':
                if catmode == 'n':
                    for text in child.txt:
                        print(str(count)+' '+text)
                        count = count+1
                elif catmode == 'e':
                    for text in child.txt:
                        print(text+'$')
                elif catmode == 'z':
                    for text in child.txt:
                        print(text)
            elif child.getmode()[0] == '-':
                print('file :'+temp+' ::do not have read permissions.')
                return
            tempexist = 1

    if tempexist == 0:
        print('cat: '+temp+': such file no exist')



def _removefile(commandline, cur_Node, mode):

    pool = ThreadPool(mode)
    sema = threading.Semaphore(3)
    right = 'w'
    works = 0
    if len(commandline) == 2:
        for child in cur_Node.children:
            tempexist = 0
            if child.name == commandline[1]:
                tempexist = 1
            if tempexist == 1:
                if child.getmode()[1] == '-':
                    check = input('do not have write permission. Are you sure you want to delete it? [Y]')
                    if check.lower() == 'y' or check.lower() == 'yes':
                        t = threading.Thread(target=_rmf, name='th_rmfile: '+str(commandline[1]), args=(sema, pool,commandline[1],cur_Node))
                        t.start()
                        works = 1
                    else:
                        return
                else:
                    t = threading.Thread(target=_rmf, name='th_rmfile: '+str(commandline[1]), args=(sema, pool,commandline[1],cur_Node))
                    t.start()
                    works = 1
            elif works == 0:
                print('rm: '+commandline[1]+': such file not exist')

    elif len(commandline) > 2:

        for temp in commandline[1:]:
            tempexist = 0
            for child in cur_Node.children:
                if child.name == temp:
                    right = child.getmode()[1]
                    tempexist = 1

            if tempexist == 1 and right == 'w':
                t = threading.Thread(target=_rmf, name='th_rmfile: '+str(temp), args=(sema, pool,temp,cur_Node))

                t.start()
                works = 1

            elif tempexist == 1 and right == '-':
                print('permission denied :'+temp)
            elif works == 0:
                print('rmd: '+temp+': such file not exist')
            works = 0

        time.sleep(0.1*len(commandline)+0.2)

    else:
        print('rm [filename(s)]::Enter the name of the file you want to delete.')


def _rmf(sema,pool,temp,cur_Node):
    with sema:
        if pool.mode == 1:
            logging.debug('Waiting to join the pool')
        name = threading.currentThread().getName()
        pool.makeActive(name)
        for child in cur_Node.children:
            if child.name == temp:
                cur_Node.children.remove(child)


        time.sleep(0.1)
        pool.makeInactive(name)


def _removedirectory(commandline, cur_Node, mode):
    pool = ThreadPool(mode)
    sema = threading.Semaphore(3)
    works = 0

    if len(commandline) == 2:
        for child in cur_Node.children:
            tempexist = 0
            if child.name == commandline[1]:
                tempexist = 1

            if tempexist == 1:
                if child.getmode()[1] == '-':
                    check = input(child.name+' : not have write permission. Are you sure you want to delete it? [Y]')
                    if check.lower() == 'y' or check.lower() == 'yes':
                        print(check.lower())
                        t = threading.Thread(target=_rmdir, name='th_rmdir: '+str(commandline[1]), args=(sema, pool,commandline[1],cur_Node))
                        t.start()
                        works = 1
                    else:
                        return
                else:
                    t = threading.Thread(target=_rmdir, name='th_rmdir: '+str(commandline[1]), args=(sema, pool,commandline[1],cur_Node))
                    t.start()
                    works = 1
        if works == 0:
            print('rmdir: '+commandline[1]+': such directory not exist')

    elif len(commandline) > 2:
        tempexist = 0
        for temp in commandline[1:]:
            right = 'w'
            for child in cur_Node.children:
                if child.name == temp:
                    right = child.getmode()[1]
                    tempexist = 1
            if tempexist == 1 and right == 'w':
                t = threading.Thread(target=_rmdir, name='th_rmdir: '+str(temp), args=(sema, pool,temp,cur_Node))
                t.start()
            elif right == '-':
                print('permission denied :'+temp)
            elif tempexist == 0:
                print('rmdir :'+temp+' ::such directory not exist')
            else:
                return
        time.sleep(0.1*len(commandline)+0.2)


    else:
        print('rmdir [directory(s)]::Enter the name of the directory you want to delete.')


def _rmdir(sema,pool,temp,cur_Node):
    with sema:
        if pool.mode == 1:
            logging.debug('Waiting to join the pool')
        name = threading.currentThread().getName()
        pool.makeActive(name)
        for child in cur_Node.children:
            if child.name == temp and child.id == 'd':
                cur_Node.children.remove(child)

        time.sleep(0.1)
        pool.makeInactive(name)

def _chmod(commandline,cur_Node):
    tempfind = 0
    if commandline[1] == '-c':
        for temp in cur_Node.children:
            if temp.name == commandline[3]:
                newMode = temp
                tempfind = 1
        if tempfind == 1:
            tempstring= ''
            tempstring = 'mode of '+str(newMode.name)+' changed from 0'+str(newMode.mode) + ' ('+str(newMode.getmode()) + ') to 0' + str(commandline[2])
            newMode.mode = commandline[2]
            tempstring = tempstring +' ('+str(newMode.getmode())+')'
            print(tempstring)
        else:
            print('chmod '+commandline[2]+'::such file or directory doesn\'t exist')


def _gettime():
    return time.strftime('%B %d %H:%M', time.localtime(time.time()))
