#### Dependency
`pip install mysql-connector-python`


#### Initialization

```Python
from database import create_db

db = create_db()
```

#### DB Tables
![db.png](https://s2.loli.net/2023/01/23/PYbzdoHpwhv5J3B.png)

#### API
##### Keypath
###### Query key-path

```Python
db.query_keypath(key=None)

Param:
    key: key=None <=> "SELECT * FROM KEYPATH"

Return：
    List[(key, path)]
    if not exist, return []
```

###### Put a pair of key-path in DB
```Python
# if found，update existing row
if db.query_keypath(key):
    db.update_keypath(key, path)
# if not found, add new row
else:
    db.add_keypath(key, path)
```

###### Delete all key-path rows
```Python
db.clear_keypath()
```

##### Memcacheconfig

###### Query memcache configuration

```Python
db.query_memcacheconfig()

Return:
    List[id, capacity, policy]
```
###### Update memcache configuration
```Python
db.update_memcacheconfig(data)

Params:
    data: List[capacity: float, policy: enum('RANDOM', 'LRU')] with length 2
```

##### Statistics

###### Query statistics

```Python
db.query_statistics()

Return:
    List[id, hit_rate, miss_rate, item_num, item_size]
```
###### Update Statistics
```Python
db.update_statistics(data)

Params:
    data: List[hit_rate: float, miss_rate: float, item_num: int, item_size: float] with length 4
```




