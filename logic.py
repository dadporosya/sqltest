import sqlite3
from config import DATABASE

skills = [(_,) for _ in (['Python', 'SQL', 'API', 'Telegram', "JS", "HTML", "CSS", "C++", "C#", "C"])]
statuses = [(_,) for _ in (
['На этапе проектирования', 'В процессе разработки', 'Разработан. Готов к использованию.', 'Обновлен',
 'Завершен. Не поддерживается'])]


class DB_Manager:
    def __init__(self, database):
        self.database = database
        self.con = sqlite3.connect(self.database, check_same_thread=False)
        self.cur = self.con.cursor()
        # self.con.execute("PRAGMA foreign_keys = ON;")
        self.create_tables()
        self.default_insert()

    def create_tables(self):
        with self.con:
            self.con.execute('''CREATE TABLE IF NOT EXISTS projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''')
            self.con.execute('''CREATE TABLE IF NOT EXISTS skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT
                        )''')
            self.con.execute('''CREATE TABLE IF NOT EXISTS project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES projects(project_id),
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                        )''')
            self.con.execute('''CREATE TABLE IF NOT EXISTS status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                        )''')
            self.con.commit()

    def __executemany(self, sql, data):
        with self.con:
            self.con.executemany(sql, data)
            self.con.commit()

    def __select_data(self, sql, data=tuple()):
        with self.con:
            self.cur.execute(sql, data)
            return self.cur.fetchall()

    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO skills (skill_name) VALUES(?)'
        data = skills
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO status (status_name) VALUES(?)'
        data = statuses
        self.__executemany(sql, data)

    def insert_project(self, data):
        sql = """INSERT INTO projects
        (user_id, project_name, url, status_id)
        values(?, ?, ?, ?)"""
        self.__executemany(sql, data)

    def insert_skill(self, user_id, project_name, skill):
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        project_id = self.__select_data(sql, (project_name, user_id))[0][0]
        skill_id = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))[0][0]
        data = [(project_id, skill_id)]
        sql = 'INSERT OR IGNORE INTO project_skills VALUES(?, ?)'
        self.__executemany(sql, data)

    # def insert_status(self, user_id, project_name, skill):
    #     sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
    #     project_id = self.__select_data(sql, (project_name, user_id))[0][0]
    #     skill_id = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))[0][0]
    #     data = [(project_id, skill_id)]
    #     sql = 'INSERT OR IGNORE INTO project_skills VALUES(?, ?)'
    #     self.__executemany(sql, data)

    def get_statuses(self):
        sql = "SELECT status_name from status"
        return self.__select_data(sql)

    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res:
            return res[0][0]
        else:
            return None

    def get_projects(self, user_id):
        sql = """SELECT * FROM projects 
        WHERE user_id = ?"""
        return self.__select_data(sql, data=(user_id,))

    def get_project_id(self, project_name, user_id):
        return self.__select_data(sql='SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?  ',
                                  data=(project_name, user_id,))[0][0]

    def get_skills(self):
        return self.__select_data(sql='SELECT * FROM skills')

    def get_project_skills(self, project_name):
        res = self.__select_data(sql='''SELECT skill_name FROM projects 
JOIN project_skills ON projects.project_id = project_skills.project_id 
JOIN skills ON skills.skill_id = project_skills.skill_id 
WHERE project_name = ?''', data=(project_name,))
        return ', '.join([x[0] for x in res])

    def get_project_info(self, user_id, project_name):
        sql = """
SELECT project_name, description, url, status_name FROM projects 
JOIN status ON
status.status_id = projects.status_id
WHERE project_name=? AND user_id=?
"""
        return self.__select_data(sql=sql, data=(project_name, user_id))

    def update_projects(self, param, data):
        sql = f"""UPDATE projects SET {param} = ? 
        WHERE project_name = ? AND user_id = ?"""
        self.__executemany(sql, [data])

    def delete_project(self, user_id, project_id):
        sql = """DELETE FROM projects 
        WHERE user_id = ? AND project_id = ? """
        self.__executemany(sql, [(user_id, project_id)])

    def delete_skill(self, project_id, skill_id):
        sql = """DELETE FROM skills 
        WHERE skill_id = ? AND project_id = ? """
        self.__executemany(sql, [(skill_id, project_id)])

    def alertTable(self, table_name, new_column_name, new_column_type):
        self.cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column_name} {new_column_type}")
        self.con.commit()


# if __name__ == '__main__':
#     manager = DB_Manager(DATABASE)


    # manager.con.commit()


