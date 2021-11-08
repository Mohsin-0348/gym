
import django_filters

from bases.filters import BaseFilters
from hr.models import Employee


class EmployeeFilters(BaseFilters):
    """Employee Filter will define here"""
    designation = django_filters.CharFilter(
        field_name='designation',
        lookup_expr='exact'
    )

    class Meta:
        model = Employee
        fields = [
            'id',
            'designation',
        ]
