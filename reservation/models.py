import datetime
from django.db import models
from django.utils import timezone


class Schedule(models.Model):
    """スケジュール"""
    user_id = models.IntegerField('ユーザーID')
    space_name = models.CharField('設備名', max_length=20)
    purpose = models.CharField('目的', max_length=255, blank=True)
    description = models.CharField('詳細', max_length=255, blank=True)
    start_time = models.TimeField('開始時間', default=datetime.time(7, 0, 0))
    end_time = models.TimeField('終了時間', default=datetime.time(7, 0, 0))
    date = models.DateField('日付')
    repeat = models.IntegerField('繰り返し', blank=True)
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return self.description
