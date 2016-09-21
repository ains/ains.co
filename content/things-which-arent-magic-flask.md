Title: Things which aren't magic - Flask and @app.route - Part 1
Date: 2014-12-28 17:00
Category: Programming
Tags: python, flask, decorators
Slug: things-which-arent-magic-flask-part-1
Author: Ainsley Escorce-Jones
Summary: First in the series "Things which aren't magic". Starting off by deconstructing the first example on the Flask website, to see how more complicated decorators can be used to create a nice API.

It's been a while since I've posted so figured it's about time I started a new series on my blog. 

Here's the first edition of a series I'm calling "Things which aren't magic", where I show how some of the nicer APIs provided by popular open source packages are constructed from the primitives of their respective languages.

In this post we're going to take a look at [Flask](flask.pocoo.org), and more specifically how Flask makes it possible to write "@app.route()" at the top of the function and expose its result to the internet.

Below is the first example given to us on the Flask Homepage, and the first example which we're going to deconstruct in order to better understand how "@app.route()" works.

    ::python
    app = Flask(__name__)
    
    @app.route("/")
    def hello():
        return "Hello World!"


### @app.route and other decorators

In order to begin understanding how "@app.route()" works we first need to look at decorators in Python (the things which start with "@", and go above function definitions).

What is a decorator exactly? Nothing special! A decorator is just a function which takes in a function (the one which you decorated with the "@" symbol) and returns a new function. 

When you decorate a function, you're telling Python to call the new function returned by your decorator, instead of just running the body of your function directly.

Still not 100% sure? Here's a simple example:

    ::python
    # This is our decorator
    def simple_decorator(f):
        # This is the new function we're going to return
        # This function will be used in place of our original definition
        def wrapper():
            print "Entering Function"
            f()
            print "Exited Function"
         
        return wrapper
    
    @simple_decorator 
    def hello():
        print "Hello World"
        
    hello()


Running the above will give produce the following output:

    
    Entering Function
    Hello World
    Exited Function


Great! 

Now we're part of the way to understanding how to build our own "@app.route()" decorator, but one difference you may have noticed is that our simple decorator doesn't take in any parameters, but "app.route()" does. 

So how can we pass arguments to our decorator? To do that we just create a "decorator factory" function, which we can call, returning the decorator to apply to our function. Let's see how that looks in practice.

    ::python
    def decorator_factory(enter_message, exit_message):
        # We're going to return this decorator
        def simple_decorator(f):
            def wrapper():
                print enter_message
                f()
                print exit_message
             
            return wrapper

        return simple_decorator
    
    @decorator_factory("Start", "End")
    def hello():
        print "Hello World"
        
    hello()


Will give us the output:

     Start
     Hello World
     End

Note that when we write _@decorator_factory("Start", "End")_ we're actually calling the function _decorator_factory_, which returns the actual decorator that is used, neat, huh?

### Putting the "app" in "app.route"

Now we know everything we're going to need to know about how decorators work in order to reimplement this part of the Flask API, so lets switch our attention to the importance of the "app" in our Flask Application.

In order to start understanding what's going on inside the Flask object, we'll create our own Python class, NotFlask.

    ::python
    class NotFlask():
        pass
        
    app = NotFlask()


Not a very interesting class, but one thing to note is that methods of a class can also be used as decorators, so lets make our class a little bit more interesting by adding a method called route which will be a simple decorator factory.

    ::python
    class NotFlask():
        def route(self, route_str):
            def decorator(f):
                return f

            return decorator
            
    app = NotFlask()
    
    @app.route("/")
    def hello():
        return "Hello World!"


The main difference between this decorator and the decorators that we have created before, is that we don't want to modify the behaviour of the function we're decorating, we just want a reference to it.

So, for our final trick, we're going to use the fact that we're allowed to use side effects inside our decorator function to store a link between the route given to us, and the decorated function that should be associated with it.

To do this we'll add a "routes" dictionary to our NotFlask object, and when our "decorator" function gets called we'll insert the route into our new dicitionary along with the function that it maps to.


    ::python
    class NotFlask():
        def __init__(self):
            self.routes = {}

        def route(self, route_str):
            def decorator(f):
                self.routes[route_str] = f
                return f

            return decorator
            
    app = NotFlask()
    
    @app.route("/")
    def hello():
        return "Hello World!"


Now we're almost there! But what use is that dictionary of routes if there's no way to access the view functions inside of it? Lets add a method _serve(path)_, which gives us the result of running a function for a given route if it exists or raises an exception if the route has not been registered yet.

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


In this series we're just focusing on replicating the nice APIs of popular libraries, so actually hooking the "serve" method up to a HTTP server is a bit out of the scope of this post, but rest assured, running the following snippet:

    ::python
    app = NotFlask()
    
    @app.route("/")
    def hello():
        return "Hello World!"
        
    print app.serve("/")


Will give us:

```
Hello World!
```

We've managed a very simple reimplementation of the first example on the Flask website, so lets write some quick tests to check that the behaviour of our small reimplementation of the Flask "@app.route()" is correct.

    ::python
    class TestNotFlask(unittest.TestCase):
        def setUp(self):
            self.app = NotFlask()

        def test_valid_route(self):
            @self.app.route('/')
            def index():
                return 'Hello World'

            self.assertEqual(self.app.serve('/'), 'Hello World')

        def test_invalid_route(self):
            with self.assertRaises(ValueError):
                self.app.serve('/invalid')



### Taking a quick breather.

__That's it!__ So, all it takes is a simple decorator, along with a a dictionary to replicate the basic behaviour of the "app.route()" decorator in Flask.

In the next post in this series, and the final post on Flask's app.route() we're going to look at how dynamic URL patterns work, by deconstructing the following example.


    ::python
    app = Flask(__name__)
    
    @app.route("/hello/<username>")
    def hello_user(username):
        return "Hello {} !".format(username)

Stay tuned!