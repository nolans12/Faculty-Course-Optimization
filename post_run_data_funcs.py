import pandas as pd
import pulp
import numpy as np
import matplotlib.pyplot as plt


# Function to output the faculty preferences to a csv file
def output_faculty_prefs(faculty_list, saveName = "outputs/faculty_preferences.csv"):
    
    # Create a list of dictionaries to store the faculty preferences
    faculty_prefs_list = []
    for faculty in faculty_list:
        for course, pref in faculty.preferences.items():
            faculty_prefs_list.append({"Faculty": faculty.name, "Course": course, "Preference": pref})

        # If empty preferences, just print the name
        if len(faculty.preferences) == 0:
            faculty_prefs_list.append({"Faculty": faculty.name, "Course": "", "Preference": ""})

        faculty_prefs_list.append({})

    faculty_prefs = pd.DataFrame(faculty_prefs_list)
    faculty_prefs.to_csv(saveName, index=False)


# Function to print the course assignments
def print_course_assignments(x, faculty_list):

    # Create a dictionary to store assignments grouped by courses
    course_assignments = {}

    # Populate the dictionary with assignments
    for key, value in x.items():
        if value.varValue == 1:
            name, course, section = key
            
            # get that profs preference
            for faculty in faculty_list:
                if faculty.name == name:
                    break

            for course_pref, pref in faculty.preferences.items():
                if course in course_pref:
                    preference = pref
                    break

            if course not in course_assignments:
                course_assignments[course] = []
            
            course_assignments[course].append((name, section, preference))

    # Print the assignments grouped by courses
    for course, assignments in course_assignments.items():
        print(f"{course}")
        for name, section, preference in assignments:
            print(f"{name} assigned to {course} for {section} sections with preference {preference}")
        print()  # New line before the next course


def output_course_assignments(x, courses, faculty_list, saveName = "outputs/course_assignments.csv"):

    # Create a dictionary to store assignments grouped by courses
    course_assignments = {}

    # Populate the dictionary with assignments
    for key, value in x.items():
        if value.varValue == 1:
            name, course, section = key

            # get that profs preference
            for faculty in faculty_list:
                if faculty.name == name:
                    break

            preference = 99  # Default preference if course is not found
            for course_pref, pref in faculty.preferences.items():
                if course in course_pref:
                    preference = pref
                    break

            # Get the TC allocation for this course
            tc_allocation = 0
            for _, row in courses.iterrows():
                if row['Course'] == course:
                    tc_allocation = row['TC Per Split'] * section
                    break

            if course not in course_assignments:
                course_assignments[course] = []
            
            course_assignments[course].append((name, section, preference, tc_allocation))

    # Create a list of dictionaries to store the course assignments
    course_assignments_list = []
    for course, assignments in course_assignments.items():
        for name, section, preference, tc_allocation in assignments:
            course_assignments_list.append({"Course": course, "Faculty": name, "Sections Taught": section,"TC Amount": tc_allocation, "Preference": preference})
        course_assignments_list.append({})

    course_assignments_df = pd.DataFrame(course_assignments_list)
    course_assignments_df.to_csv(saveName, index=False)


def plot_preferences(x, n, courses, faculty_list):

    # Create a dictionary of preferences
    pref_dict = {i: 0 for i in range(1, 10)}

    # Populate the dictionary with assignments
    for key, value in x.items():
        if value.varValue == 1:
            name, course, section = key

            # get that profs preference
            for faculty in faculty_list:
                if faculty.name == name:
                    break

            preference = 9  # Default preference if course is not found
            for course_pref, pref in faculty.preferences.items():
                if course in course_pref:
                    preference = pref
                    break

            pref_dict[preference] += 1

    
    plt.bar(pref_dict.keys(), pref_dict.values())
    plt.xticks(list(pref_dict.keys()))
    plt.yticks(np.arange(0, max(pref_dict.values()) + 1, 1))
    plt.xlabel("Preference")
    plt.ylabel("Number of Assignments")
    plt.title("Number of Assignments for Each Preference")
    plt.show()


def plot_preferences_2(x, n, courses, faculty_list):

    # Define the names of the teaching faculty:
    teaching = ["Glusman, Jeff", "Hoke, Charles", "Hodgkinson, Bobby", "Knudsen, Erik", "Le Moine, Alexandra", "Mah, John", "Rafi, Melvin", "Wingate, Kathryn", "Scott, Hank", "Rhode, Matt", "Schwartz, Trudy"]

    # Now, make one plot, but it has two different colros for the preferences.
    # In blue is the tenure preferences, in red is the teaching preferences.

    pref_tenure = {i: 0 for i in range(1, 10)}
    pref_teaching = {i: 0 for i in range(1, 10)}

    # Populate the dictionary with assignments
    for key, value in x.items():
        if value.varValue == 1:
            name, course, section = key

            # get that profs preference
            for faculty in faculty_list:
                if faculty.name == name:
                    break

            preference = 9  # Default preference if course is not found
            for course_pref, pref in faculty.preferences.items():
                if course in course_pref:
                    preference = pref
                    break

            if faculty.name in teaching:
                pref_teaching[preference] += 1
            else:
                pref_tenure[preference] += 1

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot tenure preferences in blue
    ax.bar(pref_tenure.keys(), pref_tenure.values(), color="blue", label="Tenure Faculty")

    # Stack teaching preferences on top in red
    ax.bar(pref_teaching.keys(), pref_teaching.values(), color="red", 
           bottom=list(pref_tenure.values()), label="Teaching Faculty")

    ax.set_xlabel("Preference")
    ax.set_ylabel("Number of Assignments")
    ax.set_title("Faculty Preferences")
    ax.set_xticks(list(pref_tenure.keys()))
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend()

    plt.tight_layout()
    plt.show()
