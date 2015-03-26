# coding: utf-8

import MySQLdb


class Field(object):
    pass


class Expr(object):
    def __init__(self, model, kwargs):
        self.model = model
        # How to deal with a non-dict parameter?
        self.params = kwargs.values()
        equations = [key + ' = %s' for key in kwargs.keys()]
        self.where_expr = 'where ' + ' and '.join(equations) if len(equations) > 0 else ''

    def update(self, **kwargs):
        _keys = []
        _params = []
        for key, val in kwargs.iteritems():
            if val is None or key not in self.model.fields:
                continue
            _keys.append(key)
            _params.append(val)
        _params.extend(self.params)
        sql = 'update %s set %s %s;' % (
            self.model.db_table, ', '.join([key + ' = %s' for key in _keys]), self.where_expr)
        return Database.execute(sql, _params)

    def limit(self, rows, offset=None):
        self.where_expr += ' limit %s%s' % (
            '%s, ' % offset if offset is not None else '', rows)
        return self

    def select(self):
        sql = 'select %s from %s %s;' % (', '.join(self.model.fields.keys()), self.model.db_table, self.where_expr)
        for row in Database.execute(sql, self.params).fetchall():
            inst = self.model()
            for idx, f in enumerate(row):
                setattr(inst, self.model.fields.keys()[idx], f)
            yield inst

    def count(self):
        sql = 'select count(*) from %s %s;' % (self.model.db_table, self.where_expr)
        (row_cnt, ) = Database.execute(sql, self.params).fetchone()
        return row_cnt


class MetaModel(type):
    db_table = None
    fields = {}

    def __init__(cls, name, bases, attrs):
        super(MetaModel, cls).__init__(name, bases, attrs)
        fields = {}
        for key, val in cls.__dict__.iteritems():
            if isinstance(val, Field):
                fields[key] = val
        cls.fields = fields
        cls.attrs = attrs


class Model(object):
    __metaclass__ = MetaModel

    def save(self):
        insert = 'insert ignore into %s(%s) values (%s);' % (
            self.db_table, ', '.join(self.__dict__.keys()), ', '.join(['%s'] * len(self.__dict__)))
        return Database.execute(insert, self.__dict__.values())

    @classmethod
    def where(cls, **kwargs):
        return Expr(cls, kwargs)


class Database(object):
    autocommit = True
    conn = None

    @classmethod
    def connect(cls, **db_config):
        cls.conn = MySQLdb.connect(host=db_config.get('host', 'localhost'), port=db_config.get('port', 3306),
                                   user=db_config.get('user', 'root'), passwd=db_config.get('password', ''),
                                   db=db_config.get('database', 'test'), charset=db_config.get('charset', 'utf8'))
        cls.conn.autocommit(cls.autocommit)

    @classmethod
    def get_conn(cls):
        if not cls.conn or not cls.conn.open:
            cls.connect()
        try:
            cls.conn.ping()
        except MySQLdb.OperationalError:
            cls.connect()
        return cls.conn

    @classmethod
    def execute(cls, *args):
        cursor = cls.get_conn().cursor()
        cursor.execute(*args)
        return cursor

    def __del__(self):
        if self.conn and self.conn.open:
            self.conn.close()


def execute_raw_sql(sql, params=None):
    return Database.execute(sql, params) if params else Database.execute(sql)
