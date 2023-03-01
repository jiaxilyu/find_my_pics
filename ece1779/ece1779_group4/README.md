### ece1779_group4_a1

#### Installation
```git clone git@github.com:jiaxilyu/ece1779_group4.git```

<br>

#### Run Web Service
**1. Create virtualenv**
```python3 -m venv venv```

**2. Activate virtualenv**
```source venv/bin/activate```

**3. Install dependency**
```pip install -r requirements.txt```

**4. Start**
```./start.sh```

**5. Shutdown**
```./shutdown.sh```

<br>

#### Run Performance Test

**1. Activate virtualenv**
```source venv/bin/activate```

**2. Switch directory**
```cd perftest```

**3. Start**
```python3 perf_test.py```