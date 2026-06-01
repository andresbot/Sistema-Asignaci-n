from apps.core.models import Teacher, SubjectOffering
print('Teacher fields:', [f.name for f in Teacher._meta.fields])
for t in Teacher.objects.all():
    print('TEACHER:', t.id, str(t))
    offs = SubjectOffering.objects.select_related('subject','subject_group','working_day','time_slot').filter(teacher_id=t.id)
    for o in offs:
        try:
            day = str(o.working_day) if o.working_day else 'None'
        except Exception:
            day = getattr(o.working_day, 'name', 'None') if o.working_day else 'None'
        try:
            times = str(o.time_slot) if o.time_slot else 'None'
        except Exception:
            times = 'None'
        print('  OFFER id=%s label=%s - %s day=%s time=%s' % (o.id, o.subject.code, o.subject_group.identifier, day, times))
