#Notely server
This is the companion server to [notely](http://github.com/samphippen/notely)

##Installation
I deploy this to heroku. It needs some database tables to work. To do it
execute the following sql statements:
`CREATE TABLE useractions (uuid VARCHAR(120), actions TEXT)`
`CREATE TABLE pairing (code VARCHAR(120), uuid VARCHAR(120))`

##Usage
Use notely
