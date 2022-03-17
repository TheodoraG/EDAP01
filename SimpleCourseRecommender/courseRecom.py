#a simple course recommender system based on marks given in each course

#encoding the dataset
#the keys are the students and the values are the marks
#each value is a dictionary where key is the course name and the value is the mark
kodal = {
    'tad12aaa': {'ABC01': 3, 'ABC02': 'U', 'ABC03': '?', 'ABC04': 4, 'CBA01': 5},
    'yft14xxx': {'ABC01': 4, 'ABC02': '?', 'ABC03': 3, 'ABC04': '?', 'CBA01': 5},
    'tad10bbb': {'ABC01': 5, 'ABC02': '?', 'ABC03': 5, 'ABC04': 3, 'CBA01': '?'},
    'tad11ccc': {'ABC01': 3, 'ABC02': '?', 'ABC03': 'U', 'ABC04': 4, 'CBA01': 5},
}

print("Student tad12aaa: ", kodal['tad12aaa'])
print("Grade for tad12aaa at ABCO: ",kodal['tad12aaa']['ABC01'])

#function to replace the U values with a number
#U means the student has failed a course
def replaceUvalues(dict):
    for key,value in dict.items():
        for key2,value2 in value.items():
            if value2 == 'U':
                dict[key][key2] = 1
    return dict

print()
print("#####")
print("The dictionary with students and marks before replacement")
print(kodal)

new_kodal = replaceUvalues(kodal)
print()
print("#####")
print("The dictionary with students and marks after replacement")
print(new_kodal)

#build a dictionary having the courses and a list with the
#grades for each course
def buildCourseDictionary(new_kodal):
    new_keys = []

    #collect all the courses
    for key,value in new_kodal.items():
        for key2,value2 in value.items():
            #store the courses
            if key2 not in new_keys:
                new_keys.append(key2) 

    grades_dict = {key:[] for key in new_keys}

    for key,value in new_kodal.items():
        for key2,value2 in value.items():
            #store the available grades
            if value2 != '?':
                grades_dict[key2].append(value2)

    return grades_dict

course_dict = buildCourseDictionary(new_kodal)
print()
print("#####")
print("The dictionary only with the courses and grades")
print(course_dict)

#for each course, compute the mean of the available grades
def computeMeanOfCourses(course_dict):
    means_dict = {key:0 for key in course_dict}

    for key,value in course_dict.items():
        mean = sum(value)/len(value)
        means_dict[key] = mean

    return means_dict

means_dict = computeMeanOfCourses(course_dict)
sorted_dict = sorted(means_dict.items(), key = lambda x:x[1], reverse=True)
print()
print("#####")
print("The dictionary with the courses and means")
print(sorted_dict)

list_courses = []
for key,value in sorted_dict:
    list_courses.append(key)

print()
print("#####")
print("The list of the ranked courses based on available means")
print(list_courses)

#function to replace the ? values with 0
def replaceQuestionValues(dict):
    for key,value in dict.items():
        for key2,value2 in value.items():
            if value2 == '?':
                dict[key][key2] = 0
    return dict

new_kodal = replaceQuestionValues(new_kodal)
print()
print("#####")
print("After replacement")
print(new_kodal)

#compute the dot product of two mark vectors from two students
def computeDotProductMarks(student1,student2,dict):
    #store the grades if the students in lists
    list_grades_stud1 = list(dict[student1].values())
    list_grades_stud2 = list(dict[student2].values())
    product_list = [list_grades_stud1[i] * list_grades_stud2[i] for i in range(len(list_grades_stud1))]
    product  = 0
    for i in range(len(product_list)):
        product += product_list[i]
    return product

print()
print("#####")
prod = computeDotProductMarks('tad11ccc','tad12aaa',new_kodal)
print("Dot product for tad11ccc and tad12aaa: ",prod)

import math

#compute the cosine similarity between two mark vectors from two students
def computeCosSimilarity(student1,student2,dict):
    list_grades_stud1 = list(dict[student1].values())
    list_grades_stud2 = list(dict[student2].values())
    dotProduct = computeDotProductMarks(student1,student2,dict)
    sqrt_q = 0.0
    for i in range(len(list_grades_stud1)):
        sqrt_q += list_grades_stud1[i]*list_grades_stud1[i]
    sqrt_q = math.sqrt(sqrt_q)
    sqrt_d = 0.0
    for i in range(len(list_grades_stud2)):
        sqrt_d += list_grades_stud2[i]*list_grades_stud2[i]
    sqrt_d= math.sqrt(sqrt_d)
    cos_sim = dotProduct/(sqrt_q*sqrt_d)
    return cos_sim

print()
print("#####")
sim = computeCosSimilarity('tad11ccc','tad12aaa',new_kodal)
print("Cos similarity for tad11ccc and tad12aaa: ",sim)


#compute the cosine similarity between all the pairs of students
def computeCosSimAll(dict):
    #get all the students
    students = list(dict.keys())
    sim_dict = {}
    #get all the possible combinations
    for s1 in students:
        for s2 in students:
            if s2 != s1:
                key = s1+' & '+s2
                value = computeCosSimilarity(s1,s2,dict)
                sim_dict[key] = value
    return sim_dict

print()
print("#####")
cos_sim_dict = computeCosSimAll(new_kodal)
print("Cos similarity for all students: ",cos_sim_dict)


#find most similar student 
def findMostSimilar(student, dictSim, course, dict):
    dict_sim_stud = {}
    for key in dictSim.keys():
        #find student pairs
        if student in key.split(" & ")[1]:
            #get the similarity score for the pair
            similarity_score = dictSim[key]
            pair_name = key.split(" & ")[0]
            #check if the pair has taken the course
            if dict[pair_name][course] != 0:
                dict_sim_stud[key] = similarity_score
    
    #sort the new dictionary w.r.t. the similarity score
    sorted_disct_sim_stud = sorted(dict_sim_stud.items(), key = lambda x:x[1], reverse=True)
    #save the student with the highest similarity score
    most_similar_student = sorted_disct_sim_stud[0][0].split(" & ")[0]
    #get the grade of the most similar student for the given course
    predicted_grade = dict[most_similar_student][course]
    return most_similar_student, predicted_grade

print("\n")
print("#####")
print("Results based on cos similarity")
student, result = findMostSimilar('tad11ccc', cos_sim_dict,'ABC03',new_kodal)
print("The most similar student to tad11ccc who has taken ABC03 is: ", student)
print("And the predicted result of tad11ccc for ABC03 is: ", result)

print("\n")
print("#####")
print("Results based on cos similarity")
student, result = findMostSimilar('tad11ccc', cos_sim_dict,'ABC02',new_kodal)
print("The most similar student to tad11ccc who has taken ABC02 is: ", student)
print("And the predicted result of tad11ccc for ABC02 is: ", result)