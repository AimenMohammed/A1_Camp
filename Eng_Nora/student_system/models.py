class Student:
    def __init__(self, student_id, name, grades):
        self.__student_id = student_id
        self.name = name
        self.grades = grades

    @property
    def student_id(self):
        return self.__student_id

    def calculate_average(self):
        # منع خطأ القسمة على صفر إذا كانت القائمة فارغة
        if not self.grades:
            return 0.0
        return sum(self.grades) / len(self.grades)

    def get_category(self):
        avg = self.calculate_average()
        if avg >= 90: return "امتياز"
        if avg >= 80: return "جيد جداً"
        if avg >= 70: return "جيد"
        if avg >= 50: return "مقبول"
        return "راسب"

class Classroom:
    def __init__(self):
        self.students = []

    def add_student(self, student):
        self.students.append(student)

    def remove_student(self, student_id):
        self.students = [s for s in self.students if s.student_id != student_id]

    def find_student(self, student_id):
        for s in self.students:
            if s.student_id == student_id:
                return s
        return None

    def get_class_average(self):
        if not self.students:
            return 0.0
        total = sum(s.calculate_average() for s in self.students)
        return total / len(self.students)

        
        
        
        
        
        
        
    # def Name(self, name):
    #     self.name= name
    #     return(name)
    
    # def Student_Id(self, student_id):
    #     self.student_id = student_id
    #     return(student_id)
        
    # def Grades(self, grades):
    #     self.grades = grades
    #     return("hi")
    #     # for i in grades :
    #     #     pass
    #     # return(grades)
        
        
    # def Average(self,grades):
    #     self.grades=grades
    #     count=len(grades)
    #     for i in grades:
    #         full_marks += grades
        
    #     full_average= full_marks/count
    #     return full_average
    
    # def Grade_Category(average):
    #     if average <0 :
    #         print("المعدل لا يمكن ان يساوي أقل من الصفر")
            
    #     elif average > 0 and average < 50 :
    #         print("راسب")
            
    #     elif average >=50 and average < 65 :
    #         print("مقبول")
            
    #     elif average >=65 and average < 75 :
    #         print("جيد")
            
    #     elif average >=75 and average < 90 :
    #         print("جيد جدا")
            
    #     elif average >=90 and average <= 100 :
    #         print("ممتاز") 
        
    #     else :
    #         print("المعدل لا يمكن ان يكون اكثر من 100")  
            
        