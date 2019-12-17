import mysql.connector

def writeToDB(bag):
    file_name, dataset, label, severity, noise_type, status, score, time, actual_str, detected_str = bag
    deleteExistingPrimaryKeyDB(file_name, dataset, label, severity, noise_type)
    db_conn = mysql.connector.connect(host="localhost", user="root", passwd="1234",  database='cs670research')
    db_cursor = db_conn.cursor(buffered=True)
    insert_query = "INSERT INTO research_exploration1 VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', \"{}\", \"{}\")".format(file_name, dataset, label, severity, noise_type, str(status), str(score), str(time), actual_str, detected_str)
    db_cursor.execute(insert_query)
    db_conn.commit()
    db_cursor.close()
    db_conn.close()
    #print ("Successfully written to the database...")
    return

def writeToDB_label(bag):
    file_name, dataset, label, severity, noise_type, status, score1, score2, score3, time, actual_str, detected_str = bag
    deleteExistingPrimaryKeyDB_label(file_name, dataset, label, severity, noise_type)
    db_conn = mysql.connector.connect(host="localhost", user="root", passwd="1234",  database='cs670research')
    db_cursor = db_conn.cursor(buffered=True)
    insert_query = "INSERT INTO research_exploration_label1 VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', \"{}\", \"{}\")".format (file_name, dataset, label, severity, noise_type, str(status), str(score1), str(score2), str(score3), str(time), actual_str, detected_str)
    db_cursor.execute(insert_query)
    db_conn.commit()
    db_cursor.close()
    db_conn.close()
    #print ("Successfully written to the database...")
    return

def deleteExistingPrimaryKeyDB(file_name, dataset, label, severity, noise_type):
    db_conn = mysql.connector.connect(host="localhost", user="root", passwd="1234",  database='cs670research')
    db_cursor = db_conn.cursor(buffered=True)
    delete_query = "DELETE FROM research_exploration1 WHERE file_name='{}' and dataset='{}' and label='{}' and severity='{}' and noise_type='{}'".format (file_name, dataset, label, severity, noise_type)
    db_cursor.execute(delete_query)
    db_conn.commit()
    db_cursor.close()
    db_conn.close()
    #print ("Successfully deleted the existing primary key...")
    return

def deleteExistingPrimaryKeyDB_label(file_name, dataset, label, severity, noise_type):
    db_conn = mysql.connector.connect(host="localhost", user="root", passwd="1234",  database='cs670research')
    db_cursor = db_conn.cursor(buffered=True)
    delete_query = "DELETE FROM research_exploration_label1 WHERE file_name='{}' and dataset='{}' and label='{}' and severity='{}' and noise_type='{}'".format (file_name, dataset, label, severity, noise_type)
    db_cursor.execute(delete_query)
    db_conn.commit()
    db_cursor.close()
    db_conn.close()
    #print ("Successfully deleted the existing primary key...")
    return

def countExistingRecords(file_name, dataset, label, severity, noise_type):
    db_conn = mysql.connector.connect(host="localhost", user="root", passwd="1234",  database='cs670research')
    db_cursor = db_conn.cursor(buffered=True)
    count_query = "select count(*) from research_exploration1 WHERE file_name='{}' and dataset='{}'  and label='{}' and severity='{}' and noise_type='{}'".format(file_name, dataset, label, severity, noise_type)
    db_cursor.execute(count_query)
    records = db_cursor.fetchall()[0][0]
    db_cursor.close()
    db_conn.close()
    return records

def countExistingRecords_label(file_name, dataset, label, severity, noise_type):
    db_conn = mysql.connector.connect(host="localhost", user="root", passwd="1234",  database='cs670research')
    db_cursor = db_conn.cursor(buffered=True)
    count_query = "select count(*) from research_exploration_label1 WHERE file_name='{}' and dataset='{}' \
    and label='{}' and severity='{}' and noise_type='{}'".format(file_name, dataset, label, severity, noise_type)
    db_cursor.execute(count_query)
    records = db_cursor.fetchall()[0][0]
    db_cursor.close()
    db_conn.close()
    return records

def recordsExists_label(file_name, dataset, label, severity, noise_type):
    present_count = countExistingRecords_label(file_name, dataset, label, severity, noise_type)
    return True if present_count > 0 else False

def recordsExists(file_name, dataset, label, severity, noise_type):
    present_count = countExistingRecords(file_name, dataset, label, severity, noise_type)
    return True if present_count > 0 else False
