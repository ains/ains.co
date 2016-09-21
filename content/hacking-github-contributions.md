Title: Playing with the GitHub Contribution Calendar
Date: 2014-01-29 22:50
Category: Programming
Tags: javascript, python, flask, github, d3
Slug: hacking-github-contributions
Author: Ainsley Escorce-Jones
Summary: Playing around with the GitHub Contribution Calendar and making tagGIT - an easy way to draw your own GitHub contribution calendar.	

<a href="https://github.com/gitgen">
	<img style="width: 700px;" src="theme/img/hacking-github-contributions/hello-world.png"/>
</a>

It's been a while since I've done a quick and dirty hack that's worth sharing. But inspiration sometimes comes from [strange places](https://github.com/turkishdelighthorse). This particular hack is a way more fun to play with than to talk about, so I'll keep it brief.

If you want to just check out the hack straight away (it's fairly self explanatory) just click [here](http://taggit.ains.co/)

##Contribution Graph Hacking

People have been playing with their GitHub contribution calendars for a while now, the process is fairly simple, by using the "--date" option with "git commit" you can submit a commit from any point in time. GitHub will then plot this data along with your activity on any other repositories on your contribution calendar. The way in which the calendar is shaded is explained excellently in this [blog post](http://bd808.com/blog/2013/04/17/hacking-github-contributions-graph).

As a quick hack I figured it'd be fun to let a user draw their desired contribution calendar, and then to automatically generate the corresponding repository, and thus [tagGIT](http://taggit.ains.co/) was born.

tagGIT is based on this [calendar example](http://mbostock.github.io/d3/talk/20111018/calendar.html) from D3.js which has been been modified to be editable. There's also a Flask application which creates the corresponding git repository and creates a tarball for the user to download.

The source code for tagGIT is available over on [Github](https://github.com/ains/tagGIT), contributions are always welcome.