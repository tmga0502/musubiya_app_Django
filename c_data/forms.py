from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django import forms
from .models import MusubiyaUser, CustomerData, Post

YEAR = (
    (0,'---'),(2019,2019),(2020,2020),(2021,2021),(2022,2022),(2023,2023),(2024,2024),
)

MONTH = (
    (0,'---'),(1,
    1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,11),(12,12),
)

DAY = (
    (0,'---'),(1,
    1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,11),(12,12),(13,13),(14,14),(15,15),(16,16),(17,17),(18,18),(19,19),(20,20),(21,21),(22,22),(23,23),(24,24),(25,25),(26,26),(27,27),(28,28),(29,29),(30,30),(31,31),
)

ACCURACY = (
    ('','---'),('A','A'),('B','B'),('B+','B+'),('C','C')
)

INTRODUCER = (
    ('自己案件','自己案件'),('社内紹介','社内紹介')
)

RANK = ( ('研修','研修'),('ブロンズ','ブロンズ'),('シルバー','シルバー'),('ゴールド','ゴールド'), ('プラチナ','プラチナ') )
PLAN = ( ('自走式','自走式'),('マネジメント','マネジメント') )

INTRODUCTION_TYPE = (
    ('','---'),('直依頼　友人','直依頼　友人'),('直依頼　リピート','直依頼　リピート'),('直依頼　PP','直依頼　PP'),('紹介　友人','紹介　友人'),('紹介　顧客','紹介　顧客'),('紹介　PP','紹介　PP'),('社内紹介','社内紹介')
)

STATUS = (
    ('',''),('申込','申込'),('審査通過','審査通過'),('契約締結','契約締結'),('完了','完了'),('その他','その他')
    )

SEX = (
    (1,'男'),(2,'女')
)

PARTNER = (
    (0,'不明'),(1,'無し'),(2,'恋人'),(3,'既婚')
)

CHILD = (
    (0,'不明'),(1,'いない'),(2,'いる')
)

FLOW = (
    (0,'未'),(1,'OK'),(2,'不要')
)

CHECK = (
    (0,'---'),(1,'OK')
)

# 新規登録フォーム
class CustomerDataForm(forms.ModelForm):
    class Meta:
       model = CustomerData
       fields = ["user_id","introduce_year","introduce_month","apply_year","apply_month","accuracy","introducer","customer_name","introducer_name","introduction_type","reading","brokerage_fee"]

    def __init__(self, *args, **kwargs):
        super(CustomerDataForm, self).__init__(*args, **kwargs)
        self.fields['introduce_year'] = forms.ChoiceField(widget=forms.Select, choices=YEAR)
        self.fields['introduce_month'] = forms.ChoiceField(widget=forms.Select, choices=MONTH)
        self.fields['apply_year'] = forms.ChoiceField(widget=forms.Select, choices=YEAR)
        self.fields['apply_month'] = forms.ChoiceField(widget=forms.Select, choices=MONTH)
        self.fields['accuracy'] = forms.ChoiceField(widget=forms.Select, choices=ACCURACY)
        self.fields['introducer'] = forms.ChoiceField(widget=forms.Select, choices=INTRODUCER)
        self.fields['introducer_name'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '紹介者名'})
        self.fields['introduction_type'] = forms.ChoiceField(widget=forms.Select, choices=INTRODUCTION_TYPE)
        self.fields['customer_name'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'お客様名'})
        self.fields['reading'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ふりがな'})
        self.fields['brokerage_fee'].widget = forms.NumberInput(attrs={
            'class': 'form-control',
            'value': '',
            'placeholder': '売上予定'})

# アカウント情報フォーム
class MusubiyaUserForm(forms.ModelForm):
    class Meta:
        model = MusubiyaUser
        fields = ["musubiya_user_id","user", "rank", "plan", "term", "mandatory_Oct", "mandatory_Nov", "mandatory_Dec", "mandatory_Jan", "mandatory_Feb", "mandatory_Mar", "mandatory_Apr", "mandatory_May", "mandatory_Jun", "mandatory_Jul", "mandatory_Aug", "mandatory_Sep", "stretch_Oct", "stretch_Nov", "stretch_Dec","stretch_Jan", "stretch_Feb", "stretch_Mar", "stretch_Apr","stretch_May", "stretch_Jun", "stretch_Jul", "stretch_Aug", "stretch_Sep"]

    def __init__(self, *args, **kwrgs):
        super(MusubiyaUserForm, self).__init__(*args,**kwrgs)
        self.fields['rank'] = forms.ChoiceField(widget=forms.Select, choices=RANK)
        self.fields['plan'] = forms.ChoiceField(widget=forms.Select, choices=PLAN)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control input-normal"

# 検索フォーム【一覧画面】
class ListSearchForm(forms.Form):
    customer_name = forms.CharField(
        initial='',
        label='お客様名',
        required = False,
    )
    status = forms.ChoiceField(
        initial='',
        label='状況',
        required = False,
        choices=STATUS,
    )
    apply_year = forms.ChoiceField(
        initial='',
        label='申込予定年',
        required = False,
        choices=YEAR,
    )
    apply_month = forms.ChoiceField(
        initial='',
        label='申込予定月',
        required = False,
        choices=MONTH,
    )
    introduce_year = forms.ChoiceField(
        initial='',
        label='紹介年',
        required = False,
        choices=YEAR,
    )
    introduce_month = forms.ChoiceField(
        initial='',
        label='紹介月',
        required = False,
        choices=MONTH,
    )

#検索フォーム【アカウント画面】
class TermSearchForm(forms.Form):
    term = forms.IntegerField(
        initial='',
        label='期',
        required = False,
    )

# 詳細画面用フォーム
class DetailDataForm(forms.ModelForm):
    class Meta:
       model = CustomerData
       fields = '__all__'

    def __init__(self, *args, **kwrgs):
       super(DetailDataForm, self).__init__(*args,**kwrgs)
       self.fields['progress'].widget = forms.Textarea(attrs={'rows':3, 'cols':10})
       self.fields['status'] = forms.ChoiceField(widget=forms.Select, choices=STATUS,required=False)
       self.fields['introduce_year'] = forms.ChoiceField(widget=forms.Select, choices=YEAR,required=False)
       self.fields['introduce_month'] = forms.ChoiceField(widget=forms.Select, choices=MONTH,required=False)
       self.fields['apply_year'] = forms.ChoiceField(widget=forms.Select, choices=YEAR,required=False)
       self.fields['apply_month'] = forms.ChoiceField(widget=forms.Select, choices=MONTH,required=False)
       self.fields['accuracy'] = forms.ChoiceField(widget=forms.Select, choices=ACCURACY,required=False)
       self.fields['introducer'] = forms.ChoiceField(widget=forms.Select, choices=INTRODUCER,required=False)
       self.fields['introduction_type'] = forms.ChoiceField(widget=forms.Select, choices=INTRODUCTION_TYPE,required=False)
       self.fields['bf_payment_schedule_year'] = forms.ChoiceField(widget=forms.Select, choices=YEAR,required=False)
       self.fields['bf_payment_schedule_month'] = forms.ChoiceField(widget=forms.Select, choices=MONTH,required=False)
       self.fields['bf_payment_check'] = forms.ChoiceField(widget=forms.Select, choices=CHECK,required=False)
       self.fields['bf_payment_nen'] = forms.ChoiceField(widget=forms.Select, choices=YEAR,required=False)
       self.fields['bf_payment_month'] = forms.ChoiceField(widget=forms.Select, choices=MONTH,required=False)
       self.fields['bf_payment_day'] = forms.ChoiceField(widget=forms.Select, choices=DAY,required=False)
       self.fields['ad_payment_schedule_year'] = forms.ChoiceField(widget=forms.Select, choices=YEAR,required=False)
       self.fields['ad_payment_schedule_month'] = forms.ChoiceField(widget=forms.Select, choices=MONTH,required=False)
       self.fields['ad_payment_check'] = forms.ChoiceField(widget=forms.Select, choices=CHECK,required=False)
       self.fields['ad_payment_nen'] = forms.ChoiceField(widget=forms.Select, choices=YEAR,required=False)
       self.fields['ad_payment_month'] = forms.ChoiceField(widget=forms.Select, choices=MONTH,required=False)
       self.fields['ad_payment_day'] = forms.ChoiceField(widget=forms.Select, choices=DAY,required=False)
       self.fields['contract_start_year'] = forms.ChoiceField(widget=forms.Select, choices=YEAR,required=False)
       self.fields['contract_start_month'] = forms.ChoiceField(widget=forms.Select, choices=MONTH,required=False)
       self.fields['contract_start_day'] = forms.ChoiceField(widget=forms.Select, choices=DAY,required=False)
       self.fields['contract_end_year'] = forms.ChoiceField(widget=forms.Select, choices=YEAR,required=False)
       self.fields['contract_end_month'] = forms.ChoiceField(widget=forms.Select, choices=MONTH,required=False)
       self.fields['contract_end_day'] = forms.ChoiceField(widget=forms.Select, choices=DAY,required=False)
       self.fields['sex'] = forms.ChoiceField(widget=forms.Select, choices= SEX,required=False)
       self.fields['partner'] = forms.ChoiceField(widget=forms.Select, choices= PARTNER,required=False)
       self.fields['child'] = forms.ChoiceField(widget=forms.Select, choices= CHILD,required=False)
       self.fields['required_documents'] = forms.ChoiceField(widget=forms.Select, choices= FLOW,required=False)
       self.fields['contract_location'] = forms.ChoiceField(widget=forms.Select, choices= FLOW,required=False)
       self.fields['settlement'] = forms.ChoiceField(widget=forms.Select, choices= FLOW,required=False)
       self.fields['life_line'] = forms.ChoiceField(widget=forms.Select, choices= FLOW,required=False)
       self.fields['confirmation'] = forms.ChoiceField(widget=forms.Select, choices= FLOW,required=False)
       self.fields['guarantor'] = forms.ChoiceField(widget=forms.Select, choices= FLOW,required=False)
       self.fields['hand_ovre_kye'] = forms.ChoiceField(widget=forms.Select, choices= FLOW,required=False)
       self.fields['contract_procedures'] = forms.ChoiceField(widget=forms.Select, choices= FLOW,required=False)
       self.fields['ADs_invoice'] = forms.ChoiceField(widget=forms.Select, choices= FLOW,required=False)


       for field in self.fields.values():
               field.widget.attrs["class"] = "form-control input-normal"

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('user_id', 'message',)

    def __init__(self, *args, **kwrgs):
       super(PostForm, self).__init__(*args,**kwrgs)
       self.fields['message'] = forms.CharField(widget=forms.TextInput(
       attrs={'placeholder':'New Todo'}))
       for field in self.fields.values():
            field.widget.attrs["class"] = "form-control input-normal "
