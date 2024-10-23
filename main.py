###### GOAL: Use pulp lineazr programming to optimize faculty assignments to courses based on their preferences and TC constraints

import numpy as np
import pandas as pd
import pulp

from data_processing_funcs import Faculty, add_survey_data
from post_run_data_funcs import output_faculty_prefs, output_course_assignments, print_course_assignments, plot_preferences, plot_preferences_2

# Load the data
faculty = pd.read_csv("inputs/final_faculty_w_TC.csv")
courses = pd.read_csv("inputs/final_courses_w_TC.csv")

survey_teaching = pd.read_csv("inputs/teaching_final_survey.csv")
survey_tenure = pd.read_csv("inputs/tenure_final_survey.csv")

forcing_list = pd.read_csv("inputs/forcings.csv")
banning_list = pd.read_csv("inputs/bannings.csv")

# Now put a linker which links the survey field name to the actual data
    # Can use survey_teaching.columns to get the column names
    # TODO: ADD SABBATICAL LATER
linker = {
    "name": "Q Name _1",
    "pref_1": "Q1 _1",
    "pref_2": "Q2_1",
    "pref_3": "Q3_1",
    "pref_4": "Q4_1",
    "pref_5": "Q5_1",
    "pref_6": "Q6_1",
    "pref_7": "Q7_1",
    "pref_8": "Q8_1",
    "equiv_1_2": "Q12",
    "equiv_2_3": "Q23",
    "equiv_3_4": "Q34",
    "equiv_4_5": "Q45",
    "equiv_5_6": "Q56",
    "equiv_6_7": "Q67",
    "equiv_7_8": "Q78",
}


## Collect and format the data

# Create a faculty object for each faculty member, from the faculty csv
faculty_list = []
for index, row in faculty.iterrows():
    name = row["Name"]
    TC = row["TC Needed"]
    faculty_list.append(Faculty(name, TC))

# Add both surveys to the faculty objects
add_survey_data(survey_teaching, faculty_list, linker)
add_survey_data(survey_tenure, faculty_list, linker)

# Output the csv to analyze the preferences
output_faculty_prefs(faculty_list)
# Can set a breakpoint here and look at preferences using Faculty.name and Faculty.preferences


## Now, lets set up the optimization problem!

# We need n, the number of faculty objects that actually have preferences (took the survey)
n = len(faculty_list) 


## Create the optimization instance
prob = pulp.LpProblem("Faculty Optimization", pulp.LpMinimize)


## Create the decision variables
    # We need a decision vairable for each faculty - course combo
    # BUT! For the courses that have multiple sections that can be split, we also need a TC for each sections
    # i.e. if course X has 3 TC, we need a decision variable for X (1 TC), X (2 TC), and X (3 TC)

# Loop through the faculty and courses
x = {}
for idx, row in courses.iterrows(): # Each row of the survey

    # Get the data
    course = row["Course"] # unfortunately splitting the course to just shorted like "ASEN 3711" wont work for senior projets 

    total_TC = row["Total TC"]
    split_TC = row["TC Per Split"]

    # Check, does total_TC / split_TC come out to a int?
    if abs(total_TC % split_TC) < 1e-2:  # Using a small threshold for floating-point comparison
        num_splits = round(total_TC / split_TC)
    else:
        print(f"Course {course} has a non-integer split TC amount!!!")
        exit()

    multiple_sections = row["Allow Multiple Sections"] # will either be nan or true
    # Now check, if Allow Multiple Sections isn't true (false), then just one decision variable

    if pd.isna(multiple_sections):
        num_splits = 1

    # Create the decision variables
    for faculty in faculty_list:
        name = faculty.name
        for j in range(round(num_splits)):
            x[(name, course, j + 1)] = pulp.LpVariable(f"x_{name}_{course}_{j + 1}", 0, 1, pulp.LpBinary)


# ## Testing decsion variables
# for key, value in x.items():
#     name, course, sections = key
#     print(f"Faculty: {name}, Course: {course}, Section: {sections}")
#     test = x[key]
#     has a format like [Hodgkinson Bobby, Fall - ASEN 1030: Intro to Computing - Lecture and Lab, 2] # for teaching 2 section of ASEN 1030


## Create the cost function
    # The cost function is based on the faculty preferences
    # TODO: could add section number? 
        # At the moment, preferences b/w different section amounts are counted the same
        # i.e. ASEN 2402 (teaching 1 section) and ASEN 2402 (teaching 2 sections) are counted the same cost, highest preference
        # this is only a option for teaching faculty anyways
def cost(faculty, course, sections): 
    """
    Cost function for the optimization problem.

    Input is a faculty object, and a course
    """

    if course == "Fall - ASEN 4519: Special Topics": # This is purely to accoutn for the fact that teaching 5 sections of 4519 costs alot
        multiplier = sections
    else:
        multiplier = 1

    # To account for fact could have (teaching 1 section) and (teaching 2 sections) for same course, cant just string match right from dict, have to loop
    for course_pref, pref in faculty.preferences.items():
        if course in course_pref: # this works for substring matching, so "ASEN 2402" will match "ASEN 2402 (teaching 2 sections)"
            return 2**(np.log2(n)*(pref - 1))

    # If the course is not in the preferences, return a very high cost
    return multiplier * 2**(np.log2(n)*(9 - 1))

# # ## Test cost funciton with "Hodgkinson, Bobby", Fall - ASEN 1030: Intro to Computing - Lecture and Lab (teaching 1 section)"
# for faculty in faculty_list:
#     if faculty.name == "Schwartz, Trudy":
#         break
# print(cost(faculty, "Spring - GEEN 1400: Freshman Projects"))
# Should string match to the (teaching 1 section) preference


# Initialize an empty list to store the cost terms
cost_terms = []

# Loop through the decision variables and calculate the cost for each
for key, value in x.items():
    name, course, section = key

    # Find the faculty object with the name
    for faculty in faculty_list:
        if faculty.name == name:
            break

    # Append the cost term to the list
    cost_terms.append(cost(faculty, course, section) * x[key])

# Sum the list of cost terms, will be the objective function!
prob += pulp.lpSum(cost_terms)


# # Add the constraints
#     Constraint for each faculty member that they must meet their TC amount
#     Constraint for each course the total TC cannot be exceeded
#     Constraint for all the forcings
    
## Faculty TC constraint
    # Need a for loop that goes back into the course data to get the TC split amount
for faculty in faculty_list:
    faculty_name = faculty.name

    # For this faculty, need a constraint on the sum of the TC for each course == their TC amount
    # Start an empty list to store the constraints
        # One for each faculty
    constraints = []

    # Loop through the decision variables
    for key, value in x.items():
        name, course, section = key

        if name == faculty_name:
            # Get how much each section is worth
            split_TC = courses[courses["Course"] == course]["TC Per Split"].values[0]

            # Append constraint
            constraints.append(split_TC * section * x[key])

    # Add the net TC constraint for this faculty
    prob += pulp.lpSum(constraints) >= faculty.TC - 0.3
    prob += pulp.lpSum(constraints) <= faculty.TC + 0.3


## Course TC constraint
    # The total TC for each course cannot be exceeded
    # Need to loop through the courses and add a constraint for each
for idx, row in courses.iterrows():
    course = row["Course"]
    course_TC = row["Total TC"]
    split_TC = row["TC Per Split"]
    multiple_sections = row["Allow Multiple Sections"]

    if course == "Fall - ASEN 4519: Special Topics": # Skip this course, it has a ton of extra TC just as a buffer
        continue

    # Check, does total_TC / split_TC come out to a int?
    if abs(course_TC % split_TC) < 1e-2:  # Using a small threshold for floating-point comparison
        num_splits = round(course_TC / split_TC)
    else:
        print(f"Course {course} has a non-integer split TC amount!!!")
        exit()

    # Now check, if Allow Multiple Sections isn't true, then just one decision variable
    if pd.isna(multiple_sections):
        num_splits = 1

    # Start an empty list to store the constraints
        # One for each course
    constraints = []

    # Loop through the decision variables
    for key, value in x.items():
        name, course_name, section = key

        # Now add this instance to the constraint if the course name matches
        if course_name == course:
            constraints.append(split_TC * section * x[key])

    # Add the final constraint for this course with a ±0.1 margin
    prob += pulp.lpSum(constraints) >= course_TC - 0.1
    # prob += pulp.lpSum(constraints) <= course_TC + 0.6
    prob += pulp.lpSum(constraints) <= course_TC + 2.1   


## Also add the constraint that a faculty cannot teach the same course twice, used to not allow more than one section of a course
for course in courses["Course"]:
    for faculty in faculty_list:
        constraints = []
        for key, value in x.items():
            name, course_name, section = key
            if course_name == course and name == faculty.name:
                constraints.append(x[key])
        prob += pulp.lpSum(constraints) <= 1


# # Also add the constraint that no faculty can teach senior projects for more than 2 TCs
# This way teaching faculty can get 2 TC from projects, otherwise tenure get 1
for course in courses["Course"]:
    if course == "Fall and Spring - ASEN 4018: Senior Projects (PAB Member, 8 people)":
        for faculty in faculty_list:
            constraint = []
            for key, value in x.items():
                name, course_name, section = key
                if name == faculty.name and course_name == course:
                    constraint.append(x[key] * section)
            prob += pulp.lpSum(constraint) <= 2


## Now, add the forcings as a constraint
for idx, row in forcing_list.iterrows():
    course = row["Course"]
    faculty = row["Faculty"]
    sections = row["Sections"]

    # Additionally, find that faculty and add this forcing course as a #1 preference
    for faculty_search in faculty_list:
        if faculty_search.name == faculty:
            faculty_search.preferences[course] = 1

    # Add the forcing constraint
    prob += x[(faculty, course, sections)] == 1


## Also add banning contraints
for idx, row in banning_list.iterrows():
    # Set that decision variable to 0
    faculty = row["Faculty"]
    course = row["Course"]
    for key, value in x.items():
        name, course_name, section = key
        if course_name == course and name == faculty:
            prob += x[key] == 0
           

# Now, the optimization problem is set up, solve it!
prob.solve()


## Outputs
# print_course_assignments(x, faculty_list)
output_course_assignments(x, courses, faculty_list)
plot_preferences_2(x, n, courses, faculty_list)