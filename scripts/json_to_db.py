import pandas as pd
import sqlite3
import time

sqlite_file = f"yelp_academic_dataset.db"
conn = sqlite3.connect(sqlite_file)

tables = ["business","review","user"]
for table  in tables:
    start = time.time()
    json_file = f"/home/mir/flask_yelp/static/yelp_dataset/yelp_academic_dataset_{table}.json"
    print(f"processing {json_file}... ")
    df = pd.DataFrame()
    chunks = pd.read_json(json_file,lines=True,chunksize = 10000)
    for chunk in chunks:
        
        df = pd.concat([df,chunk])

    # df.to_sql(name = table,con=conn,index=True, if_exists='replace')
    df.to_csv(f'{table}.csv' )
    temp_df = pd.read_csv(f'{table}.csv')
    temp_df.to_sql(name = table,con=conn,index=True, if_exists='replace')
    end = time.time()
    print(f"Elapsed: {(end - start)/60} min ")
conn.close()
