class Tree(object):
    def __init__(self):
        self.parents=[]
        self.children=[]

    def is_root(self):
        if len(self.parents) == 0 :
            return True
        return False



