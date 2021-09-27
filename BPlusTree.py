from math import ceil
from typing import Callable, Iterator, Optional, List
from logging import getLogger
from bisect import bisect_right, bisect_left

logger = getLogger('BPlusTree_Logger')

class BPlusTree_Node(object):
    """The node object in a B+ Tree

    Args:
        order (int): The order of the tree
        parent (BPlusTree_Node): The parent node of the new node

    Attributes:

    """
    #region Properties

    @property
    def order(self) -> int:
        """Return the BPlusTree order as integer. (Read-only)"""
        return self._order

    @property
    def parent(self) -> Optional['BPlusTree_Node']:
        """Return the parent node."""
        return self._parent

    @parent.setter
    def parent(self, value: 'BPlusTree_Node'):
        if value and not isinstance(value, BPlusTree_Node):
            raise ValueError('Parent must be a BPlusTree_Node instance.')
        self._parent = value

    @property
    def children(self) -> List['BPlusTree_Node']:
        """Return the list of child nodes."""
        return self._children

    @children.setter
    def children(self, value: List['BPlusTree_Node']):
        if not isinstance(value, list):
            raise ValueError('Children must be a list of BPlusTree_Node instance.')
        self._children = value

    @property
    def left(self) -> Optional['BPlusTree_Node']:
        """Return the brother node on the left."""
        return self._left

    @left.setter
    def left(self, value: Optional['BPlusTree_Node']):
        if value and not isinstance(value, BPlusTree_Node):
            raise ValueError('Left must be a BPlusTree_Node instance.')
        self._left = value

    @property
    def right(self) -> Optional['BPlusTree_Node']:
        """Return the brother node on the right."""
        return self._right

    @right.setter
    def right(self, value: Optional['BPlusTree_Node']):
        if value and not isinstance(value, BPlusTree_Node):
            raise ValueError('Right must be a BPlusTree_Node instance.')
        self._right = value

    @property
    def next(self) -> Optional['BPlusTree_Node']:
        """Return the next leaf node. (For leaf nodes only, None otherwise)"""
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
    def keys(self) -> list:
        """Return the list of keys in current node."""
        return self._keys

    @keys.setter
    def keys(self, value: list):
        if not isinstance(value, list):
            raise ValueError('Keys must be a list of int instance.')
        self._keys = value

    @property
    def values(self) -> list:
        """Return the list of values in current node. (For leaf nodes only)"""
        return self._values

    @values.setter
    def values(self, value: list):
        if not isinstance(value, list):
            raise ValueError('Values must be a list instance.')
        self._values = value

    @property
    def full(self) -> bool:
        """Return True if splitting is needed. (Read-only)"""
        return len(self._keys) >= self._order

    @property
    def empty(self) -> bool:
        """Return True if no key left. (Read-only)"""
        return len(self._keys) <= 0

    @property
    def valid(self) -> bool:
        """Return True if the number of keys meets the minimum requirement. (Read-only)"""
        return self.root or len(self.keys) >= ceil(self._order/2)-1

    @property
    def borrowable(self) -> bool:
        """Return True if the number of keys is more than minimum requirement. (Read-only)"""
        return len(self.keys) > ceil(self._order/2)-1

    @property
    def leaf(self) -> bool:
        """Return True if current node is a leaf node. (Read-only)"""
        return len(self._children) == 0

    @property
    def root(self) -> bool:
        """Return True if current node is a root node. (Read-only)"""
        return not self._parent

    @property
    def height(self) -> int:
        """Return the height of current node, 0 for root. (Read-only)"""
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
    """The B+ Tree object

    Args:
        order (int): The order of the tree
        parent (BPlusTree_Node): The parent node of the new node

    Attributes:
        hash_func (Callable): The hashing function to map key to integers
        len (int): The total number of elements in the tree

    """
    #region Properties

    @property
    def order(self) -> int:
        """ Return the BPlusTree order as integer. """
        return self._order

    @property
    def root(self) -> BPlusTree_Node:
        """ Return the root node. """
        return self._root

    @property
    def leaf(self) -> BPlusTree_Node:
        """ Return the first leaf node on the left. """
        return self._leaf

    #endregion

    def __init__(self, order: int, hash_func: Callable = lambda x: x):
        if not isinstance(order, int):
            raise ValueError('Order has to be integer.')
        self._order = order
        if not callable(hash_func):
            raise ValueError('Hash function is not callable.')
        self.hash_func = hash_func
        self.len = 0
        self._leaf = self._root = BPlusTree_Node(self._order)

    #region Private methods

    def _split_node(self, node: BPlusTree_Node) -> None:
        """Split a node if the number of elements exceeded the maximum.

        Split the target node with the key in the middle and add the splitting key into its parent node.
        Then a recursive check will be applied to the parent node. 
        Returns when the target node meets the rule.

        Args:
            node (BPlusTree_Node): the target node to check and split

        Returns:
            None

        """
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
        else: # inner node
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
        """Fix a node if the number of elements doesn't meet the minimum requirement.

        Fix the node after deletion by either borrowing an element or being merged with one of its brother node.
        Splitting key at the parent node will be updated or removed.
        Then a recursive check will be applied to the parent node. 
        Returns when the target node meets the rule.

        Args:
            node (BPlusTree_Node): the target node to check and fix

        Returns:
            None

        """
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
            else: # inner nodes
                key = node.parent.keys[pos]
                child = node.left.children.pop()
                child.parent, child.left, child.right = node, None, node.children[0]
                node.children[0].left = child
                node.children.insert(0, child)
            node.keys.insert(0, key)
            node.parent.keys[pos] = split_key
        elif node.right and node.right.borrowable: # if possible to borrow an element from brother node on the right
            split_key = node.right.keys.pop(0)
            pos = bisect_right(node.parent.keys, split_key) # update key in parent node
            if node.leaf:
                key, split_key = split_key, node.right.keys[0]
                node.values.append(node.right.values.pop(0))
            else: # inner nodes
                key = node.parent.keys[pos]
                child = node.right.children.pop(0)
                child.parent, child.left, child.right = node, node.children[-1], None
                node.children[-1].right = child
                node.children.append(child)
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

    def _find_target_leaf(self, key) -> BPlusTree_Node:
        """Find the corresponding leaf node by the target key value.

        Iterates from root to the leaf node where we operate additon, deletion or lecture. 

        Args:
            key (Any): the key to search with

        Returns:
            BPlusTree_Node: the leaf node of destination
            
        """
        temp = self._root
        while not temp.leaf: # iterate to the target leaf node
            pos = bisect_right(temp.keys, key)
            temp = temp.children[pos]
        return temp

    def _iterate_by_slice(self, slice_: Optional[slice]) -> Iterator[tuple]:
        """Iterates (key, value) pair in a given interval

        Iterates all records if interval is not given. 
        Otherwise, keys will be restricted. 

        Args:
            slice (slice): key interval to iterate

        Returns:
            Iterator: a generator of (key, value) tuple

        Raises:
            ValueError: if start value is no less than stop or a custom step is specified.

        """
        if not slice_: # begins from the first leaf node if slice is not given
            leaf = self._leaf
            pos = 0
        elif slice_.step is not None:
            raise ValueError('Custom step is not supported.')
        else:
            hash_start = self.hash_func(slice_.start) if slice_.start is not None else None
            hash_stop = self.hash_func(slice_.stop) if slice_.stop is not None else None
            if hash_start is not None and hash_stop is not None and hash_start >= hash_stop:
                raise ValueError('Impossible to iterate backwards.')
            elif hash_start is None: # begins from the first leaf node if start is not given
                leaf = self._leaf
                pos = 0
            else:
                try:
                    leaf = self._find_target_leaf(hash_start)
                    pos = bisect_left(leaf.keys, hash_start)
                except TypeError:
                    raise TypeError('Uncomparable key type, check hashing function.')
                else:
                    if pos >= len(leaf.keys): # in case where start value does not exist
                        leaf, pos = leaf.next, 0
                        if not leaf:
                            return
        if leaf.empty: # in case the whole tree is empty
            return
        while not slice_ or hash_stop is None or leaf.keys[pos] < hash_stop:
            yield leaf.keys[pos], leaf.values[pos]
            pos += 1
            if pos >= len(leaf.keys):
                leaf, pos = leaf.next, 0
                if not leaf:
                    break

    #endregion

    #region Overrides

    def __contains__(self, key):
        try:
            self.search(key)
        except ValueError:
            return False
        else:
            return True

    def __setitem__(self, key, value):
        self.insert(key, value, update=True)

    def __getitem__(self, key):
        if isinstance(key, slice): # return a dictionary if get by slice
            res = {}
            for k, v in self._iterate_by_slice(key):
                res[k] = v
            return res
        return self.search(key)

    def __len__(self):
        return self.len

    def __iter__(self, slice_: Optional[slice] = None):
        for k, _ in self._iterate_by_slice(slice_):
            yield k

    #endregion

    #region Public methods

    def search(self, key):
        """Search value by key.

        Args:
            key (Any): the key to search with

        Returns:
            Any: the target value
            
        Raises:
            ValueError: if key does not exist.

        """
        hash_key = self.hash_func(key)
        try:
            dest = self._find_target_leaf(hash_key)
            pos = bisect_left(dest.keys, hash_key) # search the appearance location
        except TypeError:
            raise TypeError('Uncomparable key type, check hashing function.')
        else:
            if dest.empty or dest.keys[pos] != hash_key:
                raise ValueError(f'[{key}] key doesn\'t exist.')
            return dest.values[pos]

    def insert(self, key, value, update: bool = False):
        """Insert the (key, value) pair into the tree

        Args:
            key (Any): the key to insert
            value (Any): the value to insert
            update (bool): True to ignore the presence of key and update its value

        Returns:
            None
            
        Raises:
            ValueError: if key already exists and update is not set to True.

        """
        hash_key = self.hash_func(key)
        try:
            dest = self._find_target_leaf(hash_key)
            pos = bisect_right(dest.keys, hash_key) # search the insert location
        except TypeError:
            raise TypeError('Uncomparable key type, check hashing function.')
        else:
            if not dest.empty and dest.keys[pos-1] == hash_key: # key already exists
                if update:
                    dest.values[pos-1] = value
                    logger.info(f'[{key}] updated value to: {value}.')
                else:
                    raise ValueError(f'[{key}] key already exists.')
            else:
                dest.keys.insert(pos, hash_key) # insert key into list in a sorted manner
                dest.values.insert(pos, value)
            self._split_node(dest)
            self.len += 1
            logger.info(f'[{key}] added value: {value}.')

    def delete(self, key):
        """Delete the key from the tree

        Args:
            key (Any): the key to remove

        Returns:
            None
            
        Raises:
            ValueError: if key does not exist.

        """
        hash_key = self.hash_func(key)
        try:
            dest = self._find_target_leaf(hash_key)
            pos = bisect_left(dest.keys, hash_key)
        except TypeError:
            raise TypeError('Uncomparable key type, check hashing function.')
        else:
            if dest.empty or dest.keys[pos] != hash_key:
                raise ValueError(f'[{key}] key doesn\'t exist.')
            dest.keys.pop(pos)
            dest.values.pop(pos)
            self._fix_node(dest)
            self.len -= 1
            logger.info(f'[{key}] deleted.')

    def clear(self):
        """Clear all items in the tree."""
        self._leaf = self._root = BPlusTree_Node(self._order)

    def summary(self):
        """Display the tree nodes in a BFS manner. (For test in small amount only)"""
        queue = [self._root]
        while queue:
            cur = queue.pop(0)
            print(f'height: {cur.height}\n{cur.keys}\n{cur.values}')
            queue += cur.children

    def items(self, slice_: Optional[slice] = None) -> Iterator[tuple]:
        """Iterate (key, value) pairs

        Args:
            slice_ (slice): key interval to iterate

        Returns:
            Iterator: a generator of (key, value) tuple
            
        Raises:
            ValueError: if start value is no less than stop or a custom step is specified.

        """
        return self._iterate_by_slice(slice_)

    keys = __iter__

    def values(self, slice_: Optional[slice] = None):
        """Iterate values

        Args:
            slice_ (slice): key interval to iterate

        Returns:
            Iterator: a generator of values
            
        Raises:
            ValueError: if start value is no less than stop or a custom step is specified.

        """
        for _, v in self._iterate_by_slice(slice_):
            yield v

    #endregion
