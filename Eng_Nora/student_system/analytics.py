def get_top_student(classroom):
    if not classroom.students: return None
    return max(classroom.students, key=lambda s: s.calculate_average())

def get_lowest_student(classroom):
    if not classroom.students: return None
    return min(classroom.students, key=lambda s: s.calculate_average())

def get_ranking(classroom):
    return sorted(classroom.students, key=lambda s: s.calculate_average(), reverse=True)

def get_grade_distribution(classroom):
    dist = {"امتياز": 0, "جيد جداً": 0, "جيد": 0, "مقبول": 0, "راسب": 0}
    for s in classroom.students:
        category = s.get_category()
        dist[category] += 1
    return dist
