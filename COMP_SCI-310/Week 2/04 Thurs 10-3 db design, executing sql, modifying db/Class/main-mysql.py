
import logging
import sys
import pymysql


##################################################
# main
#
print('starting')
print()

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

try:
  #
  # Connection info for staff MySQL server in AWS: 
  #
  endpoint = 'nu-cs-msa-mysql.cb1xaky37wq8.us-east-2.rds.amazonaws.com'
  portnum = 3306
  username = 'movielens-read-only'
  pwd = 'abc123!!'
  dbname = 'movielens'

  dbConn = pymysql.connect(host=endpoint,
                           port=portnum,
                           user=username,
                           passwd=pwd,
                           database=dbname)
  
  dbCursor = dbConn.cursor()
  
  genre = input("Enter genre: ")
  
  sql = """
        select title, round(avg(rating),2) as rating
        from movies
        inner join ratings on movies.movie_id = ratings.movie_id
        inner join movie_genres on movies.movie_id = movie_genres.movie_id
        inner join genres on genres.genre_id = movie_genres.genre_id
        where genre_name = %s
        group by ratings.movie_id
        having count(rating) > 100
        order by rating desc, title asc
        limit 10;
        """
  
  dbCursor.execute(sql, [genre])
  rows = dbCursor.fetchall()
  
  for row in rows:
    print("Movie:", row[0], ", avg rating:", row[1]);

  dbCursor.close()
  dbConn.close()
  
except Exception as e:
  logging.error(e)

print()
print('done')


