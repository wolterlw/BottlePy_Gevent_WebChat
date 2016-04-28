CREATE TABLE users (
id INTEGER PRIMARY KEY,
username TEXT,
password TEXT);

CREATE TABLE messages (
message_id INTEGER,
dialogue_id INTEGER,
from_id INTEGER,
message_body TEXT,
t_sent DATETIME);


CREATE TABLE dialogues ( --relation!
from_id INTEGER,
to_id INTEGER,
dialogue_id INTEGER, --shlould be a unique the same for the pair
num_messages INTEGER,
last_updated DATETIME); --days ago
--datetime in format yyyy-MM-dd HH:mm:ss
--after, when showing messages selecting them from 2 dialogues and sort by date

INSERT INTO users (id,username,password) VALUES(1,'wolterlw','ILovePy');
INSERT INTO users (id,username,password) VALUES(2,'eugene_r','ILoveJs');
INSERT INTO users (id,username,password) VALUES(3,'denbko_l','1234567');

INSERT INTO dialogues (from_id,to_id,dialogue_id,num_messages,last_updated) VALUES(1,2,0,0,'2016-04-25 18:45:00'); 
INSERT INTO dialogues (from_id,to_id,dialogue_id,num_messages,last_updated) VALUES(2,1,0,0,'2016-04-25 18:45:00'); 



/*
INSERT INTO dialogues (user1_id,user2_id) VALUES(0,1);
INSERT INTO dialogues (user1_id,user2_id) VALUES(0,2);

INSERT INTO messages (from_id,to_id,message_body) VALUES(0,1,'When is my frontend ready?');
INSERT INTO messages (from_id,to_id,message_body) VALUES(2,0,'Did U make Ur Math. Stat. already?');

SELECT * FROM users;
SELECT username, password FROM users WHERE id = 1;
SELECT message_body FROM messages WHERE from_id = 0;
SELECT message_body FROM messages WHERE from_id = 0
*/
