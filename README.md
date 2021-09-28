# bptree

Reference: [B+ tree](https://en.wikipedia.org/wiki/B%2B_tree)

## User Manuel

### Class attributes

`order` : the order of tree, applies to both inner and leaf nodes.
`hash_func` : the hash function for key mapping, default to `lambda x: x`. The return value shall be comparable. 

### Insertion

```
tree = BPlusTree()
tree.insert(key=5, value=5) # first way to insert, exception when key exists
tree[2] = 2 # second way to insert, update value when key exists
```

### Search

```
tree = BPlusTree()
tree.insert(key=5, value=5)
print(tree.search(5)) # first way to search
print(tree[5]) # second way to search
```

### Deletion

```
tree = BPlusTree()
tree.insert(key=5, value=5)
tree.delete(5) # delete element from tree
tree.delete(2) # raises exception since 2 doesn't exist
```

### Tranversive iteration

```
for k in tree: # iterate keys, equivalent to "for k in tree.keys():"
    pass
for k, v in tree.items(): # iterate items
    pass
for v in tree.values(): # iterate values
    pass
```

### Interval search

```
tree = BPlusTree()
tree.insert(key=5, value=5)
tree[5:] # returns {5: 5}
tree[:5] # returns {}
for k, v in tree.items(slice(start=5)): # tranversing in interval
    pass
```

## Test and benchmark

Run test.py and the implementation will be tested in both functionality and speed. 

The functionality test includes:

* Insert all elements and check length
* Check existance of all elements
* Remove a random half of the elements
* Check existance of reserved ones and success of deletion
* Insert all elements back and check existance of all
* Check tranversing iteration in the right order
* Clear the tree and check all elements no longer in the tree

Success when no assertion error.

The speed test will benchmark insertion, search, tranversing and deletion speed. Three tests will be conducted in a serie with the number of elements (integer keys) varying in 10^6, 10^7 and 10^8. The result in milliseconds will be samed in the project root with a name of `test_result.txt`.

Test environment:

* Windows 10 x64
* CPU: AMD Ryzen 5 5600X 6-Core Processor 3.70 GHz
* RAM: 16.0 GB
* Python 3.9.7

Test speed in milliseconds (Tree order fixed to 1000):

| Number of elements | Insertion | Search | Tranverse | Deletion |
| --- | --- | --- | --- | --- |
| 10^6 | 1789.994 | 1207.567 | 247.225 | 2116.248 |
| 10^7 | 19046.467 | 12289.392 | 2373.335 | 22051.428 |
| 10^8 | 197142.49 | 126769.23 | 24011.911 | 228485.792 |
