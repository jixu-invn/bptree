import random

from BPlusTree import BPlusTree

def test_tree(amount: int = 1000, order: int = 100):
    #random.seed(100)
    random_list = random.sample(range(amount*10), amount)
    bptree = BPlusTree(order)
    for k in random_list: # insert all keys
        bptree[k] = k
    assert(len(bptree) == amount)
    for k in random_list: # check search
        assert(bptree[k] == k)
    while random_list: # remove all keys
        pos = random.randint(1, len(random_list))
        bptree.delete(random_list.pop(pos-1))
    assert(len(bptree) == 0)

if __name__ == '__main__':
    test_tree(order=100)
    print('All tests passed.')
