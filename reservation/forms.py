import datetime
from django import forms
from .models import Schedule

REPEAT = (
    (0, 'なし'), (1, '毎日'), (2, '毎週')
)

SPACE_NAME = (
    ('Aスペース', 'Aスペース'), ('Bスペース', 'Bスペース'), ('Cスペース', 'Cスペース'), ('印鑑', '印鑑')
)

PURPOSE = (
    ('ヒアリング', 'ヒアリング'), ('契約', '契約'), ('定例MTG', '定例MTG'), ('鍵渡し', '鍵渡し'),
    ('経営陣MTG', '経営陣MTG'), ('チームMTG', 'チームMTG'), ('トレーニング', 'トレーニング'), ('決済', '決済'),
)

HOURS = [(x, x) for x in range(8, 24)]
MINUTES = [(x, x) for x in range(0, 60, 15)]

YEAR = [(x, x) for x in range(2019, 2030)]
MONTH = [(x, x) for x in range(1, 12)]
DAY = [(x, x) for x in range(1, 31)]


class ScheduleForm(forms.ModelForm):
    """Bootstrapに対応するためのModelForm"""
    start_hour = forms.ChoiceField(
        label='開始',
        choices=HOURS,
    )
    start_minute = forms.ChoiceField(
        label='開始:分',
        choices=MINUTES,
    )
    end_hour = forms.ChoiceField(
        label='終了',
        choices=HOURS,
    )
    end_minute = forms.ChoiceField(
        label='終了:分',
        choices=MINUTES,
    )

    year = forms.ChoiceField(
        label='日付',
        choices=YEAR,
    )
    month = forms.ChoiceField(
        label='月',
        choices=MONTH,
    )
    day = forms.ChoiceField(
        label='日',
        choices=DAY,
    )

    class Meta:
        model = Schedule
        fields = ('space_name', 'purpose', 'description', 'repeat')
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'start_time': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'end_time': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.fields['space_name'] = forms.ChoiceField(
            widget=forms.Select, choices=SPACE_NAME, label='設備')
        self.fields['purpose'] = forms.ChoiceField(
            widget=forms.Select, choices=PURPOSE, label='用途')
        self.fields['repeat'] = forms.ChoiceField(
            widget=forms.Select, choices=REPEAT, label='繰返し')

    def clean(self):
        space = self.cleaned_data['space_name']
        repeat = self.cleaned_data['repeat']
        date = datetime.date(
            int(self.cleaned_data['year']),
            int(self.cleaned_data['month']),
            int(self.cleaned_data['day'])
        )
        start_time_c = datetime.time(
            hour=int(self.cleaned_data['start_hour']),
            minute=int(self.cleaned_data['start_minute'])
        )
        end_time_c = datetime.time(
            hour=int(self.cleaned_data['end_hour']),
            minute=int(self.cleaned_data['end_minute'])
        )
        schedules_a = Schedule.objects.filter(
            space_name='Aスペース', date=date)
        schedules_b = Schedule.objects.filter(
            space_name='Bスペース', date=date)
        schedules_c = Schedule.objects.filter(
            space_name='Cスペース', date=date)
        schedules_i = Schedule.objects.filter(
            space_name='印鑑', date=date)

        if end_time_c <= start_time_c:
            raise forms.ValidationError(
                '終了時間は、開始時間よりも後にしてください'
            )
            return self.cleaned_data

        if space == 'Aスペース':
            for schedule in schedules_a:
                for hour in range(schedule.start_time.hour, schedule.end_time.hour):
                    for minute in range(0, 60, 15):
                        check_time = datetime.time(hour=hour, minute=minute)
                        if start_time_c <= check_time < end_time_c:
                            raise forms.ValidationError(
                                'すでに予定があります'
                            )
            return self.cleaned_data
        if space == 'Bスペース':
            for schedule in schedules_b:
                for hour in range(schedule.start_time.hour, schedule.end_time.hour):
                    for minute in range(0, 60, 15):
                        check_time = datetime.time(hour=hour, minute=minute)
                        if start_time_c <= check_time < end_time_c:
                            raise forms.ValidationError(
                                'すでに予定があります'
                            )
            return self.cleaned_data
        if space == 'Cスペース':
            for schedule in schedules_c:
                for hour in range(schedule.start_time.hour, schedule.end_time.hour):
                    for minute in range(0, 60, 15):
                        check_time = datetime.time(hour=hour, minute=minute)
                        if start_time_c <= check_time < end_time_c:
                            raise forms.ValidationError(
                                'すでに予定があります'
                            )
            return self.cleaned_data
        if space == '印鑑':
            for schedule in schedules_i:
                for hour in range(schedule.start_time.hour, schedule.end_time.hour):
                    for minute in range(0, 60, 15):
                        check_time = datetime.time(hour=hour, minute=minute)
                        if start_time_c <= check_time < end_time_c:
                            raise forms.ValidationError(
                                'すでに予定があります'
                            )
            return self.cleaned_data
