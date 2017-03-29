"""This module can be used to form pairs for students.

David Smith - 2017
"""

import random


def make_better_pairs(num_days, students):
    """Print out some pairs for a given number of days."""
    student_dict = {}

    for student in students:
        temp = dict({})

        for s in students:
            if s != student:
                temp.setdefault(s, 0)

        student_dict[student] = temp

    for day in range(0, num_days):
        used = set()
        students = sorted(students, key=lambda x: sorted(student_dict[x].values())[-1], reverse=True)

        print('')
        print(' - Day', day + 1, '-')
        print('------------')

        for student in students:
            if student not in used:

                try:
                    partner = min([(v, k) for k, v in student_dict[student].items() if k not in used])[1]
                    used.add(student)
                    used.add(partner)
                    student_dict[student][partner] += 1
                    student_dict[partner][student] += 1
                    print(student, '-', partner)

                except ValueError:
                    print('-->', student, 'must be a third.')
    for k in student_dict:
        print(k, student_dict[k])


if __name__ == '__main__':
    STUDENT_LIST = ['Bob', 'Sarah', 'Jules', 'Harold', 'Natasha', 'Veronique', 'Harry', 'John', 'Maggie', 'Wendy', 'Greg', 'Alice', 'Terry', 'Trent']
    make_better_pairs(20, STUDENT_LIST)
