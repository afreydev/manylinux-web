import pymysql
import json

def get_connection(app):
    return pymysql.connect(
        app.config["MYSQL_HOST"],
        app.config["MYSQL_USER"],
        app.config["MYSQL_PASSWORD"],
        app.config["MYSQL_DATABASE"]
    )


def create_table(app):
    conn = get_connection(app)
    cursor = conn.cursor()
    try:
        sql = """
        CREATE TABLE IF NOT EXISTS tasks (
        id BIGINT NOT NULL AUTO_INCREMENT,
        settings TINYTEXT NOT NULL,
        task_id VARCHAR(255) NOT NULL,
        created_at DATETIME NOT NULL,
        PRIMARY KEY (id))
        ENGINE = InnoDB
        """
        cursor.execute(sql)
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def create_task(app, settings, task_id):
    conn = get_connection(app)
    cursor = conn.cursor()
    try:
        sql = '''
        INSERT INTO tasks(settings, task_id, created_at) VALUES ("{}", "{}", NOW())
        '''.format(settings, task_id)
        cursor.execute(sql)
        conn.commit()
    finally:
        conn.close()

def get_tasks(app, limit=10):
    conn = get_connection(app)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        sql = """
        SELECT *
        FROM tasks
        ORDER BY created_at DESC
        LIMIT {}
        """.format(limit)
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conn.close()
