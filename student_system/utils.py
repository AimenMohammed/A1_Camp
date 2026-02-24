import csv
import os

class DataHandler:
    @staticmethod
    def save_to_csv(filename, students):
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Name', 'Grades'])
            for s in students:
                writer.writerow([s.student_id, s.name, ",".join(map(str, s.grades))])

    @staticmethod
    def load_from_csv(filename):
        students_list = []
        if not os.path.exists(filename): return students_list
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    grades = [float(g) for g in row['Grades'].split(',') if g]
                    students_list.append((row['ID'], row['Name'], grades))
        except: pass
        return students_list

    @classmethod
    def validate_input(cls, grades_str):
        try:
            parts = [g.strip() for g in grades_str.split(',') if g.strip()]
            if not parts:  # تأكد من النقطتين هنا
                return None, "خطأ: القائمة فارغة"
            
            grades = []
            for val in parts:
                num = float(val)
                if num < 0 or num > 100: # تأكد من النقطتين هنا
                    return None, f"خطأ: الدرجة {num} خارج النطاق!"
                grades.append(num)
            return grades, None
        except ValueError:
            return None, "خطأ: أدخل أرقاماً فقط"