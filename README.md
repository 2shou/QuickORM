QuickORM
========

一个简洁的ORM框架，优雅地使用SQL

连接数据库
----------

```
from data_handler import Database
Database.connect(host='localhost', port=3306, user='root', passwd='123456')
```

定义模型
--------

```
class TestModel(Model):
  db_table = 'test'
  a = Field()
  b = Field()
```

插入
----

```
test = TestModel()
test.a = 5
test.b = 'john'
test.save()
```

查询
----

```
TestModel.where(a=5, b='john').select()
```

更新
----

```
TestModel.where(a=5, b='john').update(a=1)
```
