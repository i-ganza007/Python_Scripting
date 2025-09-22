const express = require('express')
const http = require('http')
const dotenv = require('dotenv')
const router = require('./routes')
const app = express()
const mongoose = require('mongoose')

dotenv.config()

mongoose.connect(process.env.DB_URI,{useNewUrlParser:true})
const server = http.createServer(app)


app.use(express.json())
app.use('/api/user',router)

server.listen(3000,()=>{
    console.log('Logging to the server');
    
})