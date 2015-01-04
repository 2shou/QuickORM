QuickORM
========

A simple ORM provides elegant API for Python-MySQL operation

Connect to MySQL
----------------

```python
from data_handler import Database

db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'test'
}
Database.connect(**db_config)
```

Define a model
--------------

```python
from data_handler import Model, Field

class TestModel(Model):
  db_table = 'test'
  a = Field()
  b = Field()
```

Insert
------

```python
test = TestModel()
test.a = 5
test.b = 'john'
test.save()
```

Query
-----

```python
for r in TestModel.where(a=5, b='john').select():
  print r.a
  print r.b
```

Count
-----

```python
print TestModel.where(a=5, b='john').count()
```

Update
------

```python
TestModel.where(a=5, b='john').update(a=1)
```

Execute raw SQL
---------------

```python
from data_handler import execute_raw_sql

results = execute_raw_sql('select b, count(*) from test where b = %s group by b;', (1,))
for val, cnt in results:
  print val, cnt
```