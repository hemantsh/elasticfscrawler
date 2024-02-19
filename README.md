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

Case Search
- Logout link - Only displayed if user is logged in
- Login link - Only if user is not logged in
- Create User link - Only to Admin
- Report link - Only to Admin
- /search and /results routes are only available to logged in user.
- /report route will be available to admin user type

Error page
- Create a generic error page to show simple error and a link to go to home page
  
