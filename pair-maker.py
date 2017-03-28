"""This module can be used to form pairs for students.

David Smith - 2017
"""

import random


def make_better_pairs(num_days, students):
    """Print out some pairs."""
    student_dict = {}

    for student in students:
        temp = dict({})
        for s in students:
            if s != student:
                temp.setdefault(s, 0)
        student_dict[student] = temp

    for day in range(0, num_days):
        used = set()
        random.shuffle(students)

        print('')
        print('Day', day + 1)
        print('-------')

        for student in students:
            if student not in used:

                try:
                    pair = min([(v, k) for k, v in student_dict[student].items() if k not in used])[1]
                    used.add(student)
                    used.add(pair)
                    student_dict[student][pair] += 1
                    student_dict[pair][student] += 1
                    print(student, '-', pair)

                except ValueError:
                    print('-->', student, 'must be a third')


if __name__ == '__main__':
    STUDENT_LIST = ['Bob', 'Sarah', 'Jules', 'Harold', 'Natasha', 'Veronique', 'Harry', 'John', 'Maggie', 'Wendy', 'Greg', 'Alice', 'Terry', 'Trent']
    make_better_pairs(20, STUDENT_LIST)
