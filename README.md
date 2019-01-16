# message_patterns

analyzing conversations with graphs.
 
iPhone iMessages are stored as an SQLite Database. This database contains many tables, but the ones we are concerned with are `handle` table, 
and the `message` table. 

Steps:
1) Find database and explore the handle table. Get the handle_id's that corresponds to the phone number you want to explore. Usually there are two handle_id's for
one phone number: one for SMS, and one for iMessage
2) Edit the generate_messaeg_db.py by changing the PATH_TO_DF variable to the location of the iMessage database and run the following code to produce `message_db.csv` file:
```
python3 generate_message_db.py <handle_id1> <handle_id2>
```
3) Next, run the generate_graphs.py. It takes a required argument that takes in a matplotlib style which produces 9 graphs in the directory in which it is executed. An example would be 'seaborn-pastel'
```
python3 generate_graphs.py messages.csv seaborn-pastel
```
This is the a very rough code and it is mainly me trying to learn matplotlib styles and answer some questions about trends.
