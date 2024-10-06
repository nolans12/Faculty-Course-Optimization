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


def output_course_assignments(x, faculty_list, saveName = "outputs/course_assignments.csv"):

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

    # Create a list of dictionaries to store the course assignments
    course_assignments_list = []
    for course, assignments in course_assignments.items():
        for name, section, preference in assignments:
            course_assignments_list.append({"Course": course, "Faculty": name, "Sections Taught": section, "Preference": preference})
        course_assignments_list.append({})

    course_assignments_df = pd.DataFrame(course_assignments_list)
    course_assignments_df.to_csv(saveName, index=False)


def plot_preferences(x, n, courses, faculty_list):

    # Create a dictionary of preferences
    pref_dict = {i: 0 for i in range(1, 9)}

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

            pref_dict[preference] += 1

    
    plt.bar(pref_dict.keys(), pref_dict.values())
    plt.xticks(list(pref_dict.keys()))
    plt.yticks(np.arange(0, max(pref_dict.values()) + 1, 1))
    plt.xlabel("Preference")
    plt.ylabel("Number of Assignments")
    plt.title("Number of Assignments for Each Preference")
    plt.show()

