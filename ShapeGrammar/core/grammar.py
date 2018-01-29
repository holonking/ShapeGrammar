from ShapeGrammar.core.rule import RuleSequence

class Grammar(RuleSequence):
    def __init__(self, name=''):
        super(Grammar,self).__init__()
        self.name=name
        self.rule_steps=[]
        self.current_step=0
        self.selected_step_index=None
        pass

    def update_current(self,index):
        self.update_rule(index)

    def update_rest(self ,index):
        # update all rules since the index
        for i in range(index,len(self.rule_steps)):
            self.rule_steps[i].execute()


    def add_step(self, rule_step, execute=False):
        self.rule_steps.append(rule_step)
        if execute:
            rule_step.execute()


    def draw(self,e):
        self.rule_steps[self.selected_step_index].draw(e)

    def select(self, index):
        self.selected_step_index