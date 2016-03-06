import psycopg2 as connector
from settings import db_params

db = None
try:
    db = connector.connect(**db_params['DEFAULT'])
except:
    db = connector.connect(**db_params['ALTERNATIVE'])


class TooManyRoots(Exception):
    pass


class NoRowsFound(Exception):
    pass


def db_connected(func):
    def func_wrapper(*args, **kwargs):
        return func(db=db, *args,  **kwargs)
    return func_wrapper


class Model(object):
    """
    Модель - базовый класс для представления записей БД в виде набора объектов
    Python.
    """

    class _objects_(object):
        """
        Менеджер объектов. Доступен как атрибут objects произвольного
        экземпляра класса.
        """

        def __init__(self, db, obj, db_table, pk_name, select_list):
            self.outer_obj = obj
            self.db_table = db_table
            self.select_list = select_list # tuple
            self.db = db
            self.pk_name = pk_name

        def _fetch_(self, **kwargs):
            """
            Итератор на основе sql-оператора select.
            :param kwargs:
            :return:
            """

            sql = 'select {} from {} where 1=1 {}'
            cursor = db.cursor()
            sel_list = kwargs.get('select_list', ())  # список имен колонок
            # таблицы
            if not sel_list:
                sel_list = self.select_list
            where_clause_dict = kwargs.get('where_clause', {})  # словарь
            # типа "колонка таблицы"=<значение> для формирования условий
            # отбора по колонкам
            where_clause_raw = kwargs.get('where_clause_raw', '')  # строка со
            #  сложными условиями отбора (начинается с ' and')
            where_clause = ' '
            if where_clause_dict:
                for k, v in where_clause_dict.items():
                    if isinstance(v, str):
                        # для строковых значений
                        where_clause += ' and {}="{}"'.format(k, v)
                    else:
                        # для числовых значений
                        where_clause += ' and {}={}'.format(k, v)
            where_clause += where_clause_raw
            print(sql.format(','.join(sel_list), self.db_table,
                                 where_clause))
            cursor.execute(sql.format(','.join(sel_list), self.db_table,
                                 where_clause))
            for row in cursor.fetchall():
                row_object = self.outer_obj.__class__(**dict([(k, v) for k, v
                                                          in zip(
                    sel_list, row)]))
                yield row_object

        def all(self):
            """
            Итератор по всем записям модели
            :return:
            """
            return self._fetch_()

        def find(self, where_clause_raw='', **kwargs):
            """
            Итератор по записям, удовлетворяющим условиям отбора
            :param where_clause_raw:
            :param kwargs:
            :return:
            """
            return self._fetch_(where_clause=kwargs,
                                where_clause_raw=where_clause_raw)

        def get(self, pk_id: int):
            '''
            Генератор объекта по id первичного ключа или oid
            :param pk_id:
            :return:
            '''
            obj = None
            if pk_id is isinstance(pk_id, str):
                for o in self._fetch_(where_clause={self.pk_name: '"' + pk_id
                                                                      + '"'}):
                    obj = o
            else:
                for o in self._fetch_(where_clause={self.pk_name: pk_id}):
                    obj = o
            return obj

    def __init__(self, *, db_table, pk_name, select_list, **fields):
        self.params = fields
        self.objects = self._objects_(db, self, db_table, pk_name, select_list)
        # print(self.params)
        for key, val in fields.items():
            setattr(self, key, val)

    def __dict__(self):
        return self.params

