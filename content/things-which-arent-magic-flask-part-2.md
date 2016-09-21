Title: Things which aren't magic - Flask and @app.route - Part 2
Date: 2014-12-30 17:00
Category: Programming
Tags: python, flask, decorators
Slug: things-which-arent-magic-flask-part-2
Author: Ainsley Escorce-Jones
Summary: The second part and final of our look into the "@app.route" decorator provided by Flask, where we add support for dynamic urls. 

In my last post I finished off with a skeleton which mimicked the behaviour of "@app.route('/')" in the first example on the Flask website.

If you missed that edition of "Things which aren't magic", then check it out [here](things-which-arent-magic-flask-part-1.html).

In this post we're going to turn up the difficulty level a tiny bit and add the ability to have variable parameters in our URLs, by the end of this blog post we'll be able to support the expected behaviour for the following piece of code.

    ::python
    app = Flask(__name__)
    
    @app.route("/hello/<username>")
    def hello_user(username):
        return "Hello {}!".format(username)


So that the following path:

```
/hello/ains
```

Will match the route above, giving us the output of 

```
Hello ains!
```

### Expressing our routes, regularly.

Now that we're allowing our URLs to be dynamic, we can no longer directly compare the path that we're serving to the route previously registered using "@app.route()". 

What are we going to do instead? We're going to need to use regular expressions, so we can match paths against a pattern, instead comparing them to a fixed string.

I won't be going into detail about specifics of regular expressions in this blog post, but if you need a refresher check out [this website](http://www.regular-expressions.info/quickstart.html).

So, our first step is going to be to transform our route into a regular expression pattern that we can match the path incoming against. We'll also be using this regular expression to extract the variables that we're interested in.

So what would a regular expression that matches the route "/hello/&lt;username&gt;" look like? 

Well a simple regular expression such as __"^/hello/(.+)$"__, would be a good start, so lets see how that would work with some code:

    ::python
    import re

    route_regex = re.compile(r"^/hello/(.+)$")
    match = route_regex.match("/hello/ains")

    print match.groups()
    
    

Will output:

    ('ains',)


Sweet, however, ideally we want to preserve the link between the first group that we've matched, and the identifier "username" from our route _"/hello/&lt;username&gt;"_.

#### Named Gapturing Groups
Fortunately, regular expresions also support named capturing groups, this allows us to assign a name to a matching group, which we can recover later when reading through our matches.

We can use the following syntax to give our capturing group from the first example the identifier of _username_.

     /hello/(<?P<username>.+)"
     
Then we can use the _groupdict()_ method on our regular expression match to get all of the capturing groups as a dictionary, with the name of the group mapped to the matched value.

So now we get the following code:

    ::python
    route_regex = re.compile(r'^/hello/(?P<username>.+)$')
    match = route_regex.match("/hello/ains")

    print match.groupdict()
    
Giving us the following dictionary as output:

    {'username': 'ains'}
   
So now, armed with the format of the regular expressions we'll need, and the knowledge how we can use them to match incoming URLs, all that's left is to make a method that will convert our declared routes into their equivalent regular expression pattern.

To do this we're going to use another regular expression (it's regular expressions all the way down), to convert the variables in our routes into regular expression patterns, so for example we'll need to convert "&lt;username&gt;" to "(?P&lt;username&gt;.+)".

Sounds simple enough! We're able to do it with just a few lines of code.


    ::python
    def build_route_pattern(route):
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
        return re.compile("^{}$".format(route_regex))
        
    print build_route_pattern('/hello/<username>')
    
Here we're doing a regular expression substitution of all occurences of the pattern _<\w+>_ (a string enclosed in angled brackets), with it's regular expression named group equivalent. 

In the first argument of re.sub we place our pattern _<\w+>_ inside brackets in order to assign it to the first matching group. In our second argument we can use the contents of the first matching group by writing __\1__ (__\2__ would be the contents of the second matching group, etc, etc...)

So finally, inputting the pattern 

    /hello/<username>

Will give us the regular expression:

    ^/hello/(?P<username>.+)$
    

### Out with the old, in with the new.

Let's take a quick look at the simple NotFlask class that we built last time.

    ::python
    class NotFlask():
        def __init__(self):
            self.routes = {}
    
        def route(self, route_str):
            def decorator(f):
                self.routes[route_str] = f
                return f
    
            return decorator
    
        def serve(self, path):
            view_function = self.routes.get(path)
            if view_function:
                return view_function()
            else:
                raise ValueError('Route "{}"" has not been registered'.format(path))

            
    app = NotFlask()
    
    @app.route("/")
    def hello():
        return "Hello World!"



Now that we have a new and improved method of matching incoming routes, we're going to have to get rid of the naive dictionary implentation we had before.

Let's start by retrofitting our function for adding routes, so that instead of storing our routes in a dictionary we'll have a list of _(pattern, view_function)_ pairs.

This means that when a programmer decorates a function with @app.route() we'll attempt to compile their route into a regular expression and then store it along with the decorated function in our new routes list.

Let's have a look at the code that does that:

    ::python
    class NotFlask():
        def __init__(self):
            self.routes = []
        
        # Here's our build_route_pattern we made earlier
        @staticmethod
        def build_route_pattern(route):
            route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
            return re.compile("^{}$".format(route_regex))

        def route(self, route_str):
            def decorator(f):
                # Instead of inserting into a dictionary,
                # We'll append the tuple to our route list
                route_pattern = self.build_route_pattern(route_str)
                self.routes.append((route_pattern, f))

                return f

            return decorator
            
We're also going to need a _get_route_match_ method, which given a path, will try and find a matching view function, or return _None_ if one can't be found. 

However, one more thing which we're going to need return if a match is found, in addition to the view function, will be the dictionary of capturing groups which we matched earlier, we'll need this in order to pass the correct arguments over to the view function.


So here's what our _get_route_match_ function is going to look like:

	::python	
	def get_route_match(path):
	    for route_pattern, view_function in self.routes:
	        m = route_pattern.match(path)
	        if m:
	           return m.groupdict(), view_function
	           
	    return None
	  
	  
Now we're almost there, the last piece of this puzzle will be figuring out how to call the view function with the correct arguments from that dictionary of regular expression matching groups.


### A thousand ways to call a function.

Let's take a step back and look at the different ways we can call a function in python.

Like this one for example:

    ::python
    def hello_user(username):
        return "Hello {}!".format(username)


The simplest way (which you'll hopefully be familiar with) is using regular arguments, here the order of the arguments matches the order of those in our function definition.

    >>> hello_user("ains")
    Hello ains!
    
Another way to call a function is with keyword arguments. Keyword arguments can be specified in any order, and work great for functions with many optional arguments.

    >>> hello_user(username="ains")
    Hello ains!
    
One last way to call a function in Python is with a dictionary of keyword arguments, where the keys in the dictionary correspond to the name of the argument. We tell Python to unpack a dictionary and use it as the keyword arguments of a function by using two stars, "**". This snippet below is exactly the same as the snippet above, now we're using a dictionary of arguments which we can create dynamically at runtime.

    >>> kwargs = {"username": "ains"}
    >>> hello_user(**kwargs)
    Hello ains!
    
So, remember the groupdict() method from before? The same one which returned _{"username": "ains"}_ after regular expression was matched? Well now that we know about kwargs, we easily can pass the dictionary of matches as arguments to our view function, completing NotFlask!

So lets put all of this together into one final class.
    
    ::python
    class NotFlask():
        def __init__(self):
            self.routes = []

        @staticmethod
        def build_route_pattern(route):
            route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
            return re.compile("^{}$".format(route_regex))

        def route(self, route_str):
            def decorator(f):
                route_pattern = self.build_route_pattern(route_str)
                self.routes.append((route_pattern, f))

                return f

            return decorator

        def get_route_match(self, path):
            for route_pattern, view_function in self.routes:
                m = route_pattern.match(path)
                if m:
                    return m.groupdict(), view_function

            return None

        def serve(self, path):
            route_match = self.get_route_match(path)
            if route_match:
                kwargs, view_function = route_match
                return view_function(**kwargs)
            else:
                raise ValueError('Route "{}"" has not been registered'.format(path))
                
                
Now, just like magic, the following snippet: 

    ::python
    app = NotFlask()
    
    @app.route("/hello/<username>")
    def hello_user(username):
        return "Hello {}!".format(username)
        
    print app.serve("/hello/ains")


Gives us the output of :

```
Hello ains!
```


### Wrapping Up

So that's it for the our look into Flask's app.route() for "Things which aren't magic". It turns out all we had to do was use a dash of regular expressions and Python's method of calling functions with keyword arguments in order to add a bit of dynamicism to our URLs.

The source for the NotFlask example, along with it's tiny test suite is [available over on Github](https://github.com/ains/twam-flask) so over go any check it out.

Up next is this series I'll be digging into AngularJS, seeing how it does dependency injection, and how declarations like the snippet below are made possible!

    ::javascript
    angular.module('test', ['$http', function($http) {
        $http.get("http://google.com/").success(function(data) {
            console.log(data);
        });
    }]);