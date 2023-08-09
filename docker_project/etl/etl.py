"""
Example file to simulate an ETL process within a docker pipeline
- Extracts from a mongo db
- Transforms the collections
- Loads the transformed collections to postgres db

To be started by docker (see ../docker-compose.yml)

For inspecting that ETL worked out: docker exec -it pipeline_example_my_postgres_1 psql -U postgres
"""

import pymongo
import sqlalchemy  # use a version prior to 2.0.0 or adjust creating the engine and df.to_sql()
import psycopg2
import time
import logging
import pandas as pd
#import vaderSentiment
from credentials_reddit import login_psql
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# mongo db definitions; setze Mongo Database auf hier
client = pymongo.MongoClient('my_mongo', port=27017)  # my_mongo is the hostname (= service in yml file)
db = client.my_db
dbcoll = db.my_collection        #these objects allow me to interact with the mongodb database

# postgres db definitions. HEADS UP: outsource these credentials and don't push to github.
#USERNAME_PG = 'postgres'
#PASSWORD_PG = 'postgres'
#HOST_PG = 'my_postgres'  # my_postgres is the hostname (= service in yml file)
#PORT_PG = 5432
#DATABASE_NAME_PG = 'reddits_pgdb'  #name von postgres db

#connecting to the postgresql database, the above variables help set up the connection:
#it will look like this: postgresql://postgres:postgres@my_postgres:5432/reddits_pgdb
conn_string_pg = f"postgresql://{login_psql['USERNAME_PG']}:{login_psql['PASSWORD_PG']}@{login_psql['HOST_PG']}:{login_psql['PORT_PG']}/{login_psql['DATABASE_NAME_PG']}"

#not needed step
time.sleep(7)  # safety margine to ensure running postgres server, 3 sekunden

pg = sqlalchemy.create_engine(conn_string_pg).connect()    #pq is used to feed the data to postgres
logging.critical("successfully connected to postgres")


# Create the table
create_table_string = sqlalchemy.text("""CREATE TABLE IF NOT EXISTS reddits(reddit TEXT, sentiment NUMERIC);""")


# create_table_string = sqlalchemy.text("""CREATE TABLE IF NOT EXISTS reddits (
#                                         time TEXT,
#                                         reddit TEXT,
#                                         sentiment NUMERIC
#                                         );
#                                     """)

pg.execute(create_table_string)
pg.commit() #postgres engine

def extract():
    """
    reads collections from a mongo database and converts them into a pandas
    dataframe.

    Returns
    -------
    new_reddits : pandas dataframe

    """

    new_mongo_docs = dbcoll.find()
    logging.critical(new_mongo_docs)

    new_reddits = pd.DataFrame.from_records(list(new_mongo_docs))
    logging.critical(new_reddits)
    #print(new_reddits)
    new_reddits.to_csv("table_reddit.csv")
    n_reddits = new_reddits.shape[0]

    logging.critical(f"\n---- {n_reddits} reddits extracted ----\n")
    return new_reddits

    print(new_reddits)


def transform(new_reddits):
    analyser = SentimentIntensityAnalyzer()

    #   return tweet
    """
    transforms a dataframe containing reddits in a dictionary to a clean
    dataframe and adds a column for the (dummy/length) sentiment of the reddit

    Parameters
    ----------
    new_reddits : unclean pandas dataframe

    Returns
    -------
    new_reddits_df : cleaned pandas dataframe including "sentiments"
    """

    new_reddits_df = pd.DataFrame()

    for _, row in new_reddits.iterrows():
        new_reddits_df = new_reddits_df._append(row['reddit'], ignore_index=True) #reddit?

    regex='(https?:\/\/\S+)*(\\n)'
    for reddit_text in new_reddits_df.iterrows():
        re.sub(regex, '', reddit_text)

    # as a placeholder for the sentiment: add length of reddit to dataframe
        pol_scores = new_reddits_df['reddit'].apply(analyser.polarity_scores).apply(pd.Series)

#this triggers loger statements: try - except
    try:
        new_reddits_df['sentiment'] = pol_scores['compound']
        logging.critical("\n---- transformation completed ----\n")
    except:
        logging.critical("\n---- no reddits to transform ----\n")

    # try:
    #     new_reddits_df['sentiment'] = new_reddits_df['reddit'].str.len()               #append the sentiment score
    #     logging.critical("\n---- transformation completed ----\n")
    # except:
    #     logging.critical("\n---- no reddits to transform ----\n")

    return new_reddits_df



def load(new_reddits_df):
    """
    saves cleaned reddits including their sentiments to a postgres database

    Returns
    -------
    None.

    """

    if new_reddits_df.shape[0] > 0:  # only export if new reddits exist
        new_reddits_df.to_sql('reddits', pg, if_exists='append', index=False)  #pq name of the connection created

    logging.critical("\n---- new reddits loaded to postgres db ----\n")

    return None





new_reddits = extract()

new_reddits_df = transform(new_reddits)

load(new_reddits_df)