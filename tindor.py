from gurobipy import *
import hashlib


def score(student1, student2):
    if student1 == student2:
        return 0
    return int(hashlib.sha1(student1.encode('utf-8')).hexdigest(), 16) % (10 ** 4) + int(hashlib.sha1(student2.encode('utf-8')).hexdigest(), 16) % (10 ** 4)


def courses(students, course):
    courses_list = []
    for student in students:
        if course[student] not in courses_list:
            courses_list.append(course[student])

    return courses_list


def solve(students, gender, preference, average_grade, course, premium, n_matches, max_same_course, grade_difference):
    model = Model("tindor")

    model.modelSense = GRB.MAXIMIZE

    x = {}
    for student1 in students:
        for student2 in students:
            if student1 != student2:
                x[student1, student2] = model.addVar(name="x#" + student1 + "#" + student2, vtype=GRB.BINARY, obj=score(student1,student2))

    model.update()
    
    for student1 in students:
        other_s=list(students)
        other_s.remove(student1)
    
    
        model.addConstr(quicksum(x[student1,student2] for student2 in other_s)==(2*n_matches if premium[student1]   else n_matches))

    
        for student2 in other_s:
            if gender[student2] not in preference[student1]:
                model.addConstr(x[student1, student2]==0)
  
                
    
        rem_students=list(other_s)
        for c in courses(students,course):
            course_attendants=[]
            for student in list(rem_students):
                if course[student]==c:
                    course_attendants.append(student)
                    rem_students.remove(student)
                    model.addConstr(quicksum( x[student1,attendant]for attendant in course_attendants)<=max_same_course)
        
    
        for student2 in other_s:
            if abs(average_grade[student1]-average_grade[student2])> grade_difference:
                model.addConstr(x[student1,student2]==0)
                
    
        for student2 in other_s:
            model.addConstr(x[student1,student2]==x[student2,student1])
           
                
        
 

    # optimize
    model.optimize()

    # print solution
    if model.status == GRB.OPTIMAL:
        print('\nOptimaler Zielfunktionswert: %g\n' % model.ObjVal)
        for student1 in students:
            for student2 in students:
                if student1 != student2:
                    if x[student1, student2].x > 0.5:
                        print('%s (%g) hat ein Match mit %s (%g)' % (student1, average_grade[student1], student2, average_grade[student2]))
    else:
        print('Keine Optimalloesung gefunden. Status: %i' % (model.status))

    return model
