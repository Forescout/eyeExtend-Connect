## node.js simulation Server for SE Training

Server to simulate 3rd party cloud service with JWT authentication. Tested with node.js v10.14.1.

Install with `#npm install`

Run with 	`#node server.js`

Server will run on port 3000 on the local machine.

`/` is unprotected, so http://localhost:3000 will return success.

`/api` are protected routes and require authentication.

Credentials are hard coded, username: `forescout`, password: `4Scout123`


