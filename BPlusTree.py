from typing import Optional, List
from logging import getLogger
from bisect import bisect_right, bisect_left

class BPlusTree_Node(object):

    #region Properties

    @property
    def order(self) -> int:
        """ Return the BPlusTree order as integer. """
        return self._order

    @property
    def parent(self) -> Optional['BPlusTree_Node']:
        """ Return the parent node. """
        return self._parent

    @parent.setter
    def parent(self, value: 'BPlusTree_Node'):
        if not isinstance(value, BPlusTree_Node):
            raise ValueError('Parent must be a BPlusTree_Node instance.')
        self._parent = value

    @property
    def children(self) -> List['BPlusTree_Node']:
        """ Return the list of child nodes. """
        return self._children

    @children.setter
    def children(self, value: List['BPlusTree_Node']):
        if not isinstance(value, list):
            raise ValueError('Children must be a list of BPlusTree_Node instance.')
        self._children = value

    @property
    def previous(self) -> Optional['BPlusTree_Node']:
        """ Return the previous leaf node. (For leaf nodes only, None otherwise) """
        return self._previous

    @property
    def next(self) -> Optional['BPlusTree_Node']:
        """ Return the next leaf node. (For leaf nodes only, None otherwise) """
        return self._next

    @next.setter
    def next(self, value: Optional['BPlusTree_Node']):
        if value is not None:
            if not isinstance(value, BPlusTree_Node):
                raise ValueError('Next must be a BPlusTree_Node instance.')
            elif not value.leaf:
                raise ValueError('Next must be a leaf node instance.')
        self._next = value

    @property
    def keys(self) -> List[int]:
        """ Return the list of keys in current node. """
        return self._keys

    @keys.setter
    def keys(self, value: List[int]):
        if not isinstance(value, list):
            raise ValueError('Keys must be a list of int instance.')
        self._keys = value

    @property
    def values(self) -> list:
        """ Return the list of values in current node. (For leaf nodes only) """
        return self._values

    @values.setter
    def values(self, value: list):
        if not isinstance(value, list):
            raise ValueError('Values must be a list instance.')
        self._values = value

    @property
    def full(self) -> bool:
        """ Return True if splitting is needed. """
        return len(self._keys) >= self._order

    @property
    def leaf(self) -> bool:
        """ Return True if current node is a leaf node. """
        return len(self._children) == 0

    @property
    def height(self) -> int:
        """ Return the height of current node. """
        tmp, h = self.parent, 0
        while tmp is not None:
            tmp = tmp.parent
            h += 1
        return h

    #endregion

    def __init__(self, order: int, parent: 'BPlusTree_Node' = None):
        self._order = order
        self._parent = parent
        self._children = []
        self._previous = None
        self._next = None
        self._keys = [] # We use list here instead of dict to have a sorted order for keys
        self._values = []

class BPlusTree:

    #region Properties

    @property
    def order(self) -> int:
        return self._order 

    #endregion

    def __init__(self, order: int):
        if not isinstance(order, int):
            raise ValueError('Order has to be integer.')
        self._order = order
        self._root = BPlusTree_Node(self._order)
        self._leaf = self._root
        self._logger = getLogger('BPlusTree_Logger')

    #region Private methods

    def _split_node(self, node: BPlusTree_Node) -> None:
        if node.full:
            pos = int(len(node.keys)/2) # compute split position
            if node.parent is None: # if splitting a root node
                self._root = node.parent = BPlusTree_Node(self._order)
                node.parent.children.append(node)
            new = BPlusTree_Node(self._order, node.parent) # create a new node on the right hand side
            split_key = node.keys[pos]
            if node.leaf:
                node.keys, new.keys = node.keys[:pos], node.keys[pos:]
                node.values, new.values = node.values[:pos], node.values[pos:]
                node.next, new.next = new, node.next
            else:
                node.keys, new.keys = node.keys[:pos], node.keys[pos+1:]
                node.children, new.children = node.children[:pos+1], node.children[pos+1:]
            pos = bisect_right(node.parent.keys, split_key) # insert position in parent node
            node.parent.keys.insert(pos, split_key)
            node.parent.children.insert(pos+1, new)
            self._split_node(node.parent) # recursively check parent nodes

    #endregion

    def search(self, key: int):
        dest = self._root
        while not dest.leaf:
            pos = bisect_right(dest.keys, key)
            dest = dest.children[pos]
        pos = bisect_left(dest.keys, key)
        if dest.keys[pos] != key:
            raise ValueError(f'[{key}] key doesn\'t exist.')
        return dest.values[pos]

    def insert(self, key: int, value, update: bool = False):
        dest = self._root
        while not dest.leaf: # iterate to the target leaf node
            pos = bisect_right(dest.keys, key)
            dest = dest.children[pos]
        pos = bisect_right(dest.keys, key) # search the insert location
        if len(dest.keys) > 0 and dest.keys[pos-1] == key: # key already exists
            if update:
                dest.values[pos-1] = value
                self._logger.info(f'[{key}] updated value to: {value}.')
            else:
                raise ValueError(f'[{key}] key already exists.')
        else:
            dest.keys.insert(pos, key) # insert key into list in a sorted manner
            dest.values.insert(pos, value)
            self._logger.info(f'[{key}] added value: {value}.')
        self._split_node(dest)

    def delete(self, key):
        pass

    def summary(self):
        queue = [self._root]
        while queue:
            cur = queue.pop(0)
            print(f'height: {cur.height}\n{cur.keys}\n{cur.values}')
            queue += cur.children

test_set = [5, 8, 10, 15, 16, 17, 18, 6, 7, 9, 19, 20, 21, 22]
test = BPlusTree(5)
for t in test_set:
    test.insert(t, t)
#test.summary()
print(test.search(8))
print(test.search(11))