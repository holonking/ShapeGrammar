from ShapeGrammar.core.rule import Rule
from Rhino.Geometry import *

class Bisect(Rule):
    def default_params(self):
        self.params = dict(
            div=0.5,direct=0
        )

    def on_execute(self):
        div=self.params['divs']
        direct=self.params['direct']

        for shape in self.source_shapes:
            amp = self.shape.scope.size[direct] * div
            close,far = shape._split_dir_amp(direct, amp)
            if close is not None and far is not None:
                self._distribute_target_names([close,far])



