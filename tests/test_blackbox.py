"""Requirements-based cases. Expected values come from REQUIREMENTS.md."""
import json
from copy import deepcopy
from pathlib import Path

import pytest
from registration import (Student, Course, check_credit_limit,
                          prerequisites_satisfied, registration_decision,
                          register_course, withdraw_course)

CASES = json.loads((Path(__file__).parents[1] / 'docs/cases.json').read_text())


def make_objects(values):
    student = Student('S001')
    student.current_credits = values.get('current', 6)
    student.outstanding_dues = values.get('dues', 0)
    student.completed_courses = set(values.get('completed', ['CS101', 'MATH101']))
    student.registered_courses = {'CS201'} if values.get('duplicate', False) else set()
    course = Course('CS201', values.get('credits', 3), values.get('capacity', 2))
    course.enrolled = values.get('enrolled', 1)
    course.prerequisites = {'CS101', 'MATH101'}
    course.waitlist = list(values.get('waitlist', []))
    return student, course


def snapshot(student, course):
    return deepcopy((vars(student), vars(course)))


@pytest.mark.parametrize('case', CASES, ids=[c['id'] for c in CASES])
def test_requirements(case):
    values, expected, kind = case['inputs'], case['expected'], case['kind']
    if kind == 'credit':
        if isinstance(expected, str):
            with pytest.raises(ValueError, match='^' + expected + '$'):
                check_credit_limit(values['current'], values['new'])
        else:
            assert check_credit_limit(values['current'], values['new']) is expected
        return
    if kind == 'prereq':
        assert prerequisites_satisfied(set(values['completed']), set(values['required'])) is expected
        return

    student, course = make_objects(values)
    before = snapshot(student, course)
    operation = {'decision': registration_decision, 'register': register_course,
                 'withdraw': withdraw_course}[kind]
    if isinstance(expected, str) and expected.startswith('Invalid'):
        with pytest.raises(ValueError, match='^' + expected + '$'):
            operation(student, course)
        assert snapshot(student, course) == before
        return
    result = operation(student, course)
    if kind == 'withdraw':
        assert result is expected
    else:
        assert result == expected
    after = deepcopy(before)
    if kind == 'register' and expected == 'REGISTERED':
        after[0]['registered_courses'].add(course.code)
        after[0]['current_credits'] += course.credit_hours
        after[1]['enrolled'] += 1
    elif kind == 'register' and expected == 'WAITLISTED':
        if student.student_id not in after[1]['waitlist']:
            after[1]['waitlist'].append(student.student_id)
    elif kind == 'withdraw' and expected:
        after[0]['registered_courses'].remove(course.code)
        after[0]['current_credits'] -= course.credit_hours
        after[1]['enrolled'] -= 1
    assert snapshot(student, course) == after
