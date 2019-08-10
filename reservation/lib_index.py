
"""スケジュールを作成するためのモジュール."""
import datetime
from django.contrib.auth.models import User


class TimeSchedule:
    """タイムスケジュールを作成する(Bootstrap4)."""

    def __init__(
        self, minute_height=1, hours=None, schedule_color='bg-warning', step=15
    ):
        """初期化.
        引数:
        minute_height: 1分の高さ(px)。1ならば1時間が60px、全体で1440px
        hours: スケジュールに記載する時間の幅。range(6, 13)だと6〜12時まで
        schedule_color: スケジュールがある場合の背景色
        step: 何分毎にdivタグを入れるか。デフォルトは1分毎に1divタグ
              1に近いほどdivタグが多くなりパフォーマンスが落ちるが、細かい時間
              でも色をつけることができる
        """
        # hoursがNoneなら0から23時で
        if hours is None:
            self.hours = [x for x in range(8, 24)]
        else:
            self.hours = hours
        self.step = step
        self.minute_height = minute_height
        self.hour_height = self.minute_height * 30
        self.max_height = self.hour_height * len(self.hours)
        self.schedule_color = schedule_color

    def convert(self, obj):
        """(開始時間、終了時間、スケジュールテキスト)のタプルを返す.
        format_schedueメソッドに渡した各scheduleオブジェクトを
        (開始時間, 終了時間,テキスト)の形に変換するためのメソッド
        return obj.start, obj.end, obj.text
        return obj['start'], obj['end'], obj['title']+obj['text']
        のようにしてください
        """
        message = '{}〜{}<br>{}<br>{}'.format(
            str(obj.start_time)[:5], str(obj.end_time)[
                :5], obj.purpose, obj.description
        )
        return message

    # 予定ブロックの作成
    def format_schedule(self, schedule, user):
        """分部分の作成."""
        text = self.convert(schedule)
        context = {
            'color': self.schedule_color,
            'height': self.minute_height * self.step / 2,
            'text': text,
            's_id': schedule.id,
            's_userID': schedule.user_id,
            'url': "/reservation/month/delete/",
        }

        if schedule.user_id == user.id or user.is_superuser:
            base_html = (
                '''<a href="{url}{s_id}">
                <div style="height:70px;border: 1px solid darkgray;border-radius: 1em;margin:4px;font-size:1em;color:black;background-color:skyblue;">
                <p>{text}</p>
                </div></a>'''
            )
        else:
            base_html = (
                '''<div style="height:70px;border: 1px solid darkgray;border-radius: 1em;margin:4px;font-size:1vh;color:black;background-color:silver;">
                <p>{text}</p>
                </div>'''
            )

        return base_html.format(**context)

    # Aスペ、スケジュール作成部分
    def format_schedule_a(self, schedules, user):
        """タイムスケジュールを作成する."""
        v = []
        a = v.append
        self.already_tooltip = False
        a('<div class="col minute-wrapper" style="height:700px;">')
        a('<div style="height:20px;" class="space_css">Aスペース</div>')

        if schedules.count() == 0:
            a('<div></div></div>')
            return ''.join(v)
        else:
            for schedule in schedules:
                a(self.format_schedule(schedule, user))
            a('</div>')
            return ''.join(v)

    # Bスペ、スケジュール作成部分
    def format_schedule_b(self, schedules, user):
        """タイムスケジュールを作成する."""
        v = []
        a = v.append
        self.already_tooltip = False
        a('<div class="col minute-wrapper" style="height:700px;">')
        a('<div style="height:20px;" class="space_css">Bスペース</div>')

        if schedules.count() == 0:
            a('<div></div></div>')
            return ''.join(v)
        else:
            for schedule in schedules:
                a(self.format_schedule(schedule, user))
            a('</div>')
            return ''.join(v)

    # Cスペ、スケジュール作成部分
    def format_schedule_c(self, schedules, user):
        """タイムスケジュールを作成する."""
        v = []
        a = v.append
        self.already_tooltip = False
        a('<div class="col minute-wrapper" style="height:700px;">')
        a('<div style="height:20px;" class="space_css">Cスペース</div>')

        if schedules.count() == 0:
            a('<div></div></div>')
            return ''.join(v)
        else:
            for schedule in schedules:
                a(self.format_schedule(schedule, user))
            a('</div>')
            return ''.join(v)

    # 印鑑、スケジュール作成部分
    def format_schedule_i(self, schedules, user):
        """タイムスケジュールを作成する."""
        v = []
        a = v.append
        self.already_tooltip = False
        a('<div class="col minute-wrapper" style="height:700px;">')
        a('<div style="height:20px;" class="space_css">印鑑</div>')

        if schedules.count() == 0:
            a('<div></div></div>')
            return ''.join(v)
        else:
            for schedule in schedules:
                a(self.format_schedule(schedule, user))
            a('</div>')
            return ''.join(v)
