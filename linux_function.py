from tree import *
from linux_semaph import *
import win_function as w
import time
import multiprocessing
from multiprocessing import Queue
import os




def _makedirect(commandline, cur_Node, mode):
    pool = ActivePool(mode)
    jobs=[]
    works =  0
    sema = multiprocessing.Semaphore(3)
    q = Queue()


    for  temp in list(set(commandline[1:])):
        tempexist = 0
        for child in cur_Node.children:
            if child.name == temp:
                tempexist = 1

        if tempexist == 1:
            print('mkdir: '+temp+': such directory of filename already exist')
        else:
            j = multiprocessing.Process(target=_mkdir, name='mkdir: '+str(temp), args=(sema, pool, temp, cur_Node,q))
            j.start()
            jobs.append(j)
            works =1


    if works ==1:
        for j in jobs:
            j.join()
        time.sleep(0.1*len(commandline)+0.2)
        while not q.empty():
            q.get().parent = cur_Node





def _mkdir(sema,pool,temp,cur_Node,q):
    with sema:
        name = multiprocessing.current_process().name
        if pool.mode == 1:
            logging.debug('mkdir: '+temp + ' Waiting to join the pool')
        pool.makeActive(name)

        node = Node(temp)
        node.timer = w._gettime()
        q.put(node)
        if pool.mode ==1:
            print(os.getpid())
        time.sleep(0.1)
        pool.makeInactive(name)




def _removefile(commandline, cur_Node, mode):

    pool = ActivePool(mode)
    sema = multiprocessing.Semaphore(3)
    jobs=[]
    works = 0
    t = Queue()
    t.put(cur_Node)
    count = 0
    if len(commandline) == 2:
        for child in cur_Node.children:
            tempexist = 0
            if child.name == commandline[1] and child.id == '-':
                tempexist = 1
            else:
                if count == 0:
                    print('rm: '+commandline[1]+': such file not exist')
                    count = 1
            if tempexist == 1:
                if child.getmode()[1] == '-':
                    check = input('do not have write permission. Are you sure you want to delete it? [Y]')
                    if check.lower() == 'y' or check.lower() == 'yes':
                        j = multiprocessing.Process(target=_rmf, name='rmf: '+str(commandline[1]), args=(sema, pool, commandline[1], t))
                        j.start()
                        jobs.append(j)
                        works = 1
                else:
                    j = multiprocessing.Process(target=_rmf, name='rmf: '+str(commandline[1]), args=(sema, pool,commandline[1], t))
                    j.start()
                    jobs.append(j)
                    works = 1

        if works == 1:
            for j in jobs:
                j.join()
            time.sleep(0.1*len(commandline)+0.2)
            cur_Node = t.get()

        return cur_Node
    elif len(commandline) > 2:
        for temp in commandline[1:]:
            tempexist = 0
            for child in cur_Node.children:
                if child.name == temp and child.id == '-':
                    right = child.getmode()[1]
                    tempexist = 1
            if tempexist == 1 and right == 'w':
                j = multiprocessing.Process(target=_rmf, name='rmf: '+str(temp), args=(sema, pool, temp, t))
                j.start()
                jobs.append(j)
                works = 1
            elif tempexist == 1 and right == '-':
                print('permission denied :'+temp)
            else:
                print('rmdir :'+temp+' ::such directory not exist')

        if works == 1:
            for j in jobs:
                j.join()
                time.sleep(0.1*len(commandline)+0.2)
                cur_Node = t.get()

        return cur_Node



    else:
        print('rm [filename(s)]::Enter the name of the file you want to delete.')
        return cur_Node





def _rmf(sema, pool, temp, t):
    with sema:
        name = multiprocessing.current_process().name
        if pool.mode == 1:
            logging.debug('mk: '+temp + ' Waiting to join the pool')
        pool.makeActive(name)
        cur_Node = t.get()
        for child in cur_Node.children:
            if child.name == temp:
                cur_Node.children.remove(child)
        if pool.mode ==1:
            print(os.getpid())
        t.put(cur_Node)
        time.sleep(0.1)
        pool.makeInactive(name)




def _removedirectory(commandline, cur_Node, mode):
    pool = ActivePool(mode)
    sema = multiprocessing.Semaphore(3)
    jobs=[]
    works = 0
    k = Queue()
    k.put(cur_Node)


    if len(commandline) == 2:
        for child in cur_Node.children:
            tempexist = 0
            if child.name == commandline[1] and child.id == 'd':
                tempexist = 1

            if tempexist == 1:
                if child.getmode()[1] == '-':
                    check = input(child.name+' : not have write permission. Are you sure you want to delete it? [Y]')
                    if check.lower() == 'y' or check.lower() == 'yes':
                        j = multiprocessing.Process(target=_rmdir, name='rmdir: '+str(commandline[1]), args=(sema, pool, commandline[1],k))
                        j.start()
                        jobs.append(j)
                        works = 1
                    else:
                        return cur_Node
                else:
                    j = multiprocessing.Process(target=_rmdir, name='rmdir: '+str(commandline[1]), args=(sema, pool, commandline[1],k))
                    j.start()
                    jobs.append(j)
                    works = 1

        if works == 1:
            for j in jobs:
                j.join()
            time.sleep(0.1*len(commandline)+0.2)
            cur_Node = k.get()
            return cur_Node
        elif works == 0:
            print('rmdir: '+commandline[1]+': such directory not exist')
            return cur_Node


    elif len(commandline) > 2:

        for temp in commandline[1:]:
            tempexist = 0
            for child in cur_Node.children:
                if child.name == temp and child.id == 'd':
                    right = child.getmode()[1]
                    tempexist = 1
            if tempexist == 1 and right == 'w':
                j = multiprocessing.Process(target=_rmdir, name='rmdir: '+str(temp), args=(sema, pool, temp,k))
                j.start()
                jobs.append(j)
                works = 1
            elif tempexist == 1 and right == '-':
                print('permission denied :'+temp)
            else:
                print('rmdir :'+temp+' ::such directory not exist')

        if works == 1:
            for j in jobs:
                j.join()
            time.sleep(0.1*len(commandline)+0.2)

            cur_Node = k.get()



        return cur_Node

    else:
        print('rmdir [directory(s)]::Enter the name of the directory you want to delete.')
        return cur_Node


def _rmdir(sema, pool, temp,k):
    with sema:
        name = multiprocessing.current_process().name
        if pool.mode == 1:
            logging.debug('rmdir: '+temp + ' Waiting to join the pool')
        pool.makeActive(name)
        cur_Node = k.get()
        for child in cur_Node.children:
            if child.name == temp:
                cur_Node.children.remove(child)
            if pool.mode ==1:
                print(os.getpid())

        k.put(cur_Node)
        time.sleep(0.1)
        pool.makeInactive(name)
