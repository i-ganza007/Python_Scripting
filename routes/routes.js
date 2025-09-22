const router = require('express').Router()
const usermodel = require('../models/User')
const Joi = require('@hapi/joi')


router.post('/register', async (req,res)=>{
    const newUser = new usermodel({
        name:req.body.name,
        email:req.body.email,
        password:req.body.password,
    })
    // console.log(req.body)

    try {
      const firstuser = await newUser.save()  
      res.send(firstuser)
    } catch (error) {
        res.send('Getting this error',error)
    }
})


module.exports = router