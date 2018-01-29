from pyplot import exc, utils


class _TraverseContext:
    def __init__(self, qualname='', depth=0, ids=(0,), lens=(1,)):
        self.depth = depth
        self.ids = ids
        self.lens = lens
        self.qualname = qualname
        # propagate is only useful in pre-order traverse
        self.propagate = True

    def __repr__(self):
        return ("<{}(depth={}, ids={}, lens={}, qualname='{}', "
                "propagate={})>".format(
                    self.__class__.__name__,
                    self.depth, self.ids, self.lens,
                    self.qualname,
                    self.propagate,
                ))


@utils.class_logger
class Tree:
    def __init__(self):
        super().__init__()
        self.parent = None
        self._subtrees = []
        self.name = None

    def __repr__(self):
        return self.format()

    @property
    def root(self):
        if self.parent is None:
            return self
        else:
            return self.parent.root

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return not self._subtrees

    def _is_eligible_child(self, child):
        # Should return True or False
        raise NotImplementedError

    def _can_add_child(self, child):
        if child.parent is not None:
            msg = (f"'{child}' already has a parent, "
                   f"reparenting is currently not supported")
            raise exc.PlotError(msg)

    def add_child(self, child, name, index=None):
        if not self._is_eligible_child(child):
            msg = f"{child} is not an eligible child for {self}"
            raise exc.PlotError(msg)
        self._can_add_child(child)
        object.__setattr__(child, 'parent', self)
        child.name = name
        if child in self._subtrees:
            msg = f"{child} already added, cannot add again"
            raise exc.PlotError(msg)
        if index is None:
            self._subtrees.append(child)
        else:
            self._subtrees.insert(index, child)
        child.call('subscribe_all_in_cache')
        self._on_add_child(child)

    def _on_add_child(self, child):
        # For subclass to overwrite
        pass

    def has_child(self, child):
        return child in self._subtrees

    def remove_child(self, child):
        if child not in self._subtrees:
            msg = f"{child} is not child of {self}"
            raise exc.PlotError(msg)
        child.call('unsubscribe_all_in_cache')
        self._on_remove_child(child)
        child.name = None
        object.__setattr__(child, 'parent', None)
        self._subtrees.remove(child)

    def _on_remove_child(self, child):
        # For subclass to overwrite
        pass

    def __setattr__(self, name, val):
        if not name.startswith('_'):
            try:
                old_val = getattr(self, name)
            except AttributeError as e:
                pass
            else:
                if self.has_child(old_val):
                    self.remove_child(old_val)
            if self._is_eligible_child(val):
                self.add_child(val, name)
        object.__setattr__(self, name, val)

    def __delattr__(self, name):
        if not name.startswith('_'):
            val = getattr(self, name)
            if self.has_child(val):
                self.remove_child(val)
        object.__delattr__(self, name)

    def copy(self):
        raise NotImplementedError

    def traverse(self, callback=None, right_to_left=False, order='pre',
                 _context=None):
        def _call_callback():
            if callback is not None:
                ret_val = callback(self, _context)
                yield (self, ret_val)
            else:
                yield self

        if order not in ['pre', 'post']:
            msg = "Only pre-order and post-order traverse is supported"
            raise ValueError(msg)
        if _context is None:
            _context = _TraverseContext()
        if order == 'pre':
            # pre-order traversal
            yield from _call_callback()
            if not _context.propagate:
                return
        if self._subtrees:
            new_depth = _context.depth + 1
            if len(_context.lens) < _context.depth + 2:
                new_lens = _context.lens + (len(self._subtrees),)
            if right_to_left:
                it = zip(reversed(range(len(self._subtrees))),
                         reversed(self._subtrees))
            else:
                it = enumerate(self._subtrees)
            for i, tree in it:
                new_ids = _context.ids + (i,)
                if _context.qualname:
                    new_qualname = f'{_context.qualname}.{tree.name}'
                else:
                    new_qualname = f'{tree.name}'
                yield from tree.traverse(
                    callback=callback,
                    right_to_left=right_to_left,
                    order=order,
                    _context=_TraverseContext(
                        new_qualname, new_depth, new_ids, new_lens))
        if order == 'post':
            # post-order traversal
            yield from _call_callback()

    def call(self, method, call_args=None, call_kwargs=None,
             right_to_left=False, order='pre'):
        # A convenient method to call arbitrary method on trees.
        called = []
        if call_args is None:
            call_args = []
        if call_kwargs is None:
            call_kwargs = {}
        if isinstance(method, str):
            def _call(tree):
                if hasattr(tree, method):
                    ret_val = getattr(tree, method)(*call_args, **call_kwargs)
                    called.append((tree, ret_val))
        elif callable(method):
            def _call(tree):
                ret_val = method(tree, *call_args, **call_kwargs)
                called.append((tree, ret_val))
        else:
            msg = (f"'method' should be a callable or str, not "
                   f"{method.__class__.__module__}."
                   f"{method.__class__.__qualname__}")
            raise TypeError(msg)

        def callback(tree, ctx):
            _call(tree)
        list(self.traverse(callback=callback, right_to_left=right_to_left,
                           order=order))
        return called

    def add_method(self, name, func):
        from types import MethodType
        setattr(self, name, MethodType(func, self))

    def get_attr(self, attr_name, default):
        val = getattr(self, attr_name)
        if val != default:
            return val
        else:
            if self.is_root():
                return default
            else:
                return self.parent.get_attr(attr_name, default)

    def format(self, fmt='short', with_parent=True):
        if fmt not in ['short', 'full']:
            raise ValueError(f"Unknown fmt '{fmt}'")
        if with_parent:
            p_list = []
            tree = self
            while True:
                if tree.is_root():
                    if tree.name is not None:
                        name = tree.name
                    else:
                        name = 'root'
                    p_list.append(name)
                    break
                else:
                    p_list.append(tree.name)
                    tree = tree.parent
            name = '.'.join(reversed(p_list))
        else:
            if self.is_root():
                if self.name is not None:
                    name = self.name
                else:
                    name = 'root'
            else:
                name = self.name
        base = f"{name}<{self.__class__.__name__}>"
        return base

    def format_tree(self):
        T = '├─'
        I = '│'
        L = '└─'
        D = '─'             # noqa: F841
        STAR = '★ '         # noqa: F841
        DIAMOND = '♦ '      # noqa: F841
        RARROW = '→ '       # noqa: F841
        LEAF = '🍂'         # noqa: F841
        LEAF2 = '☘ '        # noqa: F841
        SELECT = '█'        # noqa: F841
        SPACE3 = ' ' * 3
        SPACE4 = ' ' * 4

        rows = []

        def callback(tree, ctx):
            if ctx.depth == 0:
                prefix = ''
            else:
                prefix = SPACE4
            end_condition = []
            for d in range(ctx.depth + 1):
                if ctx.ids[d] == ctx.lens[d] - 1:
                    end_condition.append(True)
                else:
                    end_condition.append(False)
            for c in end_condition[:-1]:
                if c:
                    prefix += SPACE4
                else:
                    prefix += I + SPACE3
            leader = L if end_condition[-1] else T
            tree_str = tree.format(fmt='full', with_parent=False)
            if tree.is_leaf():
                tree_str = LEAF + tree_str
            txt = prefix + leader + ' ' + tree_str
            rows.append(txt)

        list(self.traverse(callback=callback))
        return '\n'.join(rows)

    def print_tree(self, **kwargs):
        print(self.format_tree(), **kwargs)



