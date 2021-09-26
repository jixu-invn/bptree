from typing import Optional, List, Tuple, Union
from logging import getLogger
from bisect import bisect_right, bisect_left
from math import ceil

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
        if value and not isinstance(value, BPlusTree_Node):
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
    def left(self) -> Optional['BPlusTree_Node']:
        """ Return the brother node on the left. """
        return self._left

    @left.setter
    def left(self, value: Optional['BPlusTree_Node']):
        if value and not isinstance(value, BPlusTree_Node):
            raise ValueError('Left must be a BPlusTree_Node instance.')
        self._left = value

    @property
    def right(self) -> Optional['BPlusTree_Node']:
        """ Return the brother node on the right. """
        return self._right

    @right.setter
    def right(self, value: Optional['BPlusTree_Node']):
        if value and not isinstance(value, BPlusTree_Node):
            raise ValueError('Right must be a BPlusTree_Node instance.')
        self._right = value

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
    def empty(self) -> bool:
        """ Return True if no key left. """
        return len(self._keys) <= 0

    @property
    def valid(self) -> bool:
        return self.root or len(self.keys) >= ceil(self._order/2)-1

    @property
    def borrowable(self) -> bool:
        return len(self.keys) > ceil(self._order/2)-1

    @property
    def leaf(self) -> bool:
        """ Return True if current node is a leaf node. """
        return len(self._children) == 0

    @property
    def root(self) -> bool:
        """ Return True if current node is a root node. """
        return not self._parent

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
        self._left = self._right = self._next = None
        self._keys, self._values, self._children = [], [], [] # We use list here instead of dict to have a sorted order for keys

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
        if not node.full:
            return
        pos = int(len(node.keys)/2) # compute split position
        if node.root: # if splitting a root node
            self._root = node.parent = BPlusTree_Node(self._order)
            node.parent.children.append(node)
        new = BPlusTree_Node(self._order, node.parent) # create a new node on the right hand side
        new.left, new.right, node.right = node, node.right, new
        split_key = node.keys[pos] # the key to be inserted into parent node
        if node.leaf:
            node.keys, new.keys = node.keys[:pos], node.keys[pos:]
            node.values, new.values = node.values[:pos], node.values[pos:]
            node.next, new.next = new, node.next
        else:
            node.keys, new.keys = node.keys[:pos], node.keys[pos+1:]
            node.children, new.children = node.children[:pos+1], node.children[pos+1:]
            node.children[-1].right = new.children[0].left = None # no longer brothers due to parent splitting
            for n in new.children:
                n.parent = new
        pos = bisect_right(node.parent.keys, split_key) # insert position in parent node
        node.parent.keys.insert(pos, split_key)
        node.parent.children.insert(pos+1, new)
        self._split_node(node.parent) # recursively check parent nodes

    def _fix_node(self, node: BPlusTree_Node) -> None:
        if node.root and (not node.leaf) and node.empty: # remove empty root
            self._root = node.children.pop()
            self._root.parent = None
        if node.valid:
            return
        if node.left and node.left.borrowable: # if possible to borrow an element from brother node on the left
            split_key = node.left.keys.pop()
            pos = bisect_left(node.parent.keys, split_key) # update key in parent node
            if node.leaf:
                key = split_key
                node.values.insert(0, node.left.values.pop())
            else:
                key = node.parent.keys[pos]
                node.children.insert(0, node.left.children.pop())
                node.children[0].parent = node
            node.keys.insert(0, key)
            node.parent.keys[pos] = split_key
        elif node.right and node.right.borrowable: # if possible to borrow an element from brother node on the right
            split_key = node.right.keys.pop(0)
            pos = bisect_right(node.parent.keys, split_key) # update key in parent node
            if node.leaf:
                key, split_key = split_key, node.right.keys[0]
                node.values.append(node.right.values.pop(0))
            else:
                key = node.parent.keys[pos]
                node.children.append(node.right.children.pop(0))
                node.children[-1].parent = node
            node.keys.append(key)
            node.parent.keys[pos-1] = split_key
        else: # merge with brother on the left or on the right
            merge_left, merge_right = (node.left, node) if node.left else (node, node.right)
            pos = bisect_right(merge_left.parent.keys, merge_left.keys[0]) # remove key and child in parent node
            split_key = merge_left.parent.keys.pop(pos)
            merge_left.parent.children.pop(pos+1)
            merge_left.keys += merge_right.keys
            merge_left.right = merge_right.right
            if merge_right.right:
                merge_right.right.left = merge_left
            if merge_left.leaf:
                merge_left.values += merge_right.values
                merge_left.next = merge_right.next
            else:
                merge_left.keys.insert(len(merge_left.children)-1, split_key)
                merge_left.children[-1].right, merge_right.children[0].left = merge_right.children[0], merge_left.children[-1]
                merge_left.children += merge_right.children
                for n in merge_right.children:
                    n.parent = merge_left
            self._fix_node(merge_left.parent) # recursively check parent nodes

    def _find_target_leaf(self, key: int) -> BPlusTree_Node:
        temp = self._root
        while not temp.leaf: # iterate to the target leaf node
            pos = bisect_right(temp.keys, key)
            temp = temp.children[pos]
        return temp

    #endregion

    def search(self, key: int):
        dest = self._find_target_leaf(key)
        pos = bisect_left(dest.keys, key) # search the appearance location
        if dest.keys[pos] != key:
            raise ValueError(f'[{key}] key doesn\'t exist.')
        return dest.values[pos]

    def insert(self, key: int, value, update: bool = False):
        dest = self._find_target_leaf(key)
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
        self._split_node(dest)
        self._logger.info(f'[{key}] added value: {value}.')

    def delete(self, key: int):
        dest = self._find_target_leaf(key)
        pos = bisect_left(dest.keys, key)
        if dest.keys[pos] != key:
            raise ValueError(f'[{key}] key doesn\'t exist.')
        dest.keys.pop(pos)
        dest.values.pop(pos)
        self._fix_node(dest)

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
for t in test_set:
    test.delete(t)
#test.delete()
test.summary()