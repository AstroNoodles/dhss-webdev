__author__ = 'Michael'

'''
This script sets up the database and insertion of initial flights and users into said database as written in SQL files
'''
import psycopg2

INSERT_QUERIES = [
    "INSERT INTO Participant(pid,participant_name,skill_level,registration_year) VALUES " + \
    "(13,'Mia Hoffmann','Advanced',2024), " + \
    "(14,'Noah Osei','Expert',2024), " + \
    "(15,'Priya Sharma','Intermediate',2024), " + \
    "(16,'Quinn Dupont','Beginner',2024)",
    
    "INSERT INTO Team(team_id,team_name) VALUES (11,'Lambda Legends'), (12,'Kernel Krakens');",
    
    "INSERT INTO Submission(team_id,challenge_id,round_id,submission_date,model_type) VALUES" + \
    "(11,1,1,'2024-01-19','DenseNet')" + \
    "(11,1,2,'2024-02-03','DenseNet')" + \
    "(11,1,3,'2024-02-18','DenseNet')" + \
    "(11,3,3,'2024-04-05','CatBoost')" + \
    "(12,2,1,'2024-02-08','DistilBERT')" + \
    "(12,2,2,'2024-02-23','DistilBERT');",

    "INSERT INTO TeamMember (pid,team_id,role,challenge_id) VALUES" + \
    "(13,11,'Lead',1)" + \
    "(14,11,'Contributor',1)" + \
    "(15,12,'Lead',2)" + \
    "(16,12,'Contributor',2)" + \
    "(13,11,'Lead',3)" + \
    "(14,11,'Contributor',3);",

    "INSERT INTO Evaluates (jid,challenge_id,round_id,team_id,score) VALUES" + \
    "(1,1,1,11,89)" + \
    "(2,1,1,11,87)" + \
    "(3,1,1,11,88)" + \
    "(2,1,2,11,92)" + \
    "(3,1,2,11,90)" + \
    "(4,1,2,11,91)" + \
    "(1,1,3,11,95)" + \
    "(3,1,3,11,97)" + \
    "(4,1,3,11,94)" + \
    "(1,2,1,12,85)" + \
    "(2,2,1,12,83)" + \
    "(4,2,1,12,84)" + \
    "(1,2,2,12,88)" + \
    "(2,2,2,12,86)" + \
    "(4,2,2,12,87)" + \
    "(1,3,3,11,97)" + \
    "(3,3,3,11,93)" + \
    "(4,3,3,11,95);"
]

if __name__ == '__main__':
    connection = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password='local456',
        host='localhost'
    )

    cursor = connection.cursor()

    with open('flights.sql') as inserts:
        try:
            database_init = inserts.read()
            cursor.execute(database_init)
        except Exception as error:
            print(error)
        finally:
            cursor.close()

    connection.close()
    print('database init successfully!') 