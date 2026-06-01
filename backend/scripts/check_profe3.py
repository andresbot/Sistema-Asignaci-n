from django.db.models import Q
from apps.core.models import SubjectOffering
qs = SubjectOffering.objects.select_related('subject','subject_group','working_day','time_slot','teacher').filter(Q(teacher__name__icontains='Profe 3')|Q(teacher__full_name__icontains='Profe 3')|Q(teacher__first_name__icontains='Profe 3')|Q(teacher__last_name__icontains='Profe 3'))
print('count', qs.count())
for o in qs:
    t = getattr(o.teacher, 'full_name', None) or getattr(o.teacher, 'name', None) or str(o.teacher)
    print(f'id={o.id} label={o.subject.code} - {o.subject_group.identifier} teacher="{t}" day="{o.working_day.name}" time="{o.time_slot.label}"')
