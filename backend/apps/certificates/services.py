from .models import Certificate


def issue_certificate_if_eligible(submission):
    if submission.score < submission.exam.excellent_score:
        return None
    return Certificate.objects.get_or_create(
        student=submission.student,
        course=submission.exam.course,
        defaults={"exam_submission": submission},
    )[0]
