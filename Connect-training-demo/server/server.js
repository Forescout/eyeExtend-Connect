// node server for SE Training - spollock@forescout
const express = require('express')
const bodyParser = require('body-parser')
const morgan = require('morgan')
const jwt = require('jsonwebtoken')
const config = require('./configuration/config')
const ProtectedRoutes = express.Router()
const app = express()

// set secret
app.set('Secret', config.secret)

// use morgan to log requests to the console
app.use(morgan('dev'))

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: true }))

// parse application/json
app.use(bodyParser.json())

app.listen(3000, () => {
  console.log('Simulation Server is running on port 3000')
})

app.get('/', function (req, res) {
  res.send('SE Test Server is running -- well done!')
})

app.post('/api/authenticate', (req, res) => {
  if (req.body.username === 'forescout') {
    if (req.body.password === '4Scout123') {
      // correct username/password let's create our token
      const payload = {
        check: true
      }
      var token = jwt.sign(payload, app.get('Secret'), {
        expiresIn: '1y' // uses zeit/ms  https://github.com/zeit/ms
      })
      res.json({
        message: 'Authentication Completed',
        token: token
      })
    } else {
      res.json({ message: 'Please check your password!' })
    }
  } else {
    res.json({ message: 'User not found !' })
  }
})

app.use('/api', ProtectedRoutes)
ProtectedRoutes.use((req, res, next) => {
  // console.log(req.headers)  // debug all headers being sent
  let token = req.headers.authorization // Express headers are auto converted to lowercase
  if (token.startsWith('Bearer ')) {
    // Remove Bearer from string
    token = token.slice(7, token.length)
  }

  // decode token
  if (token) {
    // verifies secret and checks if the token is expired
    jwt.verify(token, app.get('Secret'), (err, decoded) => {
      if (err) {
        return res.json({ message: 'Invalid token' })
      } else {
        // if everything is good, save to request for use in other routes
        req.decoded = decoded
        next()
      }
    })
  } else {
  // if there is no token
    res.send({
      message: 'No token provided.'
    })
  }
})

ProtectedRoutes.get('/getdevice/:mac', (req, res) => {
  // console.log(req.params)
  const departments = ['Marketing', 'Operations', 'Sales', 'Engineering', 'Guest']
  const department = departments[Math.floor(Math.random() * departments.length)]

  const descriptions = ['CEO Laptop', 'Stolen Laptop, call IT!', '', 'Somewhere over the rainbow', 'Guest access only']
  const description = descriptions[Math.floor(Math.random() * descriptions.length)]

  const locations = ['United Airlines', 'Cafeteria', 'Elevator', 'Stairwell', 'California']
  const location = locations[Math.floor(Math.random() * locations.length)]

  const model_numbers = ['BR549', 'UNIVAC9000', 'VT100', 'IBM360', 'TRS80']
  const model_number = model_numbers[Math.floor(Math.random() * model_numbers.length)]

  const owners = ['Steven Pollock', 'Stephen Tyler', 'Stephen Deering', 'Jason LeMair', 'Vinnie Saporito']
  const owner = owners[Math.floor(Math.random() * owners.length)]

  const returns = [
    {
      department: department,
      description: description,
      location: location,
      model_number: model_number,
      owner: owner
    }
  ]
  res.json(returns)
})

ProtectedRoutes.get('/getmalware/:mac', (req, res) => {
  const returns = [
    {
      sha256: '43ce41be6eeaf3aa61a0ff9a28c045c75e6a104449a145a154eaaa6f36fda44f',
      filetype: 'Win32 DLL',
      filesize: '5.02 MB (5267459 bytes)',
      target_machine: 'Intel 386 or later processors and compatible processors',
      malware_name: 'Wannacry'
    },
    {
      sha256: '8a87a1261603af4d976faa57e49ebdd8fd8317e9dd13bd36ff2599d1031f53ce',
      filetype: 'Win32 EXE',
      filesize: '1.84 MB (1930240 bytes)',
      target_machine: 'Intel 386 or later processors and compatible processors',
      malware_name: 'Bluekeep'
    }
  ]
  // to implement mac checking, otherwise just return the same thing for any device
  // if (req.params.mac === 'c4b301cf8273') {
  //   res.json(returns)
  // }
  // else {
  //   res.json('')
  // }
  res.json(returns)
})

ProtectedRoutes.post('/senddata/', (req, res) => {
  console.log('Data from /sendata API Call ==>')
  console.log(req.body)
  res.json('Data Received!!')
})
