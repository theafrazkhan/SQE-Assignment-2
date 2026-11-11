"""Additional structural tests; expected behavior still comes from the SRS."""
from copy import deepcopy

import pytest
import registration as reg


def objects():
    return reg.Student('S001', current_credits=6), reg.Course('CS201', 3, 2, enrolled=1)


def test_W01_large_dues_branch():
    """Exercise original line 50 -> 51, missed by the black-box inventory."""
    student, course = objects()
    student.outstanding_dues = 1001
    before = deepcopy((student, course))
    assert reg.registration_decision(student, course) == 'DUES_BLOCK'
    assert (student, course) == before


@pytest.mark.parametrize('current,credits,message', [
    (-1, 3, 'Invalid current credits'),
    (6, 0, 'Invalid course credits'),
], ids=['W02-current-exception', 'W03-course-exception'])
def test_credit_exception_propagation(current, credits, message):
    """Reach the credit helper through the decision path and preserve state."""
    student, course = objects()
    student.current_credits, course.credit_hours = current, credits
    before = deepcopy((student, course))
    with pytest.raises(ValueError, match='^' + message + '$'):
        reg.registration_decision(student, course)
    assert (student, course) == before


@pytest.mark.parametrize('status,existing,expected', [
    ('WAITLISTED', [], ['S001']),
    ('WAITLISTED', ['S001'], ['S001']),
    ('DUES_BLOCK', [], []),
], ids=['W04-waitlist-add', 'W05-waitlist-existing', 'W06-non-waitlist'])
def test_waitlist_application_in_isolation(monkeypatch, status, existing, expected):
    """Original waitlist decision is infeasible: stub only its result.

    This tests register_course's real AND decision, including short-circuiting.
    It does not claim end-to-end reachability of WAITLISTED in the starter.
    """
    student, course = objects()
    course.waitlist = list(existing)
    before = deepcopy((vars(student), vars(course)))
    monkeypatch.setattr(reg, 'registration_decision', lambda s, c: status)
    assert reg.register_course(student, course) == status
    before[1]['waitlist'] = expected
    assert (vars(student), vars(course)) == before


@pytest.mark.parametrize('enrolled,capacity,invalid', [
    (0, 1, False),  # A=T, B=T, C=F -> valid
    (-1, 1, True),  # A=F, B=NE, C=NE -> invalid
    (2, 1, True),  # A=T, B=F, C=NE -> invalid
    (0, 0, True),  # A=T, B=T, C=T -> invalid
], ids=['W07-valid', 'W08-negative-enrollment', 'W09-above-capacity', 'W10-zero-capacity'])
def test_validation_conditions(enrolled, capacity, invalid):
    """Atomic validation conditions and masking MC/DC pairs for line 48."""
    student, course = objects()
    course.enrolled, course.capacity = enrolled, capacity
    before = deepcopy((student, course))
    if invalid:
        with pytest.raises(ValueError, match='^Invalid capacity or enrollment$'):
            reg.registration_decision(student, course)
    else:
        assert reg.registration_decision(student, course) == 'REGISTERED'
    assert (student, course) == before
