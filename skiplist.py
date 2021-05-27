"""A skip list implement.

"""

import random
import math


MAX_LEVEL = 32
HEAD = object()


class SkipListLink:

    def __init__(self, skpln):
        self.prev = None
        self.next = None
        self.skp_list_node = skpln

    def __str__(self):
        return f'<SkipListLink of {str(self.skp_list_node)}>'


class SkipListNode:

    def __init__(self, key, value, level):
        self.key = key
        self.value = value
        links = []
        for _ in range(level):
            links.append(SkipListLink(self))
        # cprofile said this have a high performace loss 
        # self.link = [SkipListLink(self) for i in range(level)]
        self.link = links

    @property
    def prev(self):
        link = self.link[0]
        return link.next.skp_list_node

    @property
    def next(self):
        link = self.link[0]
        return link.next.skp_list_node

    def __str__(self):
        return f'<SkipListNode {self.key}>'


class Skiplist:
    """A skip list implement.

    """

    def __init__(self, max_level=MAX_LEVEL):
        self._length = 0
        self._level = 1
        self._max_level = self._make_max_level(max_level)
        self._head = [SkipListLink(HEAD) for i in range(self._max_level)]
        self._nodes = []

    def _make_max_level(self, level):
        if level >= MAX_LEVEL:
            return level
        if level <= 0:
            raise ValueError(f'max_level should greater than 0 got {level}')

    def _random_level(self):
        level = 1
        while random.randint(1, 32767) & 0xffff < 0xffff * 0.25:
            level += 1
        return level if level <= self._max_level else self._max_level

    def _random_level1(self):
        level = int(math.log(1. - random.random()) / math.log(1. - 0.25))
        return level if level <= MAX_LEVEL else MAX_LEVEL

    def create_null_node(self, max_level):
        return Skiplist.create_node(None, None, max_level)

    @classmethod
    def create_node(cls, key, value, level):
        node = SkipListNode(key, value, level)
        return node

    @property
    def max_level(self):
        return self._max_level
    
    @property
    def level(self):
        return self._level

    @property
    def length(self):
        return self._length

    def _insert_node(self, node, level, prev, next):
        node.link[level].next = next
        node.link[level].prev = prev
        if next is not None:
            next.prev = node.link[level]
        prev.next = node.link[level]

    def insert(self, key, value):
        level = self._random_level()
        if level > self._level:
            self._level = level

        node = Skiplist.create_node(key, value, level)
        level_pointer = self._level - 1
        head_link = self._head[level_pointer]
        tail_link = None

        while level_pointer >= 0:
            dummy_head_link = head_link
            head_link = head_link.next

            while head_link is not None:
                head_node = head_link.skp_list_node
                if head_node.key >= key:
                    tail_link = head_node.link[level_pointer]
                    break

                dummy_head_link = head_link
                head_link = head_link.next

            # relocate the position
            if tail_link is not None:
                head_link = tail_link.prev
            else:
                head_link = dummy_head_link

            if level_pointer < level:
                self._insert_node(node, level_pointer, head_link, tail_link)

            # level decendding while keepping the relocated position
            level_pointer -= 1
            if level_pointer < 0:
                break

            if head_link.skp_list_node is not HEAD: 
                head_link = head_link.skp_list_node.link[level_pointer]
            else:
                head_link = self._head[level_pointer]

            if tail_link and tail_link.skp_list_node:
                tail_link = tail_link.skp_list_node.link[level_pointer]

        self._nodes.append(node)
        self._length += 1

    def search(self, k, key=None):
        level_pointer = self._level - 1
        head_link = self._head[level_pointer]
        tail_link = None

        while level_pointer >= 0:
            dummy_head_link = head_link
            head_link = head_link.next
            while is_not_none(head_link):
                head_node = head_link.skp_list_node
                if head_node.key >= k:
                    tail_link = head_node.link[level_pointer]
                    break
                dummy_head_link = head_link
                head_link = head_link.next

            if head_node and head_node.key == k:
                return head_node

            # relocate the position
            if tail_link is not None:
                head_link = tail_link.prev
            else:
                head_link = dummy_head_link

            # level decendding while keepping the relocated position
            level_pointer -= 1
            if head_link.skp_list_node is not HEAD: 
                head_link = head_link.skp_list_node.link[level_pointer]
            else:
                head_link = self._head[level_pointer]

            if tail_link and tail_link.skp_list_node:
                tail_link = tail_link.skp_list_node.link[level_pointer]

    def echo(self, brief=None):
        if callable(brief):
            brief = brief
        else:
            brief = lambda x: x #noqa

        head = self._head[0].next
        while head is not None:
            print(head.skp_list_node.key, brief(head.skp_list_node.value), '->')
            head = head.next

    @classmethod
    def build_from_list(cls, array, key_getter=None):
        make_key = callable(key_getter)
        skpl = Skiplist()
        idx = 0
        for ele in array:
            if make_key:
                skpl.insert(key_getter(ele), ele)
            else:
                skpl.insert(idx, ele)
                idx += 1
        return skpl

    @classmethod
    def build_from_dict(cls, hash_table):
        skpl = Skiplist()
        for k, v in hash_table.items():
            skpl.insert(k, v)
        return skpl
