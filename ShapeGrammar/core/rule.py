from ShapeGrammar.core.graph import GraphNode, GraphEdge
import rhinoscriptsyntax as rs
import Rhino

class RuleSequence(object):
    def __init__(self):
        # source names are names before the rule execution
        self.pre_execution_names = []
        self.pre_execution_shapes = []
        # taget names are names after the rule execution
        # the difference between the
        # Rule.targe_names and RuleStep.target_names
        # is that RuleStep.target_names includes RuleStep.source_names
        # that are not used in the rule execution
        self.post_execution_names = []
        self.post_execution_shapes = []

        self.prior_step = None
        self.next_step = None

        self.is_selected = False
        self.is_editing = False

    def get_post_execution_params(self):
        return self.post_execution_name, self.post_execution_shapes

    def get_pre_execution_params(self):
        if self.prior_step is not None:
            self.pre_execution_shapes = self.prior_step.post_execution_shapes
            self.pre_execution_names = self.prior_step.post_execution_names
        return self.pre_execution_names, self.pre_execution_shapes

    def is_first_step(self):
        if self.prior_step is None:
            return True
        return False

    def is_terminal_step(self):
        if self.next_step is None:
            return True
        return False

class Rule(object):
    def __init__(self, grammar=None, name=None, source_name=None, target_names=[], params={}):
        self.grammar = grammar
        self.name = name
        # params are params for on_execute
        self.params = params
        self.default_params()

        self.source_name = source_name
        self.source_shapes = []

        self.target_names = target_names
        self.target_shapes = []

        self.stale = True

    def create_from_names(self, source_names, target_names, callback, prams):
        pass

    @staticmethod
    def create_from_phrase(self, phrase):
        # A,B -> divide(0.2,0.3) -> C,D
        phrase = phrase.replace(' ', '')
        phrases = phrase.split('->')
        source_names = phrases[0].split(',')
        target_names = phrases[2].split(',')
        left = phrases[1].find('(')
        right = phrases[1].find(')')
        callback_name = phrases[1][:left]
        params = phrases[1][left:right]
        params = params.split(',')

        print('source_names={}'.format(source_names))
        print('target_names={}'.format(target_names))
        print('callback_name={}'.format(callback_name))
        print('params={}'.format(params))

        # TODO: codes above was designed for function rules, but the rule is class now
        # TODO: reconsider how to call create a rule class from script

    def default_params(self):
        # override to set default for self.params
        pass

    def get_source_shape(self):
        # gets the source shape before
        pass

    def _distribute_target_names(self, shapes):
        for s in shapes:
            nameindex = len(self.target_names) % len(shapes)
            s.name = self.target_names[nameindex]


    def execute(self):
        # shapes=self.callback(self.source_names,self.target_names,self.params)
        # gets the source shapes from names before execution
        # this makes sure the rule always computes with the latest source shapes
        self.get_source_shape()

        self.target_shapes = self.on_execute()

        # after gets the target_shapes
        # must update the names in current steps

        self.stale = False

    def on_execute(self):
        # use:
        # self.source_name
        # self.target_name
        # self.params
        # override
        # must return the target shapes
        pass

    def draw(self, e):
        for shape in self.target_shapes:
            shape.draw(e)

class RuleStep(RuleSequence):
    def __init__(self, grammar=None,rule=None):
        super(RuleStep,self).__init__()
        self.rule = rule
        self.added_rhino_objects=[]
        self.grammar=grammar
        if grammar:
            if len(grammar.rule_steps) == 0:
                self.pre_execution_names, self.pre_execution_shapes = grammar.get_pre_execution_params()
            grammar.add_step(self)


    def __str__(self):
        ruletype=type(self.rule)
        ruletype = '"{}"'.format(ruletype.__name__)
        pre_names=self.pre_execution_names
        txt=str(ruletype) + ' objs({}) ['.format(len(self.pre_execution_shapes))
        for n in self.pre_execution_names:
            txt += str(n) + ','
        txt +=']'
        return txt

    def _set_rule_source_shapes(self):
        #get the shapes from rule.source_name
        source_shapes=[]
        for shape in self.pre_execution_shapes:
            source_shapes.append(shape)
        self.rule.source_shapes=source_shapes

    def _fetch_pre_execution(self):
        if self.is_first_step():
            self.pre_execution_names, self.pre_execution_shapes = self.grammar.get_pre_execution_params()
        else:
            self.pre_execution_names, self.pre_execution_shapes = self.grammar.get_post_execution_params()

    def execute(self):
        self._fetch_pre_execution()
        self._set_rule_source_shapes()

        # pop the name used as the rule source
        none_execution_names = []
        for n in self.pre_execution_names:
            if n != self.rule.source_name:
                none_execution_names.append(n)

        # execute the rule
        self.rule.execute()

        # available names after execution
        self.post_execution_names = self.rule.target_names + none_execution_names

    def draw(self,e):
        if self.is_selected or self.is_editing:
            self.rule.draw(e)

    def add_mesh_to_rhino(self):
        self.remove_rhino_objects()
        if self.is_terminal_step():
            for shape in self.post_execution_shapes:
                mesh=shape.representations['mesh']
                guid=Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh)
                self.added_rhino_objects.append(guid)
                rs.ObjectName(guid,shape.name)

    def remove_rhino_objects(self):
        rs.DeleteObjects(self.added_rhino_objects)
