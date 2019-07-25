from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views import generic
from . import mixins
from .forms import ScheduleForm
from .models import Schedule
from .lib import TimeScheduleBS4
from .lib_index import TimeSchedule
from django.utils.safestring import mark_safe
import datetime
import calendar
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
# Create your views here.


class Index(mixins.MonthCalendarMixin, generic.TemplateView):
    template_name = 'reservation/index.html'
    model = Schedule
    date_field = 'date'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.user
        calendar_context = self.get_month_calendar()
        context.update(calendar_context)
        schedules_a = Schedule.objects.filter(
            space_name='Aスペース', date=context['month_current']).order_by('start_time')
        schedules_b = Schedule.objects.filter(
            space_name='Bスペース', date=context['month_current']).order_by('start_time')
        schedules_c = Schedule.objects.filter(
            space_name='Cスペース', date=context['month_current']).order_by('start_time')
        schedules_i = Schedule.objects.filter(
            space_name='印鑑', date=context['month_current']).order_by('start_time')
        time_schedule = TimeSchedule(step=15, minute_height=1)
        context['time_schedule_a'] = mark_safe(
            time_schedule.format_schedule_a(schedules_a, context['user_id'])
        )
        context['time_schedule_b'] = mark_safe(
            time_schedule.format_schedule_b(schedules_b, context['user_id'])
        )
        context['time_schedule_c'] = mark_safe(
            time_schedule.format_schedule_c(schedules_c, context['user_id'])
        )
        context['time_schedule_i'] = mark_safe(
            time_schedule.format_schedule_i(schedules_i, context['user_id'])
        )

        return context


class MonthCalendar(mixins.MonthCalendarMixin, generic.CreateView):
    """月間カレンダーを表示するビュー"""
    template_name = 'reservation/create.html'
    model = Schedule
    date_field = 'date'
    form_class = ScheduleForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()
        context.update(calendar_context)
        schedules_a = Schedule.objects.filter(
            space_name='Aスペース', date=context['month_current']).order_by('start_time')
        schedules_b = Schedule.objects.filter(
            space_name='Bスペース', date=context['month_current']).order_by('start_time')
        schedules_c = Schedule.objects.filter(
            space_name='Cスペース', date=context['month_current']).order_by('start_time')
        schedules_i = Schedule.objects.filter(
            space_name='印鑑', date=context['month_current']).order_by('start_time')
        time_schedule = TimeScheduleBS4(step=15, minute_height=1)
        context['time_schedule_time'] = mark_safe(
            time_schedule.format_schedule_time(schedules_a)
        )
        context['time_schedule_a'] = mark_safe(
            time_schedule.format_schedule_a(schedules_a)
        )
        context['time_schedule_b'] = mark_safe(
            time_schedule.format_schedule_b(schedules_b)
        )
        context['time_schedule_c'] = mark_safe(
            time_schedule.format_schedule_c(schedules_c)
        )
        context['time_schedule_i'] = mark_safe(
            time_schedule.format_schedule_i(schedules_i)
        )
        return context

    def form_valid(self, form):
        today = datetime.date(
            int(self.request.POST['year']),
            int(self.request.POST['month']),
            int(self.request.POST['day'])
        )
        after_one_year = today + relativedelta(months=12)
        day_count = after_one_year-today
        if self.request.POST['repeat'] == '1':
            posts = []
            _, lastday = calendar.monthrange(
                int(self.request.POST['year']), int(self.request.POST['month']))
            for i in range(lastday - int(self.request.POST['day'])+1):
                post = Schedule(
                    user_id=self.request.POST['user_id'],
                    space_name=self.request.POST['space_name'],
                    purpose=self.request.POST['purpose'],
                    description=self.request.POST['description'],
                    start_time=datetime.time(
                        int(self.request.POST['start_hour']),
                        int(self.request.POST['start_minute'])
                    ),
                    end_time=datetime.time(
                        int(self.request.POST['end_hour']),
                        int(self.request.POST['end_minute'])
                    ),
                    date=datetime.date(
                        int(self.request.POST['year']),
                        int(self.request.POST['month']),
                        int(self.request.POST['day'])
                    ) + timedelta(days=i),
                    repeat=1,
                )
                posts.append(post)
            Schedule.objects.bulk_create(posts)
            return redirect('reservation:index')
        elif self.request.POST['repeat'] == '2':
            posts = []
            for i in range(0, day_count.days, 7):
                post = Schedule(
                    user_id=self.request.POST['user_id'],
                    space_name=self.request.POST['space_name'],
                    purpose=self.request.POST['purpose'],
                    description=self.request.POST['description'],
                    start_time=datetime.time(
                        int(self.request.POST['start_hour']),
                        int(self.request.POST['start_minute'])
                    ),
                    end_time=datetime.time(
                        int(self.request.POST['end_hour']),
                        int(self.request.POST['end_minute'])
                    ),
                    date=datetime.date(
                        int(self.request.POST['year']),
                        int(self.request.POST['month']),
                        int(self.request.POST['day'])
                    ) + timedelta(days=i),
                    repeat=2,
                )
                posts.append(post)
            Schedule.objects.bulk_create(posts)
            return redirect('reservation:index')
        else:
            date = datetime.date(
                int(form.cleaned_data['year']),
                int(form.cleaned_data['month']),
                int(form.cleaned_data['day'])
            )
            schedule = form.save(commit=False)
            schedule.date = date
            schedule.user_id = self.request.user.id
            schedule.start_time = datetime.time(
                int(form.cleaned_data['start_hour']),
                int(form.cleaned_data['start_minute'])
            )
            schedule.end_time = datetime.time(
                int(form.cleaned_data['end_hour']),
                int(form.cleaned_data['end_minute'])
            )
            schedule.save()
            return redirect('reservation:index', year=date.year, month=date.month, day=date.day)


class ScheduleUpdateView(generic.UpdateView):
    model = Schedule
    form_class = ScheduleForm
    ate_field = 'date'
    template_name = 'reservation/update.html'
    success_url = 'reservation/index.html'

    def get_context_data(self, **kwargs):
        queryset = Schedule.objects.get(id=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['form'] = ScheduleForm(initial={
            'space_name': queryset.space_name,
            'purpose': queryset.purpose,
            'description': queryset.description,
            'year': queryset.date.year,
            'month': queryset.date.month,
            'day': queryset.date.day,
            'start_hour': queryset.start_time.hour,
            'start_minute': queryset.start_time.minute,
            'end_hour': queryset.end_time.hour,
            'end_minute': queryset.end_time.minute,
            'repeat': queryset.repeat,
        })
        return context

    def form_valid(self, form):
        date = datetime.date(
            int(form.cleaned_data['year']),
            int(form.cleaned_data['month']),
            int(form.cleaned_data['day'])
        )
        schedule = form.save(commit=False)
        schedule.date = date
        schedule.user_id = self.request.user.id
        schedule.start_time = datetime.time(
            int(form.cleaned_data['start_hour']),
            int(form.cleaned_data['start_minute'])
        )
        schedule.end_time = datetime.time(
            int(form.cleaned_data['end_hour']),
            int(form.cleaned_data['end_minute'])
        )
        schedule.save()
        return redirect('reservation:index', year=date.year, month=date.month, day=date.day)


class ScheduleDeleteView(generic.DeleteView):
    model = Schedule
    template_name = 'reservation/delete.html'
    success_url = '/reservation/month'

    def get_context_data(self, **kwargs):
        queryset = Schedule.objects.get(id=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['space_name'] = queryset.space_name
        context['purpose'] = queryset.purpose
        context['description'] = queryset.description
        context['year'] = queryset.date.year
        context['month'] = queryset.date.month
        context['day'] = queryset.date.day
        context['start_hour'] = queryset.start_time.hour
        context['start_minute'] = queryset.start_time.minute
        context['end_hour'] = queryset.end_time.hour
        context['end_minute'] = queryset.end_time.minute
        context['repeat'] = queryset.repeat
        return context
