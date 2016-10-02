***Overview***

This tool is designed to track the progress of Newly Hired college graduates (NCH).

The onboarding consists of 

1. A test to baseline the NCH 
2. Training on the specific language you need
3. Short 3 month projects
4. A training test which allows NCHs to train.
  (This test is open for the duration of 3 months, so NCHs can take the test in their free time and learn)
5. A test at the end to see how they are progressing and also to show the efficacy of the training.
6. intermediate and final project presentations

The web app consists of the following

1. **A testing application**
  - tests basic coding skills in any language. (ala google codejam)
  - allows you to upload and create questions.
  - execution of code is done on the clients computer
  - create and schedule tests
  - track how your test takers are doing
    - How many logged in, Which questions they have attempted and at what time, Which questions they passed,
      number of failed attempts.

2. **A project tracking module**
  - Setup projects assigning Director, Mentor and NCH roles
  - Upload milestones for a configurable number of readouts
  - Track status of projects on these milestones. 
    - Projects will show red if more than half of required milestones for a particular date are incomplete.
      Will be orange if less than half are incomplete, and green if everything is complete
  - Add judges for a particular batch
  - Design a scorecard which each judge will need per
  - calculate score per readout and display each judge's rating.
  
***Technology***
 
  Simple django project can be run using Apache as frontend. SQL backend.
  Relies on ldap for authentication, other than for the superuser.
  UI looks a bit horrible but I think it passes as focussed on the task at hand (Any help here would be much appreciated)
  
***Django setup***
  
  Please go through the settings.py and update all the necessary variables! Especially the directory.
  
*ToDo*

1. *A view to show the scores of the test*. 

    (This wasnt found important for people who wanted the tool, they didnt want anyone else to see NCH scores.
    I used to download the data in an excel and give it to them)

2. *A better UI!!!*
   
   (Presently uses a simple django-forms UI with bootstrap and very minimal styling)
   
