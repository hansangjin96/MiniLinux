class NodeMixin(object):        #NodeMixin 부분은 따온거라 주석 부분 보고 이해만 하면 될듯 중요하지는 않음
    @property
    def parent(self):
        try:
            return self._parent
        except AttributeError:
            return None

    @parent.setter
    def parent(self, value):
        try:
            parent = self._parent
        except AttributeError:
            parent = None
        if value is None:
            # make this Node to root node
            if parent:
                # unregister at parent
                parentchildren = parent._children
                assert self in parentchildren, "Tree internal data is corrupt."
                parentchildren.remove(self)
        elif parent is not value:
            # change parent node
            if parent:
                parentchildren = parent._children
                # unregister at old parent
                assert self in parentchildren, "Tree internal data is corrupt."
                parentchildren.remove(self)
            # check for loop
            if value is self:
                msg = "Cannot set parent. %r cannot be parent of itself."
                raise LoopError(msg % self)
            if self in value.path:
                msg = "Cannot set parent. %r is parent of %r."
                raise LoopError(msg % (self, value))

            # register at new parent
            parentchildren = value._children
            assert self not in parentchildren, "Tree internal data is corrupt."
            parentchildren.append(self)
        else:
            # keep parent
            pass
        # apply
        self._parent = value

    @property
    def _children(self):
        try:
            return self.__children
        except AttributeError:
            self.__children = []
            return self.__children

    @property
    def children(self):

        return self._children

    @property
    def path(self):

        return self._path

    @property
    def _path(self):
        path = []
        node = self
        while node:
            path.insert(0, node)
            node = node.parent
        return tuple(path)

    def depth(self):

        return len(self._path) - 1


class Node(NodeMixin, object):

    def __init__(self, name, parent=None, **kwargs):

        self.name = name            #파일이름
        self.parent = parent        #부모 노드 이름
        self.txt = []               #cat에서 쓰이는 text 저장공간
        self.timer = ''              #string형태의 time 저장공간
        self.mode = 755             #기본 directory mode 755
        self.id = 'd'               #기본 directory
        self.size = self.getsize()  #기본 directory size 4096
        self.__dict__.update(kwargs)#이건 검색... 근데 쓰이지는 않은듯 삭제해도 문제 없을듯


    def string(self):               #node를 string형태로 받기 위해 만든 함수 test.py에 cur_Path 함수에 사용함
        return "%r" % "|".join([str(node.name) for node in self.path])


    '''이 부분은 mod관련 부분
    getmode 함수를 실행하며 self.mode 755를 불러와 list형태로 받고 ['7','5','5']
    7,5,5를 각각 탐색하며 getauthor 함수를 실행시킨다.
    get getauthor함수에서는 8진수를 2진수로 바꾸어(이를 수식으로 표현해서 number를 자릿수만큼 빼주고 그 값을 비교함으로서 update 시켰다.) 각각 자리수를 r,w,x식으로 반환하고
    7 -> 111(2) -> ['r','w','x']
    5 -> 101(2) -> ['r','-','x']
    1 -> 001(2) -> ['-','-','x']
    2 -> 010(2) -> ['-','w','-']
    join함수를 통해 하나의 string으로 반환한다
    위 과정을 세번 반복하므로 7,5,5
    결국 temp에는 ['rwx','r-x','r-x']가 저장되며
    temp도 join을 시킴으로서 깔끔하게 rwxr-xr-x가 되었다
    '''
    def getauthor(self, number):
        tempauthor=['-','-','-']
        number = int(number)
        if number-4 >= 0:
            tempauthor[0] = 'r'
            number = number-4
        if number-2 >= 0:
            tempauthor[1] = 'w'
            number = number-2
        if number-1 == 0:
            tempauthor[2] = 'x'
        return ''.join(tempauthor)

    def getmode(self):
        author=list(str(self.mode))
        temp = []
        for num in author:
            temp.extend(self.getauthor(num))
        return ''.join(temp)

    def getsize(self):
        if self.id == 'd':              #디렉토리 기본 사이즈 4096
            return 4096
        else:
            sum = 0
            for temp in self.txt:       #text파일은 모든 글자의 byte수를 더했다.
                sum = sum + len(temp)
            return sum * 2              #한글자는 2byte

class PreOrderIter(object):

    def __init__(self, node):
        super(PreOrderIter, self).__init__()
        self.node = node

    def __iter__(self):
        stack = [self.node]
        while stack:
            node = stack[0]
            yield node
            stack = node.children + stack[1:]

            

class LoopError(RuntimeError):          #이것도 NodeMixin에 쓰이는데 except를 유발하는 사용자 정의 class인것만 알면 된다.

    """Tree contains infinite loop."""

    pass
