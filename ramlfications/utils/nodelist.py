from .. import errors


class NodeList(list):
    """List with attribute filtering capabilities

        Example::

            class Person(object):
                def __init__(self, first_name, last_name):
                    self.first_name = first_name
                    self.last_name = last_name

            >>> musk = Person(first_name='Elon', last_name='Musk')
            >>> torvalds = Person(first_name='Linus', last_name='Torvalds')
            >>> svensson = Person(first_name='Linus', last_name='Svensson')
            >>> persons = NodeList([musk, torvalds, svensson])

            >>> persons.first()
            Person('Elon Musk')

            >>> linuses = persons.filter_by(first_name='Linus')
            FilteredList([Person('Linus Torvalds'), Person('Linus Svensson')])

            >>> linuses.filter_by(last_name='Svensson').one()
            Person('Linus Svensson')

            >>> linuses.first()
            Person('Linus Torvalds')
    """

    def __repr__(self):
        return 'NodeList({0})'.format(super(NodeList, self).__repr__())

    def filter_by(self, **filters):
        """
        Filter the list's objects based on their attributes' values, or their
        keys' values if the objects are instances of :py:class:`dict`.

        Args:
            filters (dict):
                A dictionary that should be used for filtering the list's
                objects. The keys should correspond to the objects attributes.
        Raises:
            :py:class:`InvalidNodeListFilterKey`:
                When a filter key is passed in that could not be matched
                to any of the child's attributes.
        Returns:
            :py:class:`NodeList`:
                The new filtered list.
        """
        new_nodes = NodeList()
        is_dict = None
        for i, node in enumerate(self):
            if i == 0:
                is_dict = isinstance(node, dict)
            num_matches = 0
            for attr_name, value in filters.items():
                try:
                    if is_dict:
                        attr = node[attr_name]
                    else:
                        attr = getattr(node, attr_name)
                except (AttributeError, KeyError) as exc:
                    raise errors.InvalidNodeListFilterKey(*exc.args)
                if attr == value:
                    num_matches += 1
            if num_matches == len(filters):
                new_nodes.append(node)
        return new_nodes

    def one(self):
        """
        Get one item in the list, or raise an exception if less or more than
        one item was found.

        Raises:
            :py:class:`NoNodeFound`:
                When no node was found.
            :py:class:`MultipleNodesFound`:
                When multiple nodes were found.
        Returns:
            Any:
                The first node in the list.
        """
        if len(self) > 1:
            raise errors.MultipleNodesFound(
                'Multiple nodes were found for one()'
            )
        try:
            return self[0]
        except IndexError:
            raise errors.NoNodeFound('No node was found for one()')

    def first(self):
        """Like one(), but doesn't raise any exception.

        Returns:
            Any:
                The first node in the list, or `None` if no node was found.
        """
        try:
            return self[0]
        except IndexError:
            return None
