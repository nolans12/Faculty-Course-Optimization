import pandas as pd


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
