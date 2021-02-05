# Running the repo

## To begin from scratch:
1. Install mongodb
2. Start mongodb service
3. Run `populate_mongodb.py` script to populate the database with arXiv entries from the Kafka service.

### 1. Install mongodb

`brew tap mongodb/brew`

`brew install mongodb-community`

### 2. Start mongodb

`brew services start mongodb-community`

### 3. Populate local database

`git clone git@gitlab.jhuapl.edu:<your_username>/ig.git`

`cd ig`

`git checkout develop`

`pip install -r requirements.txt`

Change `USER529` to your own: 
`USER529 = "asherlk1"`

`python -m populate_mongodb <number of Kafkfa messages>`

Note: if you want to rebuild the database from scratch, add `-restart` flag to populate script: `python -m populate_mongodb <num messages> -restart`



## Make queries

### Topic flag

To see timeseries of all topics:

`python -m arxiv_etl -topic ''`

To see timeseries of a publications in a specific topic containing <string>:

`python -m arxiv_etl -topic <string>`

### Author flag

To see timeseries of a publications by a certain author:

`python -m arxiv_etl -author <author>`


# Random | Moodboard
https://www.figma.com/file/k1MfGcQNCoDkuEzmJeOAvV/IG-Mood-Board?node-id=0%3A1
