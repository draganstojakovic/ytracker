class Criteria:

    def __init__(self):
        self._filter = ''
        self._ordering = ''

    def __str__(self):
        if self._filter == '' and self._ordering == '':
            return ''
        filter_query = self._filter.strip()
        if filter_query.endswith('AND'):
            filter_query = filter_query[:-3]
        elif filter_query.endswith('OR'):
            filter_query = filter_query[:-2]
        order = self._ordering.strip()
        return f"{filter_query.strip()} {order}".strip()

    def where(self, statement: str, log_op=None):
        if log_op is None:
            log_op = 'AND '
        else:
            log_op = log_op.upper()
            log_op = 'OR ' if log_op == 'OR' else 'AND '
        if self._filter.startswith('WHERE'):
            self._filter += f'{statement} {log_op}'
        else:
            self._filter += f'WHERE {statement} {log_op}'
        return self

    def order_by(self, column_name: str, order=''):
        order = order.upper()
        order = 'DESC' if order == 'DESC' else ''
        if self._ordering.startswith('ORDER'):
            self._ordering = self._ordering.strip()
            self._ordering += f', {column_name} {order}'
        else:
            self._ordering += f'ORDER BY {column_name} {order}'
        return self
