from Rules.rules import *
from ShapeGrammar.core.grammar import Grammar
from ShapeGrammar.core.rule import *
from ShapeGrammar.conduit.displayEngine import DisplayEngine
from ShapeGrammar.core.geometries import ExtrBlock

sel=rs.GetObject('sel')
shape=ExtrBlock.create_from_brepid(sel)
shape.name='init'

g1 = Grammar('G1')
g1.pre_execution_shapes=[shape]
g1.pre_execution_names=['A']

RuleStep(g1,Rule(source_name='A',target_names=['B','C']))
RuleStep(g1,Rule(source_name='B',target_names=['C']))

g1.update_rest(0)

for step in g1.rule_steps:
    print(step)

#display=DisplayEngine()
#display.add(g1)
#display.create_monitor()

