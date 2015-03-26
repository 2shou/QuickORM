from data_handler import Database, Model, Field, execute_raw_sql

# connect database
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'test'
}
Database.connect(**db_config)


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
for r in TestModel.where(a='john', b=3).limit(1, offset=2).select():
    print type(r)
    print r.a
    print r.b

# update
TestModel.where(a='john', b=3).update(b=1)

# execute raw sql
results = execute_raw_sql('select b, count(*) from test where b = %s group by b;', (1,))
for val, cnt in results:
    print val, cnt