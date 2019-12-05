import mysql.connector

def writeToDB(bag):
    file_name, dataset, label, status, score, time, actual_str, detected_str = bag
    deleteExistingPrimaryKeyDB(file_name, dataset, label)
    db_conn = mysql.connector.connect(host="localhost", user="root", passwd="1234",  database='cs670research')
    db_cursor = db_conn.cursor(buffered=True)
    insert_query = "INSERT INTO research_exploration VALUES('{}', '{}', '{}', '{}', '{}', '{}', \"{}\", \"{}\")".format \
    (file_name, dataset, label, str(status), str(score), str(time), actual_str, detected_str)
    db_cursor.execute(insert_query)
    db_conn.commit()
    db_cursor.close()
    db_conn.close()
    #print ("Successfully written to the database...")
    return

def deleteExistingPrimaryKeyDB(file_name, dataset, label):
    db_conn = mysql.connector.connect(host="localhost", user="root", passwd="1234",  database='cs670research')
    db_cursor = db_conn.cursor(buffered=True)
    delete_query = "DELETE FROM research_exploration WHERE file_name='{}' and dataset='{}' and label='{}'".format \
    (file_name, dataset, label)
    db_cursor.execute(delete_query)
    db_conn.commit()
    db_cursor.close()
    db_conn.close()
    #print ("Successfully deleted the existing primary key...")
    return

def countExistingRecords(file_name, dataset, label):
    db_conn = mysql.connector.connect(host="localhost", user="root", passwd="1234",  database='cs670research')
    db_cursor = db_conn.cursor(buffered=True)
    count_query = "select count(*) from research_exploration WHERE file_name='{}' and dataset='{}' \
    and label='{}'".format(file_name, dataset, label)
    db_cursor.execute(count_query)
    records = db_cursor.fetchall()[0][0]
    db_cursor.close()
    db_conn.close()
    return records

def recordsExists(file_name, dataset, label):
    present_count = countExistingRecords(file_name, dataset, label)
    return True if present_count > 0 else False
