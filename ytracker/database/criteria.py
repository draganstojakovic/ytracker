class Criteria:
    _WHERE = 'WHERE'
    _ORDER_BY = 'ORDER BY'
    _AND = 'AND'
    _OR = 'OR'
    _DESC = 'DESC'

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

    def where(self, statement: str, log_op='AND'):
        log_op = f'{self._OR} ' if log_op.upper() == self._OR else f'{log_op} '
        where = '' if self._filter.startswith(self._WHERE) else f'{self._WHERE} '
        self._filter += f'{where}{statement} {log_op}'
        return self

    def order_by(self, column_name: str, order=''):
        order = self._DESC if order.upper() == self._DESC else ''
        if self._ordering.startswith(self._ORDER_BY):
            self._ordering = self._ordering.strip()
            self._ordering += f', {column_name} {order}'
        else:
            self._ordering += f'{self._ORDER_BY} {column_name} {order}'
        return self
