# Introduction 

[![Build Status](https://travis-ci.com/ahmedemad3965/Url-Shortener.svg?branch=master)](https://travis-ci.com/ahmedemad3965/Url-Shortener)  

This is a Url Shortener **RESTful** API built **Django**.  
You can freely use, edit and learn from this project. 
This Project is very easy and simple.
The **docker** and **docker-compose** images configuration files are stored with in the project so that you can use it and test it from anywhere with no problems.
The **API** is fully tested with **100% Code coverage** with automated **tests** in a separate folder.  

# Documentation 

There are only two **end-points** in this API, one for creating new url shorts and another to redirect user from requested short url to the original one.   

Creating a new Short Url:
      
    POST 127.0.0.1/shorten  

post request body:     
 
**original_url**: the url of the website that will be redirected to, this field is required and must be in valid url format.    

**short_url**: the short slug after the url that the user will be redirected from, this field is optional, if not send it will be generated automatically.

to Redirect from shortened url to original url we use:       
   
    GET 127.0.0.1/{short_url}