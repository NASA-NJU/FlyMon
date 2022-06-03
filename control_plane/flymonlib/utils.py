# -*- coding:UTF-8 -*-
import re
import math

class Node(object):
    def __init__(self, data):
        self.data = data
        self.parent = None
        self.left_child = None
        self.right_child = None

class TreeQueue(object):
    def __init__(self):
        self.__members = list()

    def is_empty(self):
        return not len(self.__members)

    def enter(self, data):
        self.__members.insert(0, data)

    def outer(self):
        if self.is_empty():
            return
        return self.__members.pop()

class PerfectBinaryTree(object):
    def __init__(self):
        self.__root = None
        self.prefix_branch = '├'
        self.prefix_trunk  = '|'
        self.prefix_leaf   = '└'
        self.prefix_empty  = ''
        self.prefix_left   = '─L─'
        self.prefix_right  = '─R─'

    def is_empty(self):
        return not self.__root

    def append(self, data):
        node = Node(data)
        if self.is_empty():
            self.__root = node
            return
        queue = TreeQueue()
        queue.enter(self.__root)
        while not queue.is_empty():
            cur = queue.outer()
            if cur.left_child is None:
                cur.left_child = node
                node.parent = cur
                return
            queue.enter(cur.left_child)
            if cur.right_child is None:
                cur.right_child = node
                node.parent = cur
                return
            queue.enter(cur.right_child)

    def root(self):
        return self.__root

    def inorderTraversal(self, root):
        res = []
        if root:
            res = self.inorderTraversal(root.left_child)
            res.append(root)
            res = res + self.inorderTraversal(root.right_child)
        return res

    def is_exist(self, data):
        if self.is_empty():
            return False
        queue = TreeQueue()
        queue.enter(self.__root)
        while not queue.is_empty():
            cur = queue.outer()
            if cur.data == data:
                return True
            if cur.left_child is not None:
                queue.enter(cur.left_child)
            if cur.right_child is not None:
                queue.enter(cur.right_child)
        return False

    def show_tree(self):
        if self.is_empty():
            print('Empty tree.')
            return
        print(self.__root.data)
        self.__print_tree(self.__root)

    def __print_tree(self, node, prefix=None):
        if prefix is None:
            prefix = ''
            prefix_left_child = ''
        else:
            prefix = prefix.replace(self.prefix_branch, self.prefix_trunk)
            prefix = prefix.replace(self.prefix_leaf, self.prefix_empty)
            prefix_left_child = prefix.replace(self.prefix_leaf, self.prefix_empty)
        if self.has_child(node):
            if node.right_child is not None:
                print(prefix + self.prefix_branch + self.prefix_right + str(node.right_child.data))
                if self.has_child(node.right_child):
                    self.__print_tree(node.right_child, prefix + self.prefix_branch + ' ')
            else:
                print(prefix + self.prefix_branch + self.prefix_right)
            if node.left_child is not None:
                print(prefix + self.prefix_leaf + self.prefix_left + str(node.left_child.data))
                if self.has_child(node.left_child):
                    prefix_left_child += '  '
                    self.__print_tree(node.left_child, self.prefix_leaf + prefix_left_child)
            else:
                print(prefix + self.prefix_leaf + self.prefix_left)

    def has_child(self, node):
        return node.left_child is not None or node.right_child is not None


def match_format_string(format_str, s):
    """Match s against the given format string, return dict of matches.

    We assume all of the arguments in format string are named keyword arguments (i.e. no {} or
    {:0.2f}). We also assume that all chars are allowed in each keyword argument, so separators
    need to be present which aren't present in the keyword arguments (i.e. '{one}{two}' won't work
    reliably as a format string but '{one}-{two}' will if the hyphen isn't used in {one} or {two}).

    We raise if the format string does not match s.

    Example:
    fs = '{test}-{flight}-{go}'
    s = fs.format('first', 'second', 'third')
    match_format_string(fs, s) -> {'test': 'first', 'flight': 'second', 'go': 'third'}
    """

    # First split on any keyword arguments, note that the names of keyword arguments will be in the
    # 1st, 3rd, ... positions in this list
    tokens = re.split(r'\{(.*?)\}', format_str)
    keywords = tokens[1::2]

    # Now replace keyword arguments with named groups matching them. We also escape between keyword
    # arguments so we support meta-characters there. Re-join tokens to form our regexp pattern
    tokens[1::2] = map(u'(?P<{}>.*)'.format, keywords)
    tokens[0::2] = map(re.escape, tokens[0::2])
    pattern = ''.join(tokens)

    # Use our pattern to match the given string, raise if it doesn't match
    matches = re.match(pattern, s)
    if not matches:
        raise Exception("Format string did not match")

    # Return a dict with all of our keywords and their values
    return {x: matches.group(x) for x in keywords}

def calc_keymapping(total_bitw, key_bitw, mem_type, mem_idx):
    """Calculate all key mapping according to location
    Args:
        total_bitw: total biw width of a cmu memory.
        key_bitw: int, 1 for whold, 2 for half, 3 for quartar...
        mem_idx: memory_idx on this type.
    Returns:
        a dict of mappings.
        key : (key, mask)
        val : offset (need to consider add overflow)
    NOTE:
        We implement SUB by ADD with ADD Overflow.
        Thus, all offsets will be a positive value and can cause overflow.
        Overflow is just we want to mimic the Sub translation.
    """
    key_mapping = {}
    mask_value = int('1'*(mem_type-1), base=2) << int(key_bitw - (mem_type-1))
    mem_range = int(2**total_bitw/2**(mem_type-1))
    for idx in range(2**(mem_type-1)):
        offset = (mem_idx - idx) * mem_range
        if offset != 0:
            match_value = idx << int(key_bitw - (mem_type-1))
            key_mapping[(match_value, mask_value)] = offset
    return key_mapping


        



