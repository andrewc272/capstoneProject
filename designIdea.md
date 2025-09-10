# Application architecture

## Front-end

index--v-----------v
       |set profile|enter game


## Back-end

Database of users/profiles
Chatlog
chatlog archive

### SQLite

#### Users

- User ID
- Username
- User key(maybe the same as user ID)
- Bot or human

#### Chat archive

- Chat ID
- Chat time
- Chat participants

#### Chat messages

- chat ID
- time sent
- sender

### Flask

- POST: create user
- GET: user info
- GET: host info
- GET: chatlog
- GET: current game chat
- GET: 
