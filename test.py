import random
import time
import os
from math import pow

from BPlusTree import BPlusTree

def test_functional(tree: BPlusTree = None, order: int = 1000, amount: int = 10000):
    """Test the functionality of BPlusTree

    1. Insert all elements and check length
    2. Check existance of all elements
    3. Remove a random half of the elements
    4. Check existance of reserved ones and success of deletion
    5. Insert all elements back and check existance of all
    6. Check tranversing iteration in the right order
    7. Clear the tree and check all elements no longer in the tree

    Args:
        tree (BPlusTree): optional b plus tree instance
        order (int): order of the tree
        amount (int): amount of elements to test with
    Returns:
        None

    """
    random_list = random.sample(range(amount*10), amount)
    bptree = BPlusTree(order) if tree is None else tree
    # insert all keys
    for k in random_list:
        bptree[k] = k
    assert(len(bptree) == amount)
    # check search
    for k in random_list:
        assert(bptree[k] == k)
    # remove a half of keys
    delete_list = random.sample(random_list, int(amount/2))
    for k in delete_list:
        bptree.delete(k)
    # check deletion does not destruct the tree
    for k in random_list:
        if k in delete_list:
            assert(k not in bptree)
        else:
            assert(k in bptree)
    # insert all keys back
    for k in delete_list:
        bptree[k] = k
    # recheck all elements
    for k in random_list: 
        assert(bptree[k] == k)
    # check tranversing algorithm
    last_key = None
    for k in bptree:
        assert(last_key is None or k > last_key) # keys in the right order
        last_key = k
    # check clear
    bptree.clear()
    for k in random_list:
        assert(k not in bptree)

def test_speed(tree: BPlusTree = None, order: int = 1000, amount: int = 100000, filename: str=''):
    """Test speed of insertion, search and deletion

    Args:
        tree (BPlusTree): optional b plus tree instance
        order (int): order of the tree
        amount (int): amount of elements to test with

    Returns:
        None

    """
    bptree = BPlusTree(order=order) if tree is None else tree
    keys = range(amount)
    mode = 'a' if os.path.isfile(filename) else 'w'
    file = open(filename, mode) if filename else None
    # insertion
    timing = time.time()
    for k in keys:
        bptree[k] = k
    res = 'bptree insertion speed ({}): {}ms.'.format(amount, 1000*(time.time()-timing))
    if file:
        file.write(res+'\n')
    print(res)
    # search
    timing = time.time()
    for k in keys:
        bptree[k]
    res = 'bptree search speed ({}): {}ms.'.format(amount, 1000*(time.time()-timing))
    if file:
        file.write(res+'\n')
    print(res)
    # tranversing
    timing = time.time()
    for _ in bptree:
        pass
    res = 'bptree tranversing speed ({}): {}ms'.format(amount, 1000*(time.time()-timing))
    if file:
        file.write(res+'\n')
    print(res)
    # deletion
    timing = time.time()
    for k in keys:
        bptree.delete(k)
    res = 'bptree deletion speed ({}): {}ms'.format(amount, 1000*(time.time()-timing))
    if file:
        file.write(res+'\n')
        file.close()
    print(res)

if __name__ == '__main__':
    for order in [20, 50, 100, 500, 1000]:
        test_functional(order=order)
    for amount in [int(pow(10, p)) for p in [6, 7, 8]]:
        test_speed(order=1000, amount=amount, filename='test_result.txt')
    print('All tests passed.')
