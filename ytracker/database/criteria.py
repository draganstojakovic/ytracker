class Criteria:

    __slots__ = ('_where', '_order_by')

    def __init__(self):
        self._where = ''
        self._order_by = ''

    def __str__(self):
        if self._where == '' and self._order_by == '':
            return ''
        filter_query: str = self._where.strip()
        if filter_query.endswith('AND'):
            filter_query = filter_query[:-3]
        elif filter_query.endswith('OR'):
            filter_query = filter_query[:-2]
        order = self._order_by.strip()
        return f"{filter_query.strip()} {order}".strip()

    def where(self, statement: str, log_op='AND') -> 'Criteria':
        log_op: str = 'OR ' if log_op.upper() == 'OR' else f'{log_op} '
        where: str = '' if self._where.startswith('WHERE') else 'WHERE '
        self._where += f'{where}{statement} {log_op}'
        return self

    def order_by(self, column_name: str, order='') -> 'Criteria':
        order: str = 'DESC' if order.upper() == 'DESC' else ''
        if self._order_by.startswith('ORDER BY'):
            self._order_by = self._order_by.strip()
            self._order_by += f', {column_name} {order}'
        else:
            self._order_by += f'ORDER BY {column_name} {order}'
        return self
