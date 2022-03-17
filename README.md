# EDAP01
Home assignments from EDAP01 - Artificial Intelligence course, LTH, https://kurser.lth.se/lot/course-syllabus/21_22/EDAP01

It contains the home assignments from Artificial Intelligence course. 

The first assignment, A1, provides a Alpha-Beta cutoff implementation for a Connect Four game. The framework for the project was given, but the functions that implement the Alpha-Beta algorithm, the heuristic function an the other functions necessary for these two were coded by me (lines 78 - 348 from the skeleton file).

The second assignment, A2, is a jupyter notebook containing implementations for Batch Gradient Descent algorithm, Stochastic Gradient Descent algorithm, linear regression, logistic regression and perceptron classification.

The third assignment, A3, provides a HMM implementation for finding the location of a robot. The framework for the project was given, I coded the Robot Simulator (that moves the robot one step and generates a state; then it gets the sensor reading produced based on the state) and the HMM filter. These two can be seen in RobotSimAndFilter (RobotSim class) and Localizer (hmmFilter() and update() methods) files. The results can be analyzed using the RobotLocWrapper notebook.

SimpleCourseRecommender contains the implementation of a simple course recommender system using the cosine similarity between the mark / grade vectors. 

