
"""スケジュールを作成するためのモジュール."""
import datetime


class TimeScheduleBS4:
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
        message = '{}〜{}<br>{}'.format(
            obj.start_time, obj.end_time, obj.description
        )
        return obj.start_time, obj.end_time, message

    def format_hour_name(self, hour):
        """左側の列、時間表示部分の作成."""
        div = '<div style="height:{0}px;" class="hour-name">{1}:00</div>'
        return div.format(self.hour_height, hour)

    # 予定なし時の時間部分
    def format_minute_none(self, now):
        context = {
            'color': self.schedule_color,
            'height': self.minute_height * self.step / 2,
            'just-hour': '',
        }
        if now.minute == 0:
            context['just-hour'] = 'just-hour'
        base_html = (
            '<div class="{just-hour}" style="height:{height}px;"></div>'
        )
        return base_html.format(**context)

    # 予定あり時の時間部分
    def format_minute(self, s, now):
        """分部分の作成."""
        # start, end, text = self.convert(schedule)
        context = {
            'color': self.schedule_color,
            'height': self.minute_height * self.step / 2,
            'just-hour': '',
            # 'text': text,
        }
        # 1:00、2:00などの0分に枠線を入れるためのcss
        if now.minute == 0:
            context['just-hour'] = 'just-hour'

        # 現在ループの時間が開始時間〜終了時間内なら、色をつける
        if now in s:
            base_html = (
                '<div class="{color} {just-hour}" '
                'style="height:{height}px;">'
                '</div>'
            )

        else:
            base_html = (
                '<div class="{just-hour}" style="height:{height}px;"></div>'
            )

        return base_html.format(**context)

     # 左列、時間表示部分の作成
    def format_schedule_time(self, schedules):
        """タイムスケジュールを作成する."""
        v = []
        a = v.append
        a('<div class="col" style="height:{0}px;">'.format(
            self.max_height + 20))
        a('<div style="height:20px;" class="hour-name"></div>')
        for hour in self.hours:
            a(self.format_hour_name(hour))
        a('</div>')

        return ''.join(v)

    # Aスペ、スケジュール作成部分
    def format_schedule_a(self, schedules):
        """タイムスケジュールを作成する."""
        v = []
        a = v.append
        s = []
        sa = s.append
        self.already_tooltip = False
        a('<div class="col minute-wrapper" style="height:{0}px;">'.format(
            self.max_height + 20
        ))
        a('<div style="height:20px; class="hour-name">Aスペース</div>')

        if schedules.count() == 0:
            for hour in self.hours:
                for minute in range(0, 60, self.step):
                    now = datetime.time(hour=hour, minute=minute)
                    a(self.format_minute_none(now))
            a('</div>')
            return ''.join(v)
        else:
            for schedule in schedules:
                if schedule.start_time.hour != schedule.end_time.hour:
                    for hour in range(schedule.start_time.hour, schedule.end_time.hour):
                        for minute in range(0, 60, 15):
                            check_time = datetime.time(
                                hour=hour, minute=minute)
                            sa(check_time)
                    for minute_last in range(0, schedule.end_time.minute, 15):
                        check_time_last = datetime.time(
                            hour=schedule.end_time.hour, minute=minute_last)
                        sa(check_time_last)

                else:
                    for hour in range(schedule.start_time.hour, schedule.end_time.hour + 1):
                        for minute in range(schedule.start_time.minute, schedule.end_time.minute, 15):
                            check_time = datetime.time(
                                hour=hour, minute=minute)
                            sa(check_time)
            for hour in self.hours:
                for minute in range(0, 60, self.step):
                    now = datetime.time(hour=hour, minute=minute)
                    a(self.format_minute(s, now))
            a('</div>')
            return ''.join(v)

    # Bスペ、スケジュール作成部分
    def format_schedule_b(self, schedules):
        """タイムスケジュールを作成する."""
        v = []
        a = v.append
        s = []
        sa = s.append
        self.already_tooltip = False
        a('<div class="col minute-wrapper" style="height:{0}px;">'.format(
            self.max_height + 20
        ))
        a('<div style="height:20px; class="hour-name">Bスペース</div>')

        if schedules.count() == 0:
            for hour in self.hours:
                for minute in range(0, 60, self.step):
                    now = datetime.time(hour=hour, minute=minute)
                    a(self.format_minute_none(now))
            a('</div>')
            return ''.join(v)
        else:
            for schedule in schedules:
                if schedule.start_time.hour != schedule.end_time.hour:
                    for hour in range(schedule.start_time.hour, schedule.end_time.hour):
                        for minute in range(0, 60, 15):
                            check_time = datetime.time(
                                hour=hour, minute=minute)
                            sa(check_time)
                    for minute_last in range(0, schedule.end_time.minute, 15):
                        check_time_last = datetime.time(
                            hour=schedule.end_time.hour, minute=minute_last)
                        sa(check_time_last)

                else:
                    for hour in range(schedule.start_time.hour, schedule.end_time.hour + 1):
                        for minute in range(schedule.start_time.minute, schedule.end_time.minute, 15):
                            check_time = datetime.time(
                                hour=hour, minute=minute)
                            sa(check_time)
            for hour in self.hours:
                for minute in range(0, 60, self.step):
                    now = datetime.time(hour=hour, minute=minute)
                    a(self.format_minute(s, now))
            a('</div>')
            return ''.join(v)

    # Cスペ、スケジュール作成部分
    def format_schedule_c(self, schedules):
        """タイムスケジュールを作成する."""
        v = []
        a = v.append
        s = []
        sa = s.append
        self.already_tooltip = False
        a('<div class="col minute-wrapper" style="height:{0}px;">'.format(
            self.max_height + 20
        ))
        a('<div style="height:20px; class="hour-name">Cスペース</div>')

        if schedules.count() == 0:
            for hour in self.hours:
                for minute in range(0, 60, self.step):
                    now = datetime.time(hour=hour, minute=minute)
                    a(self.format_minute_none(now))
            a('</div>')
            return ''.join(v)
        else:
            for schedule in schedules:
                if schedule.start_time.hour != schedule.end_time.hour:
                    for hour in range(schedule.start_time.hour, schedule.end_time.hour):
                        for minute in range(0, 60, 15):
                            check_time = datetime.time(
                                hour=hour, minute=minute)
                            sa(check_time)
                    for minute_last in range(0, schedule.end_time.minute, 15):
                        check_time_last = datetime.time(
                            hour=schedule.end_time.hour, minute=minute_last)
                        sa(check_time_last)

                else:
                    for hour in range(schedule.start_time.hour, schedule.end_time.hour + 1):
                        for minute in range(schedule.start_time.minute, schedule.end_time.minute, 15):
                            check_time = datetime.time(
                                hour=hour, minute=minute)
                            sa(check_time)
            for hour in self.hours:
                for minute in range(0, 60, self.step):
                    now = datetime.time(hour=hour, minute=minute)
                    a(self.format_minute(s, now))
            a('</div>')
            return ''.join(v)

    # 印鑑、スケジュール作成部分
    def format_schedule_i(self, schedules):
        """タイムスケジュールを作成する."""
        v = []
        a = v.append
        s = []
        sa = s.append
        self.already_tooltip = False
        a('<div class="col minute-wrapper" style="height:{0}px;">'.format(
            self.max_height + 20
        ))
        a('<div style="height:20px; class="hour-name">印鑑</div>')

        if schedules.count() == 0:
            for hour in self.hours:
                for minute in range(0, 60, self.step):
                    now = datetime.time(hour=hour, minute=minute)
                    a(self.format_minute_none(now))
            a('</div>')
            return ''.join(v)
        else:
            for schedule in schedules:
                if schedule.start_time.hour != schedule.end_time.hour:
                    for hour in range(schedule.start_time.hour, schedule.end_time.hour):
                        for minute in range(0, 60, 15):
                            check_time = datetime.time(
                                hour=hour, minute=minute)
                            sa(check_time)
                    for minute_last in range(0, schedule.end_time.minute, 15):
                        check_time_last = datetime.time(
                            hour=schedule.end_time.hour, minute=minute_last)
                        sa(check_time_last)

                else:
                    for hour in range(schedule.start_time.hour, schedule.end_time.hour + 1):
                        for minute in range(schedule.start_time.minute, schedule.end_time.minute, 15):
                            check_time = datetime.time(
                                hour=hour, minute=minute)
                            sa(check_time)
            for hour in self.hours:
                for minute in range(0, 60, self.step):
                    now = datetime.time(hour=hour, minute=minute)
                    a(self.format_minute(s, now))
            a('</div>')
            return ''.join(v)
