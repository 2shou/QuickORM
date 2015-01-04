# coding: utf-8

import MySQLdb


class Field(object):
    pass


class Expr(object):
    def __init__(self, model, kwargs):
        self.model = model
        # How to deal with a non-dict parameter?
        self.params = kwargs.values()
        self.where_expr = 'where ' + ' and '.join(self.gen_equation_lst(kwargs.keys()))

    @staticmethod
    def gen_equation_lst(keys):
        return [key + ' = %s' for key in keys]

    def update(self, **kwargs):
        _keys = []
        _params = []
        for key, val in kwargs.iteritems():
            if val is None or key not in self.model.fields:
                continue
            _keys.append(key)
            _params.append(val)
        _params.extend(self.params)
        sql = 'update %s set %s %s;' % (self.model.db_table, ', '.join(self.gen_equation_lst(_keys)), self.where_expr)
        return Database.execute(sql, _params)

    def select(self):
        sql = 'select %s from %s %s;' % (', '.join(self.model.fields.keys()), self.model.db_table, self.where_expr)
        insts = []
        for row in Database.execute(sql, self.params).fetchall():
            inst = self.model()
            for idx, f in enumerate(row):
                setattr(inst, self.model.fields.keys()[idx], f)
            insts.append(inst)
        return insts

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
                                   db=db_config.get('database', 'test'))
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
    # connect database
    _db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'test'
    }
    Database.connect(**_db_config)

    # define model
    class TestModel(Model):
        db_table = 'test'  # point table name
        a = Field()
        b = Field()

    # create instance
    test = TestModel()
    test.a = 'john'
    test.b = 3
    test.save()

    # select
    for r in TestModel.where(a='john', b=3).select():
        print type(r)
        print r.a
        print r.b

    # update
    TestModel.where(a='john', b=3).update(b=1)