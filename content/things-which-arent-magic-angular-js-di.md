Title: Things which aren't magic - AngularJS Dependency Injection
Date: 2015-03-28 17:00
Category: Programming
Tags: javascript, AngularJS, dependency injection
Slug: things-which-arent-magic-angular-js-di
Author: Ainsley Escorce-Jones
Summary: Continuing our exploration of things which aren't magic by dissecting AngularJS style dependency injection.

So in the last edition of "Things which aren't magic" we took a look into Flask's @app.route()  decorator, to see how decorators, side effects and a dash of regular expressions give us the magic @app.route() that exposes our Python functions to the World Wide Web.

In this edition we're going to stick with the web-based theme, but switch languages and take a dive in to JavaScript, and more specifically how the syntax of dependency injection in AngularJS works.

Let's start by taking a look an example of an AngularJS module with some dependencies that we are going to build support for.

    ::javascript
    var module = angular.module('testModule', []);

    module.service('$http', [function () {
        return {
            get: function (url) {
                return "Got data from: " + url;
            }
        }
    }]);

    module.service('dummyService', ['$http', function ($http) {
        return {
            fetchJson: function () {
                return $http.get("example.json");
            }
        }
    }]);

    module.run(['dummyService', function (dummyService) {
        console.log(dummyService.fetchJson());
    }]);
    
    
Here we first define a dummy $http module, and then we define a dummy service, which requires our $http module and uses it to make a "request".

Finally, we'll run our test module, which should give us the console output 

	Got data from: example.json


### AngularJS Dependency Injection - a quick overview.

So, as we saw above, AngularJS lets us declare the dependencies that the components of our application will require and then AngularJS handles the instantiation, management and injection of our dependencies at runtime.

In this post we're going to look at how we can identify and inject services into components of a simple application, in a similar manner to AngularJS, by replicating the "Inline Array Annotation" (seen above) and "Implicit Annotation" APIs for dependency injection.

In this post to keep things simple, we're going to be focusing on making a very stripped down (but API compatible subset of AngularJS), with the ability to create and inject services, but the general ideas we'll cover can be expanded to how AngularJS handles other application components.

A few things to keep in mind about AngularJS services is that

- They are are singletons, this means that only one instance of a service is ever created, this single instance is shared with all other application components that depend on this service
- Services are created lazily, that is they are only created for for the first time when they are required (that is a component that depends on the service is actually invoked). 

Let's take at the look of our definition of the "dummyService" from our initial example.

    ::javascript
    module.service('dummyService', ['$http', function ($http) {
        return {
            fetchJson: function () {
                return $http.get("example.json");
            }
        }
    }]);
   
In this example we're declaring a service which depends on the "$http" module, the first argument is simply the name of our new module, and in the second argument we provide a list which contains the dependencies we'll require, and as the last element of this list we provide a function, which when be called with our instantiated dependencies as it's arguments, will return an instance of our new "dummyService".

So let's start by creating a simple module class. To start with our module class will have one method, which we'll use to declare new services, and each module wil also have it's own instance of an "Injector" which which will handle instantiating and providing dependencies to components within our module.

    ::javascript
    var Module = function(moduleName, dependencies) {
        this.$injector = new Injector();

        this.service = function (serviceName, dependencies) {
            this.$injector.addDependency(serviceName, dependencies);

            return this;
        };
    }
    
In the above example note that we take in the module name and dependencies as arguments, but don't use this. We'll just do this to remain compatible with the AngularJS API, but to keep things simple we won't worry about modules depending on other modules.

Now, we've deferred all of the work in this module to our injector, so lets take a look and see how our injector is going to handle the creation and injection of instances of our services.

### Creating a simple "injector"

We'll start off by simply storing all of our dependencies in a dictionary that maps from their name, to the "injectables" (dependencies which need to be injected to create this dependency). That's simple enough, so now that we'll have a dictionary of all of our dependency definitions we're going to need to be able to "resolve" a dependency, that is get an instance of the dependency from it's name. 

The "resolveDependency" method will check if a dependency has been instantiated before to this point, and if it hasn't will create a new instance to be used in future. So to do that we'll also create another dictionary of singletons.

    ::javascript
    var Injector = function() {
        this.dependencies = {};
        this.singletons = {};

        this.addDependency = function (dependencyName, injectables) {
            this.dependencies[dependencyName] = injectables;
        };

        this.resolveDependency = function (moduleName) {
            if (moduleName in this.dependencies) {
                return this.getSingleton(moduleName);
            } else {
                throw new Error("Dependency " + moduleName +
                " could not be loaded;")
            }
        };

        this.getSingleton = function (dependencyName) {
            if (!(dependencyName in this.singletons)) {
                // No instance exists for this singleton, create it now.
                this.singletons[dependencyName] = this.invoke(this.dependencies[dependencyName]);
            }
            return this.singletons[dependencyName];
        };
    };
    
So that only leaves us with one more piece of the puzzle to solve for our injector, how does the "invoke" method create a new instance of our dependency?
    
### Invoking with the Inline array notation

 Let's take a closer look at the definition of our dummyService module.

    ::javascript
    ['$http', function ($http) {
        return {
            fetchJson: function () {
                return $http.get("example.json");
            }
        }
    }]
    
Our module is defined as a list, with all of the elements being the names of dependencies for our component, except for the last, which is a function which takes in the instantiated dependencies and returns an instance of our component.

So, if we call *Array.slice(0, -1)*, we'll get a list of our dependencies in string form. We can then map over this list with our resolveDependency function to transform it into a list of instantiated dependency components.

We know that the last element of our list is the function which will create an instance of our component, so all that we have to do is call the function with our list of newly resolved dependencies. To do this easily we can use the [Function.apply(thisArg, [argsArray])](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/apply) which will call the function with an array of arguments as if they had been provided separately.

So putting this all together our invoke method that handles the inline array notation will look something like this. 

    ::javascript
    this.invoke = function (injectables) {
        // Map to convert dependencies from strings into the singleton object
        var dependencies = injectables.slice(0, -1).map(this.resolveDependency, this);

        // Last item in the list is the module function
        var fn = injectables[injectables.length -1];

        // Create singleton object for this module
        // By calling the module function with all dependencies
        return fn.apply(null, dependencies);
    }
    
Note that our invoke function calls resolveDependency if there are any dependencies for a module, which in turn (indirectly) calls invoke again, which will means all of our dependencies for the module we're trying to create will be recursively instantiated.
    
    
### The other (magic) way of defining a component.

If we have a componenet with a large number of dependencies, using the Inline Array Notation leaves could leave us with a lot of code duplication, as we'd have to write the name of each dependency twice, once as an element of our list of dependencies, and once again as an argument to our function.

This is why AngularJS provides an alternative, "Implicit Annotations", where the dependencies are detected automatically by examining the names of the arguments to the factory function.

This allows us to write the declare our dummy service even more concisely.

    ::javascript
    module.service('dummyService', function ($http) {
        return {
            fetchJson: function () {
                return $http.get("example.json");
            }
        };
    });
    
    
How does AngularJS manage to detect the names of the dependencies without you explicitly stating them? 

Well to figure that out, you just have to remember that everything, including functions are objects in JavaScript. A function object does have an "arguments" property, but unfortunately that doesn't give us what we're looking for (it's the arguments passed to a called function, not those defined on the function). 

However JavaScript conveniently provides us which a [Function.toString()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/toString) method, which gives us the source code of a function as a string.

    ::javascript
    function ($http) {\nreturn {\nfetchJson: function () {\nreturn $http.get("example.json");\n}\n};\n}

Now with a string respresentation function, we can extract the arguments, with a regular expression to get the comma separated list of arguments from the string, which we can then split up to get a list of arguments.

We'll keep our extract method simple, which means we'll miss some corner cases (comments and weird spacing of arguments), but if you're interested you can check out the [AngularJS Injector code](https://github.com/angular/angular.js/blob/master/src/auto/injector.js#L82) for a complete solution.

So finally we'll add a method to our injector called extractArguments, based on the above AngularJS code.

    ::javascript
    var extractArguments = function(fn) {
        var FN_ARGS = /^function\s*[^\(]*\(\s*([^\)]*)\)/m;
        var FN_ARG_SPLIT = /,/;

        var argString = fn.toString().match(FN_ARGS);

        return argString[1].split(FN_ARG_SPLIT);
    };
    
Then we combine this method with our original invoke function, so that if we're passed a function directly we'll extract it's arguments to get our list of dependencies, otherwise we'll use our old code to handle the Inline Array Notation.
 
    ::javascript
    this.invoke = function (definition) {
        var dependencies, fn;
        if (typeof definition === 'function') {
            // Handling an implicit function notation
            fn = definition;
            dependencies = this.extractArguments(fn);
        } else {
            // Handling Inline Array Notation
            dependencies = definition.slice(0, -1);
            fn = definition[definition.length - 1];
        }

        // Create singleton object for this module
        // By calling the module function with all dependencies
        return fn.apply(null, dependencies.map(this.resolveDependency, this));
    }
    
One thing to note is that because we rely on the string representation of a function to detect dependencies, this method will break when code is minified (and the function arguments are renamed). Inline Array Notation still works fine however, as we inject based on the position of an argument, and use explicit strings to provide the names of dependencies.
    
    
### Putting it all together.

So let's go over what we've done in this blog post. We started by making a simple API compatible interface for AngularJS. To let us create modules, and components within them that are dependent upon eachother.

Here, we'll also define a run method, to check our implementation work, this just calls "invoke", allowing us define a component that can use any of the dependencies defined our module, but we'll ignore the return value (we just want some output).

    ::javascript
    var Module = function (moduleName, dependencies) {
        this.$injector = new Injector();

        this.service = function (serviceName, dependencies) {
            this.$injector.addDependency(serviceName, dependencies);

            return this;
        };

        this.run = function (injectables) {
            this.$injector.invoke(injectables);

            return this;
        }
    };

    var NotAngular = function() {
        this.module = function (moduleName, dependencies) {
            return new Module(moduleName, dependencies);
        };
    };
    

All of the work happens inside of our Injector, which handles instantiating and managing singletons of dependencies within our application. Our invoke method handles the two types of dependency annotation that we support, the explicit array style annotation, and the terser (but slightly more magical) implicit annotation.

    ::javascript
        var Injector = function () {
        this.dependencies = {};
        this.singletons = {};

        this.addDependency = function (dependencyName, injectables) {
            this.dependencies[dependencyName] = injectables;
        };

        this.resolveDependency = function (moduleName) {
            if (moduleName in this.dependencies) {
                return this.getSingleton(moduleName);
            } else {
                throw new Error("Dependency " + moduleName +
                " could not be loaded;")
            }
        };


        this.getSingleton = function (dependencyName) {
            if (!(dependencyName in this.singletons)) {
                // No instance exists for this singleton, create it now.
                this.singletons[dependencyName] = this.invoke(this.dependencies[dependencyName]);
            }
            return this.singletons[dependencyName];
        };

        this.extractArguments = function (fn) {
            var FN_ARGS = /^function\s*[^\(]*\(\s*([^\)]*)\)/m;
            var FN_ARG_SPLIT = /,/;

            var argString = fn.toString().match(FN_ARGS);

            return argString[1].split(FN_ARG_SPLIT);
        };


        this.invoke = function (definition) {
            var dependencies, fn;            
            if (typeof definition === 'function') {
                // Handling an implicit function notation
                fn = definition;
                dependencies = this.extractArguments(fn);
            } else {
                // Handling Inline Array Notation
                dependencies = definition.slice(0, -1);
                fn = definition[definition.length - 1];
            }

            // Create singleton object for this module
            // By calling the module function with all dependencies
            return fn.apply(null, dependencies.map(this.resolveDependency, this));
        }
    };
    
    
So if we put this all together with our dummy example from above (mixing the two types of annotations now).

    ::javascript
    var angular = new NotAngular();
    var module = angular.module('testModule', []);

    module.service('$http', [function () {
        return {
            get: function (url) {
                return "Got data from: " + url;
            }
        }
    }]);

    module.service('dummyService', function ($http) {
        return {
            fetchJson: function () {
                return $http.get("example.json");
            }
        }
    });

    module.run(['dummyService', function (dummyService) {
        console.log(dummyService.fetchJson());
    }]); 
    
We'll get the output of: 

	Got data from: example.json


### That's all folks

As we saw in the Flask post before, a dictionary mapping from strings to callables is a key ingredient to the more useful APIs provided by some of our favourite open source libraries. Mixing that pattern with a few neat JavaScript tricks allows us to replicate some of the nifty API that AngularJS provides in under 100 lines of JS.

All of the code from this post can be found [over on GitHub](https://github.com/ains/twam-angular).

Next time we'll be sticking with the JavaScript theme for just a tiny bit longer to have a look at how JSONP works, and why it's one of my favourite (horrible) hacks of all time.