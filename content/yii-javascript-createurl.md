Title: Creating Yii URLs in JavaScript: The Nice Way
Date: 2013-07-17 17:00
Category: Programming
Tags: javascript, yii, createurl, programming
Slug: yii-javascript-createurl
Author: Ainsley Escorce-Jones
Summary: Developing a nicer way to use Yii's URL Management from JavaScript, in order to make custom code which depends on AJAX calls easier to write, maintain and serve up.

Whenever I'm writing a Web Application in PHP I love to get stuck in with the [Yii Framework](http://www.yiiframework.com/). Yii is often overlooked but is a fast, mature and stable PHP Framework which makes rapidly building or prototyping a Web app a joy.

##The URL Manager
Yii sports great [URL Management](http://www.yiiframework.com/doc/guide/1.1/en/topics.url) features, the URL Manager in Yii handles everything from the simple hiding of index.php to incredibly complicated rules which can use regular expressions. 

Centralising the URL Management behaviour means that as long as you issue calls to "Yii::app()->createUrl()" any changes to your URL Manager rules are propagated throughout your application without any further changes.

Unfortunately this tight dependency on calling the createUrl method from the Yii framework means that in order to write custom JavaScript code which makes AJAX calls you either have to intermingle PHP echo statements with your JavaScript code (which means they can't be stored as separate files), or utilise other [fairly awkward workarounds](http://www.yiiframework.com/forum/index.php/topic/17731-get-baseurl-in-javascript/) (exporting generated URLs as JavaScript variables)

##A Nicer Solution
In order to avoid the awkward workaround of having to predefine every URL in JavaScript code within the header of your page, or having to mix dynamic PHP code with static JavaScript assets I wrote an implementation of the Yii CUrlManager class in JavaScript.

Having the ability to access the URL Manager directly from JavaScript code, whilst maintaining all previously defined rules, means that all of your JavaScript code can be kept separately from your PHP code, and can as a result be treated as static assets (stored on a CDN or minified).

##A Simple Example
Previously to utilise the power of the URL Manager in Yii with an AJAX call the following code wouldn't be uncommon in a view file:

	$('#result').load(<?= Yii::app()->createUrl('user/view', array('id' => 1); ?>), function() {
  		alert('Load was performed.');
	});
	
However utilising the JavaScript URL Manager the example can be written as:

	$('#result').load(Yii.app.createUrl('user/view', {id: 1})), function() {
  		alert('Load was performed.');
	});
	
The latter example is pure JavaScript so it can then be moved into a separate file and served up like any other static asset. Much nicer.

The JSUrlManager is available over on [Github](https://github.com/ains/Yii-JSUrlManager), along with installation instructions and details of any known issues.