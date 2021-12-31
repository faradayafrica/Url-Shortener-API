# Introduction 

This is a Url Shortener **RESTful** API built **Django** for use within the Faraday Organization

# Documentation 

There are only two **end-points** in this API, one for creating new url shorts and another to redirect user from requested short url to the original one.   

Creating a new Short Url:
      
    POST /shorten  

post request body:     
 
**original_url**: the url of the website that will be redirected to, this field is required and must be in valid url format.    

**short_url**: the short slug after the url that the user will be redirected from, this field is optional, if not send it will be generated automatically.

to Redirect from shortened url to original url we use:       
   
    GET 127.0.0.1/{short_url}