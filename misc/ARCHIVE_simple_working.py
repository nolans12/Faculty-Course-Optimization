###### GOAL: Use pulp lineazr programming to optimize faculty assignments to courses based on their preferences and TC constraints

import numpy as np
import pandas as pd
import pulp

# Load the data
faculty = pd.read_csv("faculty_w_TC.csv")
courses = pd.read_csv("courses_w_TC.csv")

survey_teaching = pd.read_csv("Teaching Survey.csv")
survey_tenure = pd.read_csv("Tenure Survey.csv")

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

# Create a faculty class that stores their name, and preferences
    # If the equivalence is filled out, puts it as the same preference
    # Preferences will be stored in a dict containing [course: preference]
    # Will split out the courses by the first ":" hit, thus, will be "Fall - ASEN 2402", etc.

class Faculty:
    def __init__(self, name, TC):
        # Name of the faculty and teaching credits needed to teach
        self.name = name
        self.TC = TC
        self.preferences = {} # Will be a dict of [course: preference]

    def add_pref(self, course, pref):
        # Add the course with a given preference to the preferences

        # If the course is already in the preferences, return
        if course in self.preferences:
            print(f"For {self.name}, {course} is already in the preferences")
            return
        self.preferences[course] = pref

    def add_equiv(self, equiv_array):
        """
        Equiv array will be an array of two integers, [1, 2] for example
        Will take the format of [pref_match, pref_matcher] where want to set the preference of pref_matcher to the preference of pref_match
        But, have to deal with daisy chaninig, so while loop until find the next highest preference, if it doesnt exist
        """

        if self.name == "Argrow, Brian":
            test = 1
        
        pref_match = equiv_array[0]
        pref_matcher = equiv_array[1]

        # Easily find the course your trying to change the pref of
        course2 = None
        for course, pref in self.preferences.items():
            if pref == pref_matcher:
                course2 = course
                break

        if course2 == None:
            return
            
        # Now, find the course you want to match the preference of
        # First, try just using the pref mentioned in equiv_array
        course1 = None
        for course, pref in self.preferences.items():
            if pref == pref_match:
                course1 = course
                break

        # Now, check, if course1 is none, take the next highest preferences value
        if course1 == None:
            # Get the lowest preference in the courses that is > pref_match
            pref_match = pref_match - 1
            while pref_match > 0:
                for course, pref in self.preferences.items():
                    if pref == pref_match:
                        course1 = course
                        break
                if course1 != None:
                    break
                pref_match = pref_match - 1
        
        # Now, set the preference of course2 to the preference of course1
        self.preferences[course2] = self.preferences[course1]


def split_course_name(course):
    """
    Simply splits the course name by the first :
    Thus, Fall - ASEN 3801: Vehicle Dynamics and Control Lab (Might be team taught: 1-2 people) -> Fall - ASEN 3801
    """
    return course
    # return course.split(":")[0]


# Create a faculty object for each faculty member, from the faculty csv
faculty_list = []
for index, row in faculty.iterrows():
    name = row["Name"]
    TC = row["TC Needed"]
    faculty_list.append(Faculty(name, TC))


def add_survey_data(survey, faculty_list, linker):
    # ADD THE TEACHING PREFERENCES
    # Loop through the survey_teaching data
    for index, row in survey.iterrows():

        # Get the name from the survey
        survey_name = row[linker["name"]]

        # See if that name is in the faculty list
        for faculty in faculty_list:
            if faculty.name == survey_name:
                # Loop through the preferences
                for linker_key, survey_value in linker.items():
                    # If it's a preference, add it to the faculty object
                    if "pref" in linker_key:

                        # Check, does the linker key exist in the row? and if so is the value for that key null?
                        if survey_value not in row:
                            continue
                        if pd.isnull(row[survey_value]):
                            continue

                        # Get the course
                        course = row[survey_value]

                        # Split the course name
                        course = split_course_name(course)

                        # Add the preference to the faculty object
                        pref = int(linker_key.split("_")[1])

                        faculty.add_pref(course, pref)
        

    # ADD THE EQUIVALENCES
    # Loop through each faculty member and add their equivalences (courses should already have been added)
    for index, row in survey.iterrows():

        # Get the name from the survey
        survey_name = row[linker["name"]]

        # See if that name is in the faculty list
        for faculty in faculty_list:
            if faculty.name == survey_name:
                # Now, for this faculty, loop through the linker and add the equivalences
                for linker_key, survey_value in linker.items():
                    if "equiv" in linker_key:
                    # Check, does the linker key exist in the row? and if so is the value for that key null?
                        if survey_value not in row:
                            continue
                        if pd.isnull(row[survey_value]):
                            continue

                        # If the value is not null, means this faculty member selected the equivalence!
                        # Get the equivalence, split by _, such as "equiv_1_2" -> [1, 2] have the same preference
                        equiv = linker_key.split("_")[1:]
                        equiv = [int(x) for x in equiv]
                        faculty.add_equiv(equiv)


add_survey_data(survey_teaching, faculty_list, linker)
add_survey_data(survey_tenure, faculty_list, linker)

                    
# print out the faculty preferences
for faculty in faculty_list:
    print(faculty.name)
    for course, pref in faculty.preferences.items():
        print(course, pref)
    print("\n\n")

## Now, create the optimization problem

# Get n, the number of faculty objects that actually have preferences (took the survey)
# Purge the faculty list of those who didn't take the survey
faculty_list = [faculty for faculty in faculty_list if len(faculty.preferences) > 0]

n = len(faculty_list)

# Now, we can define the cost function. 
def cost(faculty, course):
    """
    Cost function for the optimization problem.

    Input is a faculty object and a course name
    Cost is 2**(log2(n)*(pref - 1)) where pref is the preference of the faculty for the course
    """
    # Shorten the course name
    course = split_course_name(course)
    if course in faculty.preferences:
        pref = faculty.preferences[course]
        return 2**(np.log2(n)*(pref - 1))
    else:
        return int(1e15)


def tc_amount(course):
    """
    Returns the number of teaching credits needed to teach the course

    Where a course looks like "Fall - ASEN 3801: Vehicle Dynamics and Control Lab (Might be team taught: 1-2 people)"
    """
    # In general, this will just return the amount specified in the courses csv. 
    # But! If it is an option for "(teaching 1 secion)" or "(teaching 2 sections)", will return 1 or 2
    if "1 section" in course:
        return 1
    if "2 sections" in course:
        return
    
    return 1


# Now that we have the cost function, we can create the optimization problem
# Create the LP object
prob = pulp.LpProblem("Faculty Optimization", pulp.LpMinimize)

# Create the decision variables
# x_i_j is 1 if faculty i is assigned to course j, 0 otherwise
x = pulp.LpVariable.dicts("x", ((i, j) for i in range(n) for j in range(len(courses))), 0, 1, pulp.LpBinary)

# Add the cost function to the LP
prob += pulp.lpSum(cost(faculty_list[i], courses["Course"][j]) * x[i, j] for i in range(n) for j in range(len(courses)))

# Add the constraints
# Each faculty member can only be assigned to one course
for i in range(n):
    prob += pulp.lpSum(x[i, j] for j in range(len(courses))) == faculty_list[i].TC

# Each course must have AT LEAST the number of faculty members needed to teach it
for j in range(len(courses)):
    # prob += pulp.lpSum(x[i, j] for i in range(n)) <= courses['TC'][j]
    # The sum of the teaching credits for a faculty teaching a course must be <= the TC max for that course
    prob += pulp.lpSum(tc_amount(courses["Course"][j]) * x[i, j] for i in range(n)) <= courses['TC per teacher'][j]

# Solve the problem
prob.solve()

# Print the results
for i in range(n):
    for j in range(len(courses)):
        if pulp.value(x[i, j]) == 1:
            preference = faculty_list[i].preferences[split_course_name(courses["Course"][j])]
            print(f"{faculty_list[i].name} assigned to {courses['Course'][j]} with preference {preference}")

# Also make a plot of the results, how many of what preference were assigned
# Create a dictionary of preferences
pref_dict = {i: 0 for i in range(1, 9)}

for i in range(n):
    for j in range(len(courses)):
        if pulp.value(x[i, j]) == 1:
            course = split_course_name(courses["Course"][j])
            pref = faculty_list[i].preferences[course]
            pref_dict[pref] += 1

# Now, plot the results
import matplotlib.pyplot as plt

plt.bar(pref_dict.keys(), pref_dict.values())
plt.xticks(list(pref_dict.keys()))
plt.yticks(np.arange(0, max(pref_dict.values()) + 1, 1))
plt.xlabel("Preference")
plt.ylabel("Number of Assignments")
plt.title("Number of Assignments for Each Preference")

plt.show()