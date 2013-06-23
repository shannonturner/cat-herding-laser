----------------------------
 What is Cat Herding Laser?
----------------------------

Cat Herding Laser is a program that allows you to create a customized survey that, upon completion, generates an Un-form letter.

For a jazzier presentation, see Cat Herding Laser.pdf

------------------------------
 How to use Cat Herding Laser
------------------------------

Everything provided in this repository will allow you to set up a local copy of Cat Herding Laser so you can see how it works.  Most importantly, you'll want:

survey.txt: the properly formatted text file containing the survey you'd like to use
howto_survey.txt: all of the instructions on how to properly format that text file so you can make your own surveys

--------------------------------------------
 Using Cat Herding Laser: A bird's eye view
--------------------------------------------

1) Create your survey!
2) Run it through the validator to make sure you've formatted everything correctly
3) When you've created your survey, Cat Herding Laser will tell you the survey_id
4) Send people to the survey to fill it out at /survey?survey_id=<your survey_id from Step 3>
5) When someone completes your survey, they'll get their own custom Un-form letter.  You can customize the program so that they can send that letter to the target of your choice (though that's not explicitly included, you're free to customize your form to allow it).
6) Your survey is shareable with the survey_id
7) You can see the responses to your survey at any time

--------------------------------------------------
 Setting up Cat Herding Laser for the first time:
--------------------------------------------------

1) Cat Herding Laser uses CherryPy to display its surveys, so you'll need to download and install that if you don't already have it.  http://cherrypy.org/
2) Use the provided survey.txt, or create your own survey according to the instructions in howto_survey.txt
3) Launch the Cat Herding Laser.  From the command line on your local computer, run: python catherdinglaser.py
4) If you used the default configuration file provided in this repository (cfg.cfg), you'll go to http://127.0.0.1:8080
5) Your options are now:

5a) http://127.0.0.1:8080/validate - this will be your first step, where you can check to make sure you've formatted your survey correctly.

5b) http://127.0.0.1:8080/admin - this will be your second step, where you can create the survey and customize the look and feel of the page
	
After completing step 5b), you'll receive a survey_id that you can use.  If creating your survey was successful, you'll also notice some new files in your directory.
	
5c) http://127.0.0.1:8080/survey - to see your survey, you'll go to http://127.0.0.1:8080/survey?survey_id=<the survey_id you received in step b> (be sure to omit the < and >)
	
When someone completes the survey in step 5c), their answers will be saved to a file in your directory and they'll be sent to /submit where they'll see their completed Un-form letter.  
If you customized your form to allow it, they can send the Un-form letter to the target of your choice now.
	
There are other pages that get used by Cat Herding Laser, but you won't go to those directly.  These include /createsurvey and /submit.

-------------------------------------------------
 Comments / Suggestions / Feature Requests / etc
-------------------------------------------------

 I'm @svt827 on Twitter.