# elasticfscrawler

User
- id
- email address
- displayname
- password
- is_admin 
- countries

UserSearch
- user_id (ref to User.id)
- Search_query
- time

Rules
- Only Admin can create a user
- Email can be sent to user when user is created (?)
- Only admin can do a search report for a given time frame

Report Screen
- Start_time
- End_time
- Search button
- Results in datatable with export buttons like case search screen
- query (select * from usersearch where time > start_time and time < end_time)
