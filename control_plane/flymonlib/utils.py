# -*- coding:UTF-8 -*-
import re
import math
import json

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

def calc_keymapping(total_bitw, mem_type, mem_idx):
    """Calculate all key mapping according to location
    Args:
        total_bitw: total biw width of a cmu memory. (address bit width)
        mem_type: int, 1 for whold, 2 for half, 3 for quartar...
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
    if mem_type == 1:
        return {(0,0) : 0}
    key_mapping = {}
    mask_value = int('1'*(mem_type-1), base=2) << int(total_bitw - (mem_type-1))
    mem_range = int(2**total_bitw/2**(mem_type-1))
    for idx in range(2**(mem_type-1)):
        offset = (mem_idx - idx) * mem_range
        if offset != 0:
            match_value = idx << int(total_bitw - (mem_type-1))
            key_mapping[(match_value, mask_value)] = (offset+2**total_bitw)%(2**total_bitw)
    return key_mapping

def parse_filter(filter_str):
    """
    Args:
        filter_std: e.g., a.b.c.d/32,a.b.c.d/24
    Returns:
        [(a.b.c.d, 255.255.0.0), (0.0.0.0, 0.0.0.0)]
    """
    filters = ["src_filter",  "dst_filter"]
    results = []
    try:
        re_step1 = match_format_string("{src_filter},{dst_filter}", filter_str)
        for filter in filters:
            if re_step1[filter] == "*":
                results.append(("0.0.0.0", "0.0.0.0"))
            else:
                if '/' in re_step1[filter]:
                    re_step2 = match_format_string("{ip}/{prefix}", re_step1[filter])
                    ip = re_step2['ip']
                    prefix = int(re_step2['prefix'])
                    if prefix > 32 or prefix < 0 or len(ip)<7 or len(ip)>15:
                        raise RuntimeError()
                    mask = '1' * prefix + '0' * (32-prefix)
                    splt_mask = []
                    temp = ''
                    for idx, bit in enumerate(mask):
                        if idx != 0 and idx % 8 == 0:
                            splt_mask.append(temp)
                            temp = ''
                        else:
                            temp += bit
                    splt_mask.append(temp)
                    results.append((ip, f"{int(splt_mask[0], base=2)}.{int(splt_mask[1], base=2)}.{int(splt_mask[2], base=2)}.{int(splt_mask[3], base=2)}"))
                else:
                    results.append((re_step1[filter], "255.255.255.255"))
    except Exception as e:
        raise RuntimeError("Invalid filter format, example: 10.0.0.0/8,20.0.0.0/16 or 10.0.0.0/8,* or *,*")
    return results

def s2d(d, count = 1000):
    #convert string key to tuple.
    limit = count
    new_d = {}
    for key in list(d.keys()):
        try:
            new_d[eval(key)] = d[key]
            limit -= 1
            if limit == 0:
                return new_d
        except Exception:
            continue
    return new_d


def tuplize_keys(d):
    # s2d(d['flow_set_ip_pair'])
    # s2d(d['flow_set_5_tuple'])
    d['ip_pair_pkt_cnt_table'] = s2d(d['ip_pair_pkt_cnt_table'])
    # s2d(d['5_tuple_pkt_cnt_table'])
    # s2d(d['ip_pair_flow_size_table'])
    # s2d(d['5_tuple_flow_size_table'])
    return d

def loadJsonToDict(js_file):
    js_dict = dict()
    with open(js_file) as js:
        js_dict = json.load(js)
    return tuplize_keys(js_dict)
    # return js_dict