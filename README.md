# do_when
A background process to open URLs or apps (or whatever MAC OS Terminal "open" command can open) at different intervals. MAC Only for now.

1. Clone this repo
2. Create a sqllite3 DB called stuff_to_do in the same dir as the repo
3. Add tuples to stuff_to_do with this format: 

INSERT INTO stuff_to_do VALUES(1,'open http://cnn.com','2022-11-20 14:00:00.010000','hourly','2022-11-20 13:34:45.429673');

First field is index (unique), second is 'open' command to execute, third is next time to execute command, fourth is how often to do it. Could be yearly, monthly, weekly, daily, hourly. Last field is the last time the command was executed.

4. Start it

python3 ./do_when -s
