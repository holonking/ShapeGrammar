class GraphNode(object):
    def __init__(self):
        self.name=''
        # the output and inputs are dictionaries
        # indexed by names
        self.source = {}
        self.target = {}
        self.stale = False

    def add_source(self,source):
        self.source[source.name]=source

    def add_target(self,target):
        self.target[target.name]=target

    def add_edge(self,name):
        self.target[name]=GraphEdge()


    def set_target_shape(self,name,shape):
        if name not in self.target:
            self.add_edge(name)

    def set_stale(self,flag=True):
        self.stale=flag

    def upate(self):
        if self.stale:
            for k in self.target:
                self.target[k].update()

    def pop_target(self,name):
        if name in self.target:
            self.target.pop(name)

    def pop_source(self,name):
        if name in self.source:
            self.target.pop(name)

    def print_node(self):
        # ls=len(self.source)
        # lt=len(self.target)
        source_text=[]
        target_text=[]
        for s,t in zip(self.source,self.target):
            source_text.append(s.name)
            target_text.append(t.name)

        txt='<{}>- {} -<{}>'.format(source_text,self.name,target_text)

class GraphEdge(object):
    def __init__(self,source=None, target=None, shape=None):
        self.source=source
        self.target=target
        self.stale=False
        self.shape=shape

    def update(self):
        if self.target and self.stale:
            self.target.update()

    def set_shape(self,shape,update=False):
        self.stale=True
        self.shape=shape
        if update:
            self.update()

    def set_source(self,source):
        self.source=source
        self.stale=True

    def sel_target(self,target):
        self.target=target
        self.target.set_stale()






