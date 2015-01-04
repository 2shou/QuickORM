# coding: utf-8

from numbers import Number
from datetime import date

import MySQLdb


class Field(object):
    pass


def normalize(val):
    if not val or isinstance(val, basestring):
        return val
    elif isinstance(val, date):
        return val.strftime('%Y-%m-%d')
    elif isinstance(val, Number):
        return str(val)


class Expr(object):
    def __init__(self, model, kwargs):
        self.model = model
        elst = self.normalize(kwargs)
        self.wexpr = '' if len(elst) == 0 else 'where %s' % ' and '.join(elst)

    def normalize(self, fdct):
        def format(x):
            if isinstance(x, basestring):
                return '\'%s\'' % x
            if isinstance(x, date):
                return '\'%s\'' % x.strftime('%Y-%m-%d')
            if isinstance(x, Number):
                return str(x)

        return ['%s = %s' % (key, format(val)) for key, val in fdct.iteritems() if
                val is not None and key in self.model.fields]

    def update(self, **kwargs):
        set_elements = []
        params = []
        for key, val in kwargs.iteritems():
            if val is None or key not in self.model.fields:
                continue
            set_elements.append(key + ' = %s')
            params.append(format(val))
        sql = 'update %s set %s %s;' % (self.model.db_table, ', '.join(set_elements), self.wexpr)
        return Database.execute(sql, params)

    def select(self):
        sql = 'select %s from %s %s;' % (', '.join(self.model.fields.keys()), self.model.db_table, self.wexpr)
        ilst = []
        for r in Database.execute(sql).fetchall():
            inst = self.model()
            for idx, f in enumerate(r):
                setattr(inst, self.model.fields.keys()[idx], f)
            ilst.append(inst)
        return ilst

    def count(self):
        sql = 'select count(*) from %s %s;' % (self.model.db_table, self.wexpr)
        (row_cnt, ) = Database.execute(sql).fetchone()
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
        rand_field = self.fields.keys()[0]
        insert = 'insert into %s(%s) values (%s) on duplicate key update %s = %s;' % (
            self.db_table, ', '.join(self.__dict__.keys()), ', '.join(['%s'] * len(self.__dict__)), rand_field,
            rand_field)
        return Database.execute(insert, tuple([normalize(val) for val in self.__dict__.values()]))

    @classmethod
    def where(cls, **kwargs):
        return Expr(cls, kwargs)


class Database(object):
    autocommit = True
    conn = None

    @classmethod
    def connect(cls, **db_config):
        cls.conn = MySQLdb.connect(**db_config)
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


if __name__ == '__main__':
    class TestModel(Model):
        db_table = 'test'
        a = Field()
        b = Field()

    test = TestModel()
    test.a = 5
    test.b = 3
    test.save()
    TestModel.where(a=5, b=3).update(a=1)
