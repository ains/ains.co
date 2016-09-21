Title: Things which aren't magic - JSONP
Date: 2015-04-18 17:00
Category: Programming
Tags: javascript, jsonp, hack
Slug: things-which-arent-magic-jsonp
Author: Ainsley Escorce-Jones
Summary: A quick look behind the scenes of one of my favourite dirty hacks, JSONP.

In this post we're going to continue our "Things which aren't magic tour" of JavaScript, by taking a quick look at JSONP, a neat trick which lets us share information across web services where we'd otherwise be unable to due to the [Same-Origin Policy](http://en.wikipedia.org/wiki/Same-origin_policy) (in a world before CORS).

To look into JSONP we're going to implement a simple API that will let us fetch data from a remote resource (we're going to use the Flickr API), and then pass it to a callback for processing. So that by the end of this post the following snippet should give us a list of the Photo URLs from Flickr's Public Photo feed.

    ::javascript
    var API_URL = "https://api.flickr.com/services/feeds/photos_public.gne?format=json&jsoncallback=?";
    JSONP.fetch(API_URL, function (res) {
        console.log(res.title);
        res.items.forEach(function (item) {
            console.log(item.link);
        });
    }); 
  
### Why do we need JSONP?

So before we dig into building our API lets first start by looking at why we need JSONP, and why a regular AJAX request doesn't cut it sometimes.

Normal AJAX requests, like the following snippet of jQuery code would work perfectly fine for grabbing a JSON file or calling an API endpoint, because the URL is relative, it'll be fetched from the same domain as the page in which the script is running.

    ::javascript    
    $.getJSON( "example.json", function() {
        console.log( "success" );
    });

But if we were to change *"example.json"* to *"http://www.google.com/example.json"*, the above code would fail to make the request. Why? Well that's because AJAX requests, like many typical JavaScript operations that can interact across domains are restricted by the Same Origin Policy, meaning we'll only be permitted to perform certain actions on targets which have the same protocol, port, and domain as the initiating script.

However, like in the case of consuming Flickr's API, a developer might want to legimately make a request to an endpoint from a different origin, and there are a few ways to get around this. Modern browsers support Cross-Origin Resource Sharing (CORS), which allow a server to send custom HTTP headers telling the browser that it's okay to relax some of the Same-Origin Policy restrictions when interacting with it, but for older browsers we're left with two options, creating a server from the same origin as our script that proxies requests to the API we want to communicate with, or alternatively, we can use JSONP.

### So how does JSONP work?

To understand JSONP, all you have to do is remember that we're allowed to import scripts from any origin into our page using "<script\>" tags, which is obvious, considering that we're allowed (and encouraged) to grab common JavaScript libraries from CDN's. Additionally, we can also use JavaScript code to insert new script tags into our document, which our browser will execute immediately in the same global scope as the rest of our code.  

So, combining these facts, and the fact that JSON is a subset[*](http://timelessrepo.com/json-isnt-a-javascript-subset) of JavaScript, we can try and use dynamically created script tags to bring data from external resources into our web application, without being bound by the Same-Origin Policy.


### Building our Simple API

Let's start with a skeleton of our JSONP API:

	::javascript
	var JSONP = function () {
        return {
            fetch: function (url, cb) {
               
            }
        };
    }();
 
Using our intuition from above lets start by creating a new script tag in our page, pointed at the URL the user want's to make a JSONP request to.

    ::javascript
    fetch: function (url, cb) {
        // Inject new script tag
        var scriptElem = document.createElement("script");
        scriptElem.setAttribute('src', url);
        document.body.appendChild(scriptElem);
    }
    
Great! Now when we load our page, we'll see an extra request being sent to the Flickr API, but not much else will happen apart from that. 

Let's take a closer look at the URL we're trying to make a request to, notice the extra GET parameter **"&jsoncallback=?"**? That's where the next part of the magic comes from with JSONP, if we change this parameter to read **"&jsoncallback=test"**, our response from the Flickr API will change;

    ::javascript
    test({    
		"title": "Uploads from everyone",
    ....
    
There it is, the JSON payload we were expecting is being passed to a function of our choosing, and so if we refresh our test page now we'll recieve the following error after our JSONP fetch call has been executed.

    Uncaught ReferenceError: test is not defined
    
So, after we inject the new script tag into our page, the code inside it gets executed but at the moment there's no function in our global scope called "test", in order to get that result back from the Flickr API and into our callback function, we're going to need to define a function in our global scope (window), that will be called with the JSON payload once the script tag that we've created has been loaded. We'll randomly generate the name of this function, just incase we have more than one of these JSONP requests in flight at any given moment in time, and also make sure we clean up after ourselves once the request has been handled.

    ::javascript
    // Generate a random function name
    var cbName = "cb" + Math.floor(Math.random() * 1000);

    // Define global callback function
    window[cbName] = function(payload) {
        // Call the users callback w/ payload
        cb(payload);

        // Clean up this function when we're done;
        delete window[cbName];
    };
    
    
Finally we need to replace the string "callback=?" with the actual name of our callback function, so that the Flickr API knows which function to call in it's response.

    ::javascript
    var scriptUrl = url.replace("callback=?", "callback=" + cbName);
    
    
### Putting it all together

So, finally, if we put that all together the code for our JSONP API will look like the following:

    ::javascript
    var JSONP = function () {
        return {
            fetch: function (url, cb) {
                // Generate a random function name
                var cbName = "cb" + Math.floor(Math.random() * 1000);

                // Define global callback function
                window[cbName] = function(payload) {
                    // Call the users callback w/ payload
                    cb(payload);

                    // Clean up this function when we're done;
                    delete window[cbName];
                };

                // Replace "callback=?" with actual callback function name
                var scriptUrl = url.replace("callback=?", "callback=" + cbName);

                // Inject script tag
                var scriptElem = document.createElement("script");
                scriptElem.setAttribute('src', scriptUrl);
                document.body.appendChild(scriptElem);
            }
        };
    }();
    
 and sure enough, if we run the following code in an HTML document.

    ::javascript
    var API_URL = "https://api.flickr.com/services/feeds/photos_public.gne?format=json&jsoncallback=?";
    JSONP.fetch(API_URL, function (res) {
        console.log(res.title);
        res.items.forEach(function (item) {
            console.log(item.link);
        });
    }); 
    
We'll get the following output:
    
    Uploads from everyone
	https://www.flickr.com/photos/palmer-gould/16366905884/
	https://www.flickr.com/photos/nagradim/16366905974/
	...
	
### Wrapping up

That's all there is to it! JSONP is just a simple convention that involves a server agreeing to wrap it's JSON payload inside a JavaScript function call, which the client will have defined, ready to be called when it executes the payload for the server.

JSONP was a neat hack that used existing features of browsers to support the integration of external API's whilst avoiding the sometimes awkward Same-Origin Policy. However, JSONP is not without it's flaws, and as we saw above involves actually executing arbitrary JavaScript from a remote server (not just parsing a response), this means a client has to absolutely trust a server not to send it a malicious response.

Fortunately, JSONP has been superseded by CORS in all modern browsers, but it's still a cool look into how something so helpful and ubiquitous is also really easy to understand underneath the hood.

The code from this blog post is available over in this [Gist](https://gist.github.com/ains/e127290195a5e4e304d3), or see a very barebones demo over at [http://ains.co/jsonp/](http://ains.co/jsonp/)