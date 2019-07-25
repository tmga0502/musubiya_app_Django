from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import CustomerData, MusubiyaUser, Post
from .forms import CustomerDataForm, MusubiyaUserForm,  ListSearchForm, DetailDataForm, PostForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.contrib import messages
import math, collections, datetime, itertools
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
from . import use_selenium

now_term = 9 #決算期が変わったら変えること


# Create your views here.

# ページネーション用
def paginate_queryset(request, queryset, count):
    paginator = Paginator(queryset, count)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj

def index(request):
    return redirect('accounts:login')

# トップ画面【完了】
@login_required
def user_detail(request, pk):
    this_year = datetime.date.today().year
    this_month = datetime.date.today().month
    prospect = CustomerData.objects.filter(user_id=request.user.id)  #見込み客obj
    # 今月売上目標
    mandatory_list = {10:'mandatory_Oct', 11:'mandatory_Nov', 12:'mandatory_Dec', 1:'mandatory_Jan', 2:'mandatory_Feb', 3:'mandatory_Mar', 4:'mandatory_Apr', 5:'mandatory_May', 6:'mandatory_Jun', 7:'mandatory_Jul', 8:'mandatory_Aug', 9:'mandatory_Sep'}
    stretch_list = {10:'stretch_Oct', 11:'stretch_Nov', 12:'stretch_Dec', 1:'stretch_Jan', 2:'stretch_Feb', 3:'stretch_Mar', 4:'stretch_Apr', 5:'stretch_May', 6:'stretch_Jun', 7:'stretch_Jul', 8:'stretch_Aug', 9:'stretch_Sep'}
    md = mandatory_list[this_month]
    sd = stretch_list[this_month]
    if MusubiyaUser.objects.filter(musubiya_user_id=request.user.id, term=now_term).exists():
        mandatory_goal = MusubiyaUser.objects.values_list(md, flat=True).get(musubiya_user_id=request.user.id, term=now_term)
        stretch_goal = MusubiyaUser.objects.values_list(sd, flat=True).get(musubiya_user_id=request.user.id, term=now_term)
    else:
        mandatory_goal = 0
        stretch_goal = 0
    # 必達達成率計算
    mandatory_now_list = []
    mandatory_now_bf = prospect.filter(bf_payment_nen=this_year,bf_payment_month=this_month)
    mandatory_now_ad = prospect.filter(ad_payment_nen=this_year, ad_payment_month=this_month)
    for mnbf in mandatory_now_bf:
        mandatory_now_list.append(mnbf.bf_payment_amount)
    for mnad in mandatory_now_ad:
        mandatory_now_list.append(mnad.ad_payment_amount)
    mnl = sum(mandatory_now_list)
    if mandatory_goal == 0:
        mat = 0  #mandatory_achievement_rate
    else:
        mat = mnl / mandatory_goal *100   #mandatory_achievement_rate

    # ストレッチ達成率計算
    stretch_now_list = []
    stretch_now_bf = prospect.filter(bf_payment_nen=this_year,bf_payment_month=this_month)
    stretch_now_ad = prospect.filter(ad_payment_nen=this_year, ad_payment_month=this_month)
    for stbf in stretch_now_bf:
        stretch_now_list.append(stbf.bf_payment_amount)
    for stad in stretch_now_ad:
        stretch_now_list.append(stad.ad_payment_amount)
    stl = sum(stretch_now_list)
    if stretch_goal == 0:
        sat = 0  #stretch_achievement_rate
    else:
        sat = stl / stretch_goal *100   #stretch_achievement_rate

    # Todoリスト
    posts = Post.objects.filter(user_id=request.user.id)
    form = PostForm()
    if 'new' in request.POST:
        form = PostForm()
        obj = Post()
        post = PostForm(request.POST, instance=obj)
        post.save()
        return redirect('c_data:user_detail', pk=request.user.id)
    if 'del' in request.POST:
        post = Post.objects.get(id=request.POST['del'])
        post.delete()
        return redirect('c_data:user_detail', pk=request.user.id)

    # 解約３ヶ月前取得
    list_3_key = []
    list_3_value = []
    for pro in prospect:
        threeMonthAgo_m = pro.contract_end_month - 3
        threeMonthAgo_y = pro.contract_end_year
        if threeMonthAgo_m <=3:
            threeMonthAgo_m = pro.contract_end_month + 12 - 3
            threeMonthAgo_y = pro.contract_end_year - 1
        if threeMonthAgo_m == this_month and threeMonthAgo_y == this_year:
            list_3_key.append(pro.id)
            list_3_value.append(pro.customer_name)
    l = dict(zip(list_3_key,list_3_value))

    # 誕生日検索
    prospect_bd = prospect.filter(birthday__month=(this_month))
    prospect_pbd = prospect.filter(partner_birthday__month=(this_month))
    prospect_c1bd = prospect.filter(child1_birthday__month=(this_month))
    prospect_c2bd = prospect.filter(child2_birthday__month=(this_month))


    login_user = request.user
    if pk == login_user.id:
        user = User.objects.get(pk=pk)
        context = {
            'user': user,
            'this_year': this_year,
            'this_month': this_month,
            'mandatory_goal': mandatory_goal,
            'mat': mat,
            'stretch_goal': stretch_goal,
            'sat': sat,
            'posts': posts,
            'form': form,
            'l': l,
            'prospect_bd':prospect_bd,
            'prospect_pbd':prospect_pbd,
            'prospect_c1bd':prospect_c1bd,
            'prospect_c2bd':prospect_c2bd,
        }
        return render(request, 'c_data/users_detail.html', context)
    else:
        return redirect('accounts:logout')

# プロフィール画面【完了】
@login_required
def profile(request, pk):
    if request.method == 'GET':
        login_user = request.user
        # フォームに初期値を流し込む
        if 'term' in request.session:
            term_name = request.session['term']
            u_data = MusubiyaUser.objects.get(musubiya_user_id=request.user.id, term=term_name[0])
            form = MusubiyaUserForm(initial={
                "rank":u_data.rank,
                "plan":u_data.plan,
                'term':u_data.term,
                "mandatory_Oct":u_data.mandatory_Oct,
                "mandatory_Nov":u_data.mandatory_Nov,
                "mandatory_Dec":u_data.mandatory_Dec,
                "mandatory_Jan":u_data.mandatory_Jan,
                "mandatory_Feb":u_data.mandatory_Feb,
                "mandatory_Mar":u_data.mandatory_Mar,
                "mandatory_Apr":u_data.mandatory_Apr,
                "mandatory_May":u_data.mandatory_May,
                "mandatory_Jun":u_data.mandatory_Jun,
                "mandatory_Jul":u_data.mandatory_Jul,
                "mandatory_Aug":u_data.mandatory_Aug,
                "mandatory_Sep":u_data.mandatory_Sep,
                "stretch_Oct":u_data.stretch_Oct,
                "stretch_Nov":u_data.stretch_Nov,
                "stretch_Dec":u_data.stretch_Dec,
                "stretch_Jan":u_data.stretch_Jan,
                "stretch_Feb":u_data.stretch_Feb,
                "stretch_Mar":u_data.stretch_Mar,
                "stretch_Apr":u_data.stretch_Apr,
                "stretch_May":u_data.stretch_May,
                "stretch_Jun":u_data.stretch_Jun,
                "stretch_Jul":u_data.stretch_Jul,
                "stretch_Aug":u_data.stretch_Aug,
                "stretch_Sep":u_data.stretch_Sep
            })
            # 合計の計算
            mandatory_sum = u_data.mandatory_Oct + u_data.mandatory_Nov + u_data.mandatory_Dec + u_data.mandatory_Jan + u_data.mandatory_Feb + u_data.mandatory_Mar + u_data.mandatory_Apr + u_data.mandatory_May + u_data.mandatory_Jun + u_data.mandatory_Jul + u_data.mandatory_Aug + u_data.mandatory_Sep
            stretch_sum = u_data.stretch_Oct + u_data.stretch_Nov + u_data.stretch_Dec + u_data.stretch_Jan + u_data.stretch_Feb + u_data.stretch_Mar + u_data.stretch_Apr + u_data.stretch_May + u_data.stretch_Jun + u_data.stretch_Jul + u_data.stretch_Aug + u_data.stretch_Sep
        elif MusubiyaUser.objects.filter(musubiya_user_id=request.user.id).exists():
            u_data = MusubiyaUser.objects.get(musubiya_user_id=request.user.id, term=now_term)
            form = MusubiyaUserForm(initial={
                "rank":u_data.rank,
                "plan":u_data.plan,
                'term':u_data.term,
                "mandatory_Oct":u_data.mandatory_Oct,
                "mandatory_Nov":u_data.mandatory_Nov,
                "mandatory_Dec":u_data.mandatory_Dec,
                "mandatory_Jan":u_data.mandatory_Jan,
                "mandatory_Feb":u_data.mandatory_Feb,
                "mandatory_Mar":u_data.mandatory_Mar,
                "mandatory_Apr":u_data.mandatory_Apr,
                "mandatory_May":u_data.mandatory_May,
                "mandatory_Jun":u_data.mandatory_Jun,
                "mandatory_Jul":u_data.mandatory_Jul,
                "mandatory_Aug":u_data.mandatory_Aug,
                "mandatory_Sep":u_data.mandatory_Sep,
                "stretch_Oct":u_data.stretch_Oct,
                "stretch_Nov":u_data.stretch_Nov,
                "stretch_Dec":u_data.stretch_Dec,
                "stretch_Jan":u_data.stretch_Jan,
                "stretch_Feb":u_data.stretch_Feb,
                "stretch_Mar":u_data.stretch_Mar,
                "stretch_Apr":u_data.stretch_Apr,
                "stretch_May":u_data.stretch_May,
                "stretch_Jun":u_data.stretch_Jun,
                "stretch_Jul":u_data.stretch_Jul,
                "stretch_Aug":u_data.stretch_Aug,
                "stretch_Sep":u_data.stretch_Sep
            })
            # 合計の計算
            mandatory_sum = u_data.mandatory_Oct + u_data.mandatory_Nov + u_data.mandatory_Dec + u_data.mandatory_Jan + u_data.mandatory_Feb + u_data.mandatory_Mar + u_data.mandatory_Apr + u_data.mandatory_May + u_data.mandatory_Jun + u_data.mandatory_Jul + u_data.mandatory_Aug + u_data.mandatory_Sep
            stretch_sum = u_data.stretch_Oct + u_data.stretch_Nov + u_data.stretch_Dec + u_data.stretch_Jan + u_data.stretch_Feb + u_data.stretch_Mar + u_data.stretch_Apr + u_data.stretch_May + u_data.stretch_Jun + u_data.stretch_Jul + u_data.stretch_Aug + u_data.stretch_Sep
        else:
            u_data = 'Nun'
            form = MusubiyaUserForm(initial={'customer_name':request.user.id, 'term':now_term})
            mandatory_sum = ''
            stretch_sum = ''
        if pk == login_user.id:
           user = User.objects.get(pk=pk)
           return render(request, 'c_data/profile.html', {'form': form, 'u_data':u_data, 'mandatory_sum': mandatory_sum, 'stretch_sum': stretch_sum})
        else:
           return redirect('accounts:logout')

    if request.method == 'POST':
        # 更新or作成
        if 'update' in request.POST:
            check_term = request.POST["term"]
            check_user_id = request.POST["musubiya_user_id"]
            MusubiyaUser.objects.update_or_create(
                musubiya_user_id = check_user_id,
                term = check_term,
                defaults = {
                    "musubiya_user_id":request.POST["musubiya_user_id"],
                    "user":request.POST["user"], "rank":request.POST["rank"],
                    "plan":request.POST["plan"], "term":request.POST["term"],
                    "mandatory_Oct":request.POST["mandatory_Oct"],
                    "mandatory_Nov":request.POST["mandatory_Nov"],
                    "mandatory_Dec":request.POST["mandatory_Dec"],
                    "mandatory_Jan":request.POST["mandatory_Jan"],
                    "mandatory_Feb":request.POST["mandatory_Feb"],
                    "mandatory_Mar":request.POST["mandatory_Mar"],
                    "mandatory_Apr":request.POST["mandatory_Apr"],
                    "mandatory_May":request.POST["mandatory_May"],
                    "mandatory_Jun":request.POST["mandatory_Jun"],
                    "mandatory_Jul":request.POST["mandatory_Jul"],
                    "mandatory_Aug":request.POST["mandatory_Aug"],
                    "mandatory_Sep":request.POST["mandatory_Sep"],
                    "stretch_Oct":request.POST["stretch_Oct"],
                    "stretch_Nov":request.POST["stretch_Nov"],
                    "stretch_Dec":request.POST["stretch_Dec"],
                    "stretch_Jan":request.POST["stretch_Jan"],
                    "stretch_Feb":request.POST["stretch_Feb"],
                    "stretch_Mar":request.POST["stretch_Mar"],
                    "stretch_Apr":request.POST["stretch_Apr"],
                    "stretch_May":request.POST["stretch_May"],
                    "stretch_Jun":request.POST["stretch_Jun"],
                    "stretch_Jul":request.POST["stretch_Jul"],
                    "stretch_Aug":request.POST["stretch_Aug"],
                    "stretch_Sep":request.POST["stretch_Sep"]
                },
            )
            return redirect('c_data:profile', pk=request.user.id)
        # 検索
        if 'search' in request.POST:
            # フォームの値を受け取る
            term = request.POST["term"]
            term_data = MusubiyaUser.objects.filter(musubiya_user_id=request.user.id, term=term)
            if term_data.exists():
                request.session['term'] = [term]  #セッションに入れる
            return redirect('c_data:profile', pk=request.user.id)
        # クリアボタン
        if 'clear' in request.POST:
            if 'term' in request.session:
                del request.session['term']
            return redirect('c_data:profile', pk=request.user.id)

# 一覧画面【完了】
@login_required
def list(request, pk):
    form = ListSearchForm()
    c_data = CustomerData.objects.filter(user_id=request.user.id).order_by('id').reverse()
    login_user = request.user
    if pk == login_user.id:
        if request.method=='POST':
            # フォームの値を受け取る
            customer_name = request.POST["customer_name"]
            apply_year = request.POST["apply_year"]
            apply_month = request.POST["apply_month"]
            # お客様名検索
            if 'c_name' in request.POST:
                c_data = CustomerData.objects.filter(user_id=login_user.id, customer_name=customer_name).order_by('id').reverse()
                request.session['c_name'] = [customer_name]  #セッションに入れる
                if'apply' in request.session:
                    del request.session['apply']    #申込セッションがあれば消す
            # 申込予定検索
            if 'apply' in request.POST:
                c_data = CustomerData.objects.filter(user_id=login_user.id, apply_year=apply_year, apply_month=apply_month).order_by('id').reverse()
                request.session['apply'] = [apply_year, apply_month]    #セッションに入れる
                if 'c_name' in request.session:
                    del request.session['c_name']   #お客様名セッションがあれば消す
            #クリアボタン処理
            if 'clear' in request.POST:
                if 'c_name' in request.session:
                    del request.session['c_name']   #お客様名セッションがあれば消す
                if'apply' in request.session:
                    del request.session['apply']    #申込セッションがあれば消す

        # 顧客セッションがあればそこから検索
        if 'c_name' in request.session:
            c_name = request.session['c_name']
            c_data = CustomerData.objects.filter(user_id=login_user.id, customer_name=c_name[0]).order_by('id').reverse()
        # 申込セッションがあればそこから検索
        elif 'apply' in request.session:
            apply = request.session['apply']
            c_data = CustomerData.objects.filter(user_id=login_user.id, apply_year=apply[0], apply_month=apply[1]).order_by('id').reverse()
        page_obj = paginate_queryset(request, c_data, 15)
        context = {
            'post_list': page_obj.object_list,
            'page_obj': page_obj,
            'form': form,
        }
        return render(request, 'c_data/list.html', context)
    else:
        return redirect('accounts:logout')

# 新規登録【完了】
@login_required
def new_data(request, pk):
    if request.method == 'GET':
        form = CustomerDataForm()
        login_user = request.user
        if pk == login_user.id:
            user = User.objects.get(pk=pk)
            return render(request, 'c_data/new_data.html', {'form': form})
        else:
            return redirect('accounts:logout')

    if request.method == 'POST':
        form = CustomerDataForm()
        obj = CustomerData()
        c_data = CustomerDataForm(request.POST, instance=obj)
        c_data.save()
        return redirect('c_data:list', pk=request.user.id)

# 詳細画面【完了】
@login_required
def detail(request, CustomerData_id, pk):
    if request.method == 'GET':
        # フォームに初期値を流し込む
        detail_data = CustomerData.objects.get(id=CustomerData_id)
        form = DetailDataForm(initial={
            "user_id":detail_data.user_id,
            "status":detail_data.status,
            "introduce_year":detail_data.introduce_year,
            "introduce_month":detail_data.introduce_month,
            "apply_year":detail_data.apply_year,
            "apply_month":detail_data.apply_month,
            "accuracy":detail_data.accuracy,
            "reading":detail_data.reading,
            "customer_name":detail_data.customer_name,
            "progress":detail_data.progress,
            "introducer":detail_data.introducer,
            "introducer_name":detail_data.introducer_name,
            "introduction_type":detail_data.introduction_type,
            "brokerage_fee":detail_data.brokerage_fee,
            "advertising_fee":detail_data.advertising_fee,
            "discount":detail_data.discount,
            "bf_payment_schedule_year":detail_data.bf_payment_schedule_year,
            "bf_payment_schedule_month":detail_data.bf_payment_schedule_month,
            "bf_payment_check":detail_data.bf_payment_check,
            "bf_payment_amount":detail_data.bf_payment_amount,
            "bf_payment_nen":detail_data.bf_payment_nen,
            "bf_payment_month":detail_data.bf_payment_month,
            "bf_payment_day":detail_data.bf_payment_day,
            "ad_payment_schedule_year":detail_data.ad_payment_schedule_year,
            "ad_payment_schedule_month":detail_data.ad_payment_schedule_month,
            "ad_payment_check":detail_data.ad_payment_check,
            "ad_payment_amount":detail_data.ad_payment_amount,
            "ad_payment_nen":detail_data.ad_payment_nen,
            "ad_payment_month":detail_data.ad_payment_month,
            "ad_payment_day":detail_data.ad_payment_day,
            "apartment_name":detail_data.apartment_name,
            "room_number":detail_data.room_number,
            "postal_code":detail_data.postal_code,
            "address1":detail_data.address1,
            "address2":detail_data.address2,
            "real_estate_agent":detail_data.real_estate_agent,
            "tel":detail_data.tel,
            "fax":detail_data.fax,
            "person_in_charge":detail_data.person_in_charge,
            "contract_start_year":detail_data.contract_start_year,
            "contract_start_month":detail_data.contract_start_month,
            "contract_start_day":detail_data.contract_start_day,
            "contract_end_year":detail_data.contract_end_year,
            "contract_end_month":detail_data.contract_end_month,
            "contract_end_day":detail_data.contract_end_day,
            "remarks":detail_data.remarks,
            "progress":detail_data.progress,
            "sex":detail_data.sex,
            "birthday":detail_data.birthday,
            "age":detail_data.age,
            "born":detail_data.born,
            "partner":detail_data.partner,
            "child":detail_data.child,
            "partner_name":detail_data.partner_name,
            "partner_birthday":detail_data.partner_birthday,
            "child1_name":detail_data.child1_name,
            "child1_birthday":detail_data.child1_birthday,
            "child2_name":detail_data.child2_name,
            "child2_birthday":detail_data.child2_birthday,
            "relation":detail_data.relation,
            "encount":detail_data.encount,
            "hope":detail_data.hope,
            "job":detail_data.job,
            "position":detail_data.position,
            "hoby":detail_data.hoby,
            "dream":detail_data.dream,
            "other":detail_data.other,
            "required_documents":detail_data.required_documents,
            "contract_location":detail_data.contract_location,
            "settlement":detail_data.settlement,
            "life_line":detail_data.life_line,
            "confirmation":detail_data.confirmation,
            "guarantor":detail_data.guarantor,
            "hand_ovre_kye":detail_data.hand_ovre_kye,
            "contract_procedures":detail_data.contract_procedures,
            "ADs_invoice":detail_data.ADs_invoice,
        })
        bf_tax_included = math.floor(detail_data.brokerage_fee * 1.08)
        ad_tax_included = math.floor(detail_data.advertising_fee * 1.08)
        if pk == request.user.id:
            user = User.objects.get(pk=pk)
            c_data = CustomerData.objects.get(id=CustomerData_id)
            return render(request, 'c_data/detail.html', {'c_data':c_data, 'form':form, 'bf_tax_included':bf_tax_included, 'ad_tax_included':ad_tax_included})

    if request.method == 'POST':
        customerData_id = CustomerData.objects.get(id=CustomerData_id)
        obj = CustomerData(id=customerData_id.id)
        # 顧客データ
        if 'customer_data' in request.POST:
            CustomerData.objects.update_or_create(
                id=CustomerData_id,
                defaults={
                    'status': request.POST["status"],
                    'introduce_year': request.POST["introduce_year"],
                    'introduce_month': request.POST["introduce_month"],
                    'apply_year': request.POST["apply_year"],
                    'apply_month': request.POST["apply_month"],
                    'accuracy': request.POST["accuracy"],
                    'reading': request.POST["reading"],
                    'customer_name': request.POST["customer_name"],
                    'introducer': request.POST["introducer"],
                    'introducer_name': request.POST["introducer_name"],
                    'introduction_type': request.POST["introduction_type"],
                    'progress': request.POST["progress"],
                }
            )
            return redirect('c_data:detail', pk=request.user.id, CustomerData_id=customerData_id.id)
        # 売上データ
        if 'sales_data' in request.POST:
            CustomerData.objects.update_or_create(
                id=CustomerData_id,
                defaults={
                    'brokerage_fee': request.POST["brokerage_fee"],
                    'advertising_fee': request.POST["advertising_fee"],
                    'discount': request.POST["discount"],
                    'bf_payment_schedule_year': request.POST["bf_payment_schedule_year"],
                    'bf_payment_schedule_month': request.POST["bf_payment_schedule_month"],
                    'bf_payment_check': request.POST["bf_payment_check"],
                    'bf_payment_amount': request.POST["bf_payment_amount"],
                    'bf_payment_nen': request.POST["bf_payment_nen"],
                    'bf_payment_month': request.POST["bf_payment_month"],
                    'bf_payment_day': request.POST["bf_payment_day"],
                    'ad_payment_schedule_year': request.POST["ad_payment_schedule_year"],
                    'ad_payment_schedule_month': request.POST["ad_payment_schedule_month"],
                    'ad_payment_check': request.POST["ad_payment_check"],
                    'ad_payment_amount': request.POST["ad_payment_amount"],
                    'ad_payment_nen': request.POST["ad_payment_nen"],
                    'ad_payment_month': request.POST["ad_payment_month"],
                    'ad_payment_day': request.POST["ad_payment_day"],
                }
            )
            return redirect('c_data:detail', pk=request.user.id, CustomerData_id=customerData_id.id)
        # 物件データ
        if 'property_data' in request.POST:
            CustomerData.objects.update_or_create(
                id=CustomerData_id,
                defaults={
                    'room_number': request.POST["room_number"],
                    'postal_code': request.POST["postal_code"],
                    'address1': request.POST["address1"],
                    'address2': request.POST["address2"],
                    'real_estate_agent': request.POST["real_estate_agent"],
                    'tel': request.POST["tel"],
                    'fax': request.POST["fax"],
                    'person_in_charge': request.POST["person_in_charge"],
                    'contract_start_year': request.POST["contract_start_year"],
                    'contract_start_month': request.POST["contract_start_month"],
                    'contract_start_day': request.POST["contract_start_day"],
                    'contract_end_year': request.POST["contract_end_year"],
                    'contract_end_month': request.POST["contract_end_month"],
                    'contract_end_day': request.POST["contract_end_day"],
                    'remarks': request.POST["remarks"],
                }
            )
            return redirect('c_data:detail', pk=request.user.id, CustomerData_id=customerData_id.id)
        # フローデータ
        if 'flow_data' in request.POST:
            CustomerData.objects.update_or_create(
                id=CustomerData_id,
                defaults={
                    'required_documents': request.POST["required_documents"],
                    'contract_location': request.POST["contract_location"],
                    'settlement': request.POST["settlement"],
                    'life_line': request.POST["life_line"],
                    'confirmation': request.POST["confirmation"],
                    'guarantor': request.POST["guarantor"],
                    'hand_ovre_kye': request.POST["hand_ovre_kye"],
                    'contract_procedures': request.POST["contract_procedures"],
                    'ADs_invoice': request.POST["ADs_invoice"],
                }
            )
            return redirect('c_data:detail', pk=request.user.id, CustomerData_id=customerData_id.id)
        # 詳細データ
        if 'detail_data' in request.POST:
            bd = request.POST["birthday"]
            pbd = request.POST["partner_birthday"]
            c1bd = request.POST["child1_birthday"]
            c2bd = request.POST["child2_birthday"]
            if request.POST["birthday"] == '':
                bd = None
            if request.POST["partner_birthday"] == '':
                pbd = None
            if request.POST["age"] == '':
                age = None
            if request.POST["child1_birthday"] == '':
                c1bd = None
            if request.POST["child2_birthday"] == '':
                c2bd = None
            CustomerData.objects.update_or_create(
                id=CustomerData_id,
                defaults={
                    'sex': request.POST["sex"],
                    'birthday': bd,
                    'age': age,
                    'born': request.POST["born"],
                    'partner': request.POST["partner"],
                    'child': request.POST["child"],
                    'partner_name': request.POST["partner_name"],
                    'partner_birthday': pbd,
                    'child1_name': request.POST["child1_name"],
                    'child1_birthday': c1bd,
                    'child2_name': request.POST["child2_name"],
                    'child2_birthday': c2bd,
                    'relation': request.POST["relation"],
                    'encount': request.POST["encount"],
                    'hope': request.POST["hope"],
                    'job': request.POST["job"],
                    'position': request.POST["position"],
                    'hoby': request.POST["hoby"],
                    'dream': request.POST["dream"],
                    'other': request.POST["other"],
                }
            )
            return redirect('c_data:detail', pk=request.user.id, CustomerData_id=customerData_id.id)
    return redirect('c_data:detail', pk=request.user.id, CustomerData_id=customerData_id.id)

# 見込み管理【完了】
@login_required
def prospect(request, pk):
    # フォームと当月設定
    form = ListSearchForm()
    this_year = datetime.date.today().year
    this_month = datetime.date.today().month
    prospect = CustomerData.objects.filter(user_id=request.user.id)  #見込み客obj

    if request.method == 'POST':
        if 'serch' in request.POST:
            this_year =  int(request.POST["apply_year"])
            this_month = int(request.POST["apply_month"])
        if 'clear' in request.POST:
            this_year =  datetime.date.today().year
            this_month = datetime.date.today().month

    # 【申込み状況】画面
    apply_bf_list = []
    apply_ad_list = []
    apply_dis_list = []
    tmd_bf = []   #This_Month_Deposit
    tmd_ad = []
    tmd_dis = []
    nmd_bf = []   #Next_Month_Deposit
    nmd_ad = []
    nmd_dis = []
    tma_bf = []   #This_Month_Apply
    tma_ad = []
    tma_dis = []
    # ---申込合計---
    apply_data = prospect.filter(status='申込')
    # 仲手
    for a_d_l in apply_data:
        apply_bf_list.append( a_d_l.brokerage_fee)
    apply_bf_sum = math.floor(sum(apply_bf_list)*1.08)
    # AD
    for a_d_l in apply_data:
        apply_ad_list.append( a_d_l.advertising_fee)
    apply_ad_sum = sum(apply_ad_list)
    # 割引
    for a_d_l in apply_data:
        apply_dis_list.append( a_d_l.discount)
    apply_dis_sum = sum(apply_dis_list)
    # 合計
    apply_sum = apply_bf_sum + apply_ad_sum - apply_dis_sum

    # ---当月着金---
    tmd_prospect = prospect.filter(Q(apply_year=this_year), Q(apply_month=this_month), Q(status='審査通過') |  Q(status='契約締結') |  Q(status='完了') )
    # 仲手
    for tmd in tmd_prospect:
        if tmd.bf_payment_schedule_year == this_year and tmd.bf_payment_schedule_month == this_month:
            tmd_bf.append( tmd.brokerage_fee)
    tmd_bf_sum = math.floor(sum(tmd_bf)*1.08)
    # AD
    for tmd in tmd_prospect:
        if tmd.ad_payment_schedule_year == this_year and tmd.ad_payment_schedule_month == this_month:
            tmd_ad.append( tmd.advertising_fee)
    tmd_ad_sum = sum(tmd_ad)
    # 割引
    for tmd in tmd_prospect:
        if tmd.bf_payment_schedule_year == this_year and tmd.bf_payment_schedule_month == this_month:
            tmd_dis.append( tmd.discount)
    tmd_dis_sum = sum(tmd_dis)
    # 合計
    tmd_sum = tmd_bf_sum + tmd_ad_sum - tmd_dis_sum

    # ---翌月着金---
    if this_month + 1 == 13:
        nmd_prospect = prospect.filter(Q(apply_year=this_year + 1), Q(apply_month=1), Q(status='審査通過') |  Q(status='契約締結') |  Q(status='完了'))
    else:
        nmd_prospect = prospect.filter(Q(apply_year=this_year), Q(apply_month=this_month + 1), Q(status='審査通過') |  Q(status='契約締結') |  Q(status='完了'))
    # 仲手
    for nmd in nmd_prospect:
        if nmd.bf_payment_schedule_year == this_year and nmd.bf_payment_schedule_month == this_month + 1:
            nmd_bf.append( nmd.brokerage_fee)
    nmd_bf_sum = math.floor(sum(nmd_bf)*1.08)
    # AD
    for nmd in nmd_prospect:
        if nmd.ad_payment_schedule_year == this_year and nmd.ad_payment_schedule_month == this_month + 1:
            nmd_ad.append( nmd.advertising_fee)
    nmd_ad_sum = sum(nmd_ad)
    # 割引
    for nmd in nmd_prospect:
        if nmd.bf_payment_schedule_year == this_year and nmd.bf_payment_schedule_month == this_month + 1:
            nmd_dis.append( nmd.discount)
    nmd_dis_sum = sum(nmd_dis)
    # 合計
    nmd_sum = nmd_bf_sum + nmd_ad_sum - nmd_dis_sum

    # ---当月申込---
    this_manth_apply = prospect.filter(status='申込',apply_year=this_year, apply_month=this_month)
    # 仲手
    for tma in this_manth_apply:
        tma_bf.append( tma.brokerage_fee)
    tma_bf_sum = math.floor(sum(tma_bf)*1.08)
    # AD
    for tma in this_manth_apply:
        tma_ad.append( tma.advertising_fee)
    tma_ad_sum = sum(tma_ad)
    # 割引
    for tma in this_manth_apply:
        tma_dis.append( tma.discount)
    tma_dis_sum = sum(tma_dis)
    # 合計
    tma_sum = tma_bf_sum + tma_ad_sum - tma_dis_sum

    # 【角度別】画面
    accuracy_count = prospect.filter(status='',apply_year=this_year, apply_month=this_month)
    price_a = accuracy_count.filter(accuracy='A',apply_year=this_year, apply_month=this_month)
    price_b = accuracy_count.filter(accuracy='B',apply_year=this_year, apply_month=this_month)
    price_b_plus = accuracy_count.filter(accuracy='B+',apply_year=this_year, apply_month=this_month)
    price_c = accuracy_count.filter(accuracy='C',apply_year=this_year, apply_month=this_month)
    a_count = 0
    b_count = 0
    b_plus_count = 0
    c_count = 0
    accuracy_list =[]
    price_list = []
    a_price_list = []
    b_price_list = []
    b_plus_price_list = []
    c_price_list = []
    # --件数--
    for l in accuracy_count:
        accuracy_list.append(l.accuracy)
        price_list.append(l.brokerage_fee)
        a_count = accuracy_list.count('A')
        b_count = accuracy_list.count('B')
        b_plus_count = accuracy_list.count('B+')
        c_count = accuracy_list.count('C')
    # --金額--
    if price_a.exists():
        for pa in price_a:
            if pa.accuracy == 'A':
                a_price_list.append(pa.brokerage_fee)
                a_price = sum(a_price_list)
    else:
        a_price = 0
    if price_b.exists():
        for pb in price_b:
            if pb.accuracy == 'B':
                b_price_list.append(pb.brokerage_fee)
                b_price = sum(b_price_list)
    else:
        b_price = 0
    if price_b_plus.exists():
        for pb_plus in price_b_plus:
            if pb_plus.accuracy == 'B+':
                b_plus_price_list.append(pb_plus.brokerage_fee)
                b_plus_price = sum(b_plus_price_list)
    else:
        b_plus_price = 0
    if price_c.exists():
        for pc in price_c:
            if pc.accuracy == 'C':
                c_price_list.append(pc.brokerage_fee)
                c_price = sum(c_price_list)
    else:
        c_price = 0
    # --合計--
    count_sum = a_count + b_count + b_plus_count + c_count
    price_sum = a_price + b_price + b_plus_price + c_price

    # 【見込み客】画面
    prospect_this_month = prospect.filter(status='',apply_year=this_year, apply_month=this_month)
    # 【申込中】画面
    apply_now = prospect.filter(status='申込')
    # 【当月着金予定】画面
    tm_apply = prospect.filter(Q(apply_year=this_year), Q(apply_month=this_month), Q(status='審査通過') |  Q(status='契約締結') |  Q(status='完了'))
    # 【翌月着金予定】画面
    if this_month + 1 == 13:
        nm_apply = prospect.filter(Q(apply_year=this_year + 1), Q(apply_month=1), Q(status='審査通過') |  Q(status='契約締結') |  Q(status='完了'))
    else:
        nm_apply = prospect.filter(Q(apply_year=this_year), Q(apply_month=this_month + 1), Q(status='審査通過') |  Q(status='契約締結') |  Q(status='完了'))

    # render
    if pk == request.user.id:
        user = User.objects.get(pk=pk)
        context = {
            'form': form,
            'this_year': this_year,
            'this_month': this_month,
            'apply_bf_sum': "{:,}".format(apply_bf_sum),
            'apply_ad_sum': "{:,}".format(apply_ad_sum),
            'apply_dis_sum': "{:,}".format(apply_dis_sum),
            'apply_sum': "{:,}".format(apply_sum),
            'tmd_bf_sum': "{:,}".format(tmd_bf_sum),
            'tmd_ad_sum': "{:,}".format(tmd_ad_sum),
            'tmd_dis_sum': "{:,}".format(tmd_dis_sum),
            'tmd_sum': "{:,}".format(tmd_sum),
            'nmd_bf_sum': "{:,}".format(nmd_bf_sum),
            'nmd_ad_sum': "{:,}".format(nmd_ad_sum),
            'nmd_dis_sum': "{:,}".format(nmd_dis_sum),
            'nmd_sum': "{:,}".format(nmd_sum),
            'tma_bf_sum': "{:,}".format(tma_bf_sum),
            'tma_ad_sum': "{:,}".format(tma_ad_sum),
            'tma_dis_sum': "{:,}".format(tma_dis_sum),
            'tma_sum': "{:,}".format(tma_sum),
            'a_count':a_count,
            'b_count':b_count,
            'b_plus_count':b_plus_count,
            'c_count':c_count,
            'a_price':"{:,}".format(a_price),
            'b_price':"{:,}".format(b_price),
            'b_plus_price':"{:,}".format(b_plus_price),
            'c_price':"{:,}".format(c_price),
            'count_sum':count_sum,
            'price_sum':"{:,}".format(price_sum),
            'prospect_this_month':prospect_this_month,
            'apply_now':apply_now,
            'tm_apply':tm_apply,
            'nm_apply':nm_apply,
        }
        return render(request, 'c_data/prospect.html', context)
    else:
        return redirect('accounts:logout')

# 進捗管理【完了】
@login_required
def progress(request, pk):
    form = ListSearchForm()
    progress_data = CustomerData.objects.filter(Q(user_id=request.user.id), Q(status='') |Q(status='申込') | Q(status='審査通過') |  Q(status='契約締結')).order_by('id').reverse().distinct()
    login_user = request.user
    if pk == login_user.id:
        if request.method=='POST':
            # 進捗変更ボタン
            if 'update' in request.POST:
                CustomerData.objects.update_or_create(
                    id=request.POST["id"],
                    defaults={
                        'progress': request.POST["progress"],
                    }
                )
                return redirect('c_data:progress_data', pk=request.user.id)

            # フォームの値を受け取る
            customer_name = request.POST["customer_name"]
            status = request.POST["status"]
            apply_year = request.POST["apply_year"]
            apply_month = request.POST["apply_month"]
            # お客様名検索
            if 'progress_c_name' in request.POST:
                progress_data = CustomerData.objects.filter(user_id=login_user.id, customer_name=customer_name).order_by('id').reverse()
                request.session['progress_c_name'] = [customer_name]  #セッションに入れる
                if'progress_status' in request.session:
                    del request.session['progress_status']    #状況セッションがあれば消す
                if'progress_apply' in request.session:
                    del request.session['progress_apply']    #申込セッションがあれば消す
            # 状況検索
            if 'progress_status' in request.POST:
                progress_data = CustomerData.objects.filter(user_id=login_user.id, status=status).order_by('id').reverse()
                request.session['progress_status'] = [status]    #セッションに入れる
                if 'progress_c_name' in request.session:
                    del request.session['progress_c_name']   #お客様名セッションがあれば消す
                if'progress_apply' in request.session:
                    del request.session['progress_apply']    #申込セッションがあれば消す
            # 申込予定検索
            if 'progress_apply' in request.POST:
                progress_data = CustomerData.objects.filter(user_id=login_user.id, apply_year=apply_year, apply_month=apply_month).order_by('id').reverse()
                request.session['progress_apply'] = [apply_year, apply_month]    #セッションに入れる
                if 'progress_c_name' in request.session:
                    del request.session['progress_c_name']   #お客様名セッションがあれば消す
                if'progress_status' in request.session:
                    del request.session['progress_status']    #状況セッションがあれば消す
            #クリアボタン処理
            if 'clear' in request.POST:
                if 'progress_c_name' in request.session:
                    del request.session['progress_c_name']   #お客様名セッションがあれば消す
                if'progress_apply' in request.session:
                    del request.session['progress_apply']    #申込セッションがあれば消す
                if'progress_status' in request.session:
                    del request.session['progress_status']    #状況セッションがあれば消す

        # 顧客セッションがあればそこから検索
        if 'progress_c_name' in request.session:
            progress_c_name = request.session['progress_c_name']
            progress_data = CustomerData.objects.filter(user_id=login_user.id, customer_name=progress_c_name[0]).order_by('id').reverse()
        # 申込セッションがあればそこから検索
        elif 'progress_apply' in request.session:
            progress_apply = request.session['progress_apply']
            progress_data = CustomerData.objects.filter(user_id=login_user.id, apply_year=progress_apply[0], apply_month=progress_apply[1]).order_by('id').reverse()
        page_obj = paginate_queryset(request, progress_data, 15)
        context = {
            'post_list': page_obj.object_list,
            'page_obj': page_obj,
            'progress_data': progress_data,
            'form':form,
        }
        return render(request, 'c_data/progress.html', context)
    else:
        return redirect('accounts:logout')

# 予実管理【完了】
@login_required
def budget_control(request, pk):
    prospect = CustomerData.objects.filter(user_id=request.user.id)  #見込み客obj
    first_term_yer = now_term + 2009
    latter_term_yer =  now_term + 2010
    mandatory_list = []
    stretch_list = []
    achievement_list = []
    # 必達＆ストレッチのリスト化
    if MusubiyaUser.objects.filter(musubiya_user_id=request.user.id, term=now_term).exists():
        b_c_data = MusubiyaUser.objects.get(musubiya_user_id=request.user.id, term=now_term)
    else:
        b_c_data = MusubiyaUser.objects.get(musubiya_user_id=0)
    mandatory_list.append(b_c_data.mandatory_Oct)
    mandatory_list.append(b_c_data.mandatory_Nov)
    mandatory_list.append(b_c_data.mandatory_Dec)
    mandatory_list.append(b_c_data.mandatory_Jan)
    mandatory_list.append(b_c_data.mandatory_Feb)
    mandatory_list.append(b_c_data.mandatory_Mar)
    mandatory_list.append(b_c_data.mandatory_Apr)
    mandatory_list.append(b_c_data.mandatory_May)
    mandatory_list.append(b_c_data.mandatory_Jun)
    mandatory_list.append(b_c_data.mandatory_Jul)
    mandatory_list.append(b_c_data.mandatory_Aug)
    mandatory_list.append(b_c_data.mandatory_Sep)
    mandatory_sum = sum(mandatory_list)
    stretch_list.append(b_c_data.stretch_Oct)
    stretch_list.append(b_c_data.stretch_Nov)
    stretch_list.append(b_c_data.stretch_Dec)
    stretch_list.append(b_c_data.stretch_Jan)
    stretch_list.append(b_c_data.stretch_Feb)
    stretch_list.append(b_c_data.stretch_Mar)
    stretch_list.append(b_c_data.stretch_Apr)
    stretch_list.append(b_c_data.stretch_May)
    stretch_list.append(b_c_data.stretch_Jun)
    stretch_list.append(b_c_data.stretch_Jul)
    stretch_list.append(b_c_data.stretch_Aug)
    stretch_list.append(b_c_data.stretch_Sep)
    stretch_sum = sum(stretch_list)
    # 実績のリスト化
    # --10月--
    list_10 = []
    achievement_10_bf = prospect.filter(bf_payment_nen=first_term_yer,bf_payment_month=10)
    achievement_10_ad = prospect.filter(ad_payment_nen=first_term_yer,ad_payment_month=10)
    for a10 in achievement_10_bf:
        list_10.append(a10.bf_payment_amount)
    for a10 in achievement_10_ad:
        list_10.append(a10.ad_payment_amount)
    a10_sum = sum(list_10)
    achievement_list.append(a10_sum)
    # --11月--
    list_11 = []
    achievement_11_bf = prospect.filter(bf_payment_nen=first_term_yer,bf_payment_month=11)
    achievement_11_ad = prospect.filter(ad_payment_nen=first_term_yer,ad_payment_month=11)
    for a11 in achievement_11_bf:
        list_11.append(a11.bf_payment_amount)
    for a11 in achievement_11_ad:
        list_11.append(a11.ad_payment_amount)
    a11_sum = sum(list_11)
    achievement_list.append(a11_sum)
    # --12月--
    list_12 = []
    achievement_12_bf = prospect.filter(bf_payment_nen=first_term_yer,bf_payment_month=12)
    achievement_12_ad = prospect.filter(ad_payment_nen=first_term_yer,ad_payment_month=12)
    for a12 in achievement_12_bf:
        list_12.append(a12.bf_payment_amount)
    for a12 in achievement_12_ad:
        list_12.append(a12.ad_payment_amount)
    a12_sum = sum(list_12)
    achievement_list.append(a12_sum)
    # --1月--
    list_1 = []
    achievement_1_bf = prospect.filter(bf_payment_nen=latter_term_yer,bf_payment_month=1)
    achievement_1_ad = prospect.filter(ad_payment_nen=latter_term_yer,ad_payment_month=1)
    for a1 in achievement_1_bf:
        list_1.append(a1.bf_payment_amount)
    for a1 in achievement_1_ad:
        list_1.append(a1.ad_payment_amount)
    a1_sum = sum(list_1)
    achievement_list.append(a1_sum)
    # --2月--
    list_2 = []
    achievement_2_bf = prospect.filter(bf_payment_nen=latter_term_yer,bf_payment_month=2)
    achievement_2_ad = prospect.filter(ad_payment_nen=latter_term_yer,ad_payment_month=2)
    for a2 in achievement_2_bf:
        list_2.append(a2.bf_payment_amount)
    for a2 in achievement_2_ad:
        list_2.append(a2.ad_payment_amount)
    a2_sum = sum(list_2)
    achievement_list.append(a2_sum)
    # --3月--
    list_3 = []
    achievement_3_bf = prospect.filter(bf_payment_nen=latter_term_yer,bf_payment_month=3)
    achievement_3_ad = prospect.filter(ad_payment_nen=latter_term_yer,ad_payment_month=3)
    for a3 in achievement_3_bf:
        list_3.append(a3.bf_payment_amount)
    for a3 in achievement_3_ad:
        list_3.append(a3.ad_payment_amount)
    a3_sum = sum(list_3)
    achievement_list.append(a3_sum)
    # --4月--
    list_4 = []
    achievement_4_bf = prospect.filter(bf_payment_nen=latter_term_yer,bf_payment_month=4)
    achievement_4_ad = prospect.filter(ad_payment_nen=latter_term_yer,ad_payment_month=4)
    for a4 in achievement_4_bf:
        list_4.append(a4.bf_payment_amount)
    for a4 in achievement_4_ad:
        list_4.append(a4.ad_payment_amount)
    a4_sum = sum(list_4)
    achievement_list.append(a4_sum)
    # --5月--
    list_5 = []
    achievement_5_bf = prospect.filter(bf_payment_nen=latter_term_yer,bf_payment_month=5)
    achievement_5_ad = prospect.filter(ad_payment_nen=latter_term_yer,ad_payment_month=5)
    for a5 in achievement_5_bf:
        list_5.append(a5.bf_payment_amount)
    for a5 in achievement_5_ad:
        list_5.append(a5.ad_payment_amount)
    a5_sum = sum(list_5)
    achievement_list.append(a5_sum)
    # --6月--
    list_6 = []
    achievement_6_bf = prospect.filter(bf_payment_nen=latter_term_yer,bf_payment_month=6)
    achievement_6_ad = prospect.filter(ad_payment_nen=latter_term_yer,ad_payment_month=6)
    for a6 in achievement_6_bf:
        list_6.append(a6.bf_payment_amount)
    for a6 in achievement_6_ad:
        list_6.append(a6.ad_payment_amount)
    a6_sum = sum(list_6)
    achievement_list.append(a6_sum)
    # --7月--
    list_7 = []
    achievement_7_bf = prospect.filter(bf_payment_nen=latter_term_yer,bf_payment_month=7)
    achievement_7_ad = prospect.filter(ad_payment_nen=latter_term_yer,ad_payment_month=7)
    for a7 in achievement_7_bf:
        list_7.append(a7.bf_payment_amount)
    for a7 in achievement_7_ad:
        list_7.append(a7.ad_payment_amount)
    a7_sum = sum(list_7)
    achievement_list.append(a7_sum)
    # --8月--
    list_8 = []
    achievement_8_bf = prospect.filter(bf_payment_nen=latter_term_yer,bf_payment_month=8)
    achievement_8_ad = prospect.filter(ad_payment_nen=latter_term_yer,ad_payment_month=8)
    for a8 in achievement_8_bf:
        list_8.append(a8.bf_payment_amount)
    for a8 in achievement_8_ad:
        list_6.append(a6.ad_payment_amount)
    a8_sum = sum(list_8)
    achievement_list.append(a8_sum)
    # --9月--
    list_9 = []
    achievement_9_bf = prospect.filter(bf_payment_nen=latter_term_yer,bf_payment_month=9)
    achievement_9_ad = prospect.filter(ad_payment_nen=latter_term_yer,ad_payment_month=9)
    for a9 in achievement_9_bf:
        list_9.append(a9.bf_payment_amount)
    for a9 in achievement_9_ad:
        list_9.append(a9.ad_payment_amount)
    a9_sum = sum(list_9)
    achievement_list.append(a9_sum)
    # --合計--
    achievement_sum = sum(achievement_list)

    # 【対必達】
    # --単月度　売上達成率   achievement_monaural_achievement_rate--
    amar = []
    if sum(mandatory_list) == 0:
        amar = []
    else:
        amar.append(achievement_list[0] / mandatory_list[0])
        amar.append(achievement_list[1] / mandatory_list[1])
        amar.append(achievement_list[2] / mandatory_list[2])
        amar.append(achievement_list[3] / mandatory_list[3])
        amar.append(achievement_list[4] / mandatory_list[4])
        amar.append(achievement_list[5] / mandatory_list[5])
        amar.append(achievement_list[6] / mandatory_list[6])
        amar.append(achievement_list[7] / mandatory_list[7])
        amar.append(achievement_list[8] / mandatory_list[8])
        amar.append(achievement_list[9] / mandatory_list[9])
        amar.append(achievement_list[10] / mandatory_list[10])
        amar.append(achievement_list[11] / mandatory_list[11])
        amar.append(achievement_sum / mandatory_sum)

    # -単月度　売上高過不足額   achievement_monaural_deficiency_sales--
    amds = []
    amds.append(achievement_list[0] - mandatory_list[0])
    amds.append(achievement_list[1] - mandatory_list[1])
    amds.append(achievement_list[2] - mandatory_list[2])
    amds.append(achievement_list[3] - mandatory_list[3])
    amds.append(achievement_list[4] - mandatory_list[4])
    amds.append(achievement_list[5] - mandatory_list[5])
    amds.append(achievement_list[6] - mandatory_list[6])
    amds.append(achievement_list[7] - mandatory_list[7])
    amds.append(achievement_list[8] - mandatory_list[8])
    amds.append(achievement_list[9] - mandatory_list[9])
    amds.append(achievement_list[10] - mandatory_list[10])
    amds.append(achievement_list[11] - mandatory_list[11])
    amds.append(achievement_sum - mandatory_sum)

    # -累計　売上高過不足額   achievement_cumulative_deficiency_sales--
    aca = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0]  #achievement_cumulative_achievement
    aca[0] = achievement_list[0]
    for i in range(len(achievement_list)-1):
        aca[i+1] = aca[i] + achievement_list[i+1]

    acm = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0]  #achievement_cumulative_mandatory
    acm[0] = mandatory_list[0]
    for i in range(len(mandatory_list)-1):
        acm[i+1] = acm[i] + mandatory_list[i+1]
    acds = []
    acds.append(aca[0] - acm[0])
    acds.append(aca[1] - acm[1])
    acds.append(aca[2] - acm[2])
    acds.append(aca[3] - acm[3])
    acds.append(aca[4] - acm[4])
    acds.append(aca[5] - acm[5])
    acds.append(aca[6] - acm[6])
    acds.append(aca[7] - acm[7])
    acds.append(aca[8] - acm[8])
    acds.append(aca[9] - acm[9])
    acds.append(aca[10] - acm[10])
    acds.append(aca[11] - acm[11])
    acds.append(aca[11] - acm[11])


    # 【対ストレッチ】
    # --単月度　売上達成率   stretch_monaural_achievement_rate--
    smar = []
    if sum(stretch_list) == 0:
        smar = []
    else:
        smar.append(achievement_list[0] / stretch_list[0])
        smar.append(achievement_list[1] / stretch_list[1])
        smar.append(achievement_list[2] / stretch_list[2])
        smar.append(achievement_list[3] / stretch_list[3])
        smar.append(achievement_list[4] / stretch_list[4])
        smar.append(achievement_list[5] / stretch_list[5])
        smar.append(achievement_list[6] / stretch_list[6])
        smar.append(achievement_list[7] / stretch_list[7])
        smar.append(achievement_list[8] / stretch_list[8])
        smar.append(achievement_list[9] / stretch_list[9])
        smar.append(achievement_list[10] / stretch_list[10])
        smar.append(achievement_list[11] / stretch_list[11])
        smar.append(achievement_sum / stretch_sum)

    # -単月度　売上高過不足額   stretch_monaural_deficiency_sales--
    smds = []
    smds.append(achievement_list[0] - stretch_list[0])
    smds.append(achievement_list[1] - stretch_list[1])
    smds.append(achievement_list[2] - stretch_list[2])
    smds.append(achievement_list[3] - stretch_list[3])
    smds.append(achievement_list[4] - stretch_list[4])
    smds.append(achievement_list[5] - stretch_list[5])
    smds.append(achievement_list[6] - stretch_list[6])
    smds.append(achievement_list[7] - stretch_list[7])
    smds.append(achievement_list[8] - stretch_list[8])
    smds.append(achievement_list[9] - stretch_list[9])
    smds.append(achievement_list[10] - stretch_list[10])
    smds.append(achievement_list[11] - stretch_list[11])
    smds.append(achievement_sum - stretch_sum)

    # -累計　売上高過不足額   stretch_cumulative_deficiency_sales--
    sca = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0]  #stretch_cumulative_achievement
    sca[0] = achievement_list[0]
    for i in range(len(achievement_list)-1):
        sca[i+1] = sca[i] + achievement_list[i+1]

    scm = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0]  #stretch_cumulative_mandatory
    scm[0] = stretch_list[0]
    for i in range(len(stretch_list)-1):
        scm[i+1] = scm[i] + stretch_list[i+1]
    scds = []
    scds.append(sca[0] - scm[0])
    scds.append(sca[1] - scm[1])
    scds.append(sca[2] - scm[2])
    scds.append(sca[3] - scm[3])
    scds.append(sca[4] - scm[4])
    scds.append(sca[5] - scm[5])
    scds.append(sca[6] - scm[6])
    scds.append(sca[7] - scm[7])
    scds.append(sca[8] - scm[8])
    scds.append(sca[9] - scm[9])
    scds.append(sca[10] - scm[10])
    scds.append(sca[11] - scm[11])
    scds.append(sca[11] - scm[11])

    # 【紹介分析】
    cy_list = []
    cr_list = []
    cp_list = []
    sy_list = []
    sk_list = []
    sp_list = []
    ss_list = []
    st_list = []
    sum_list = []
    analysis_first =prospect.filter(introduce_year=first_term_yer)
    analysis_latter =prospect.filter(introduce_year=latter_term_yer)
    # ①直依頼　友人
    cy_list.append(analysis_first.filter(introduce_month=10, introduction_type='直依頼　友人').count()) #10月
    cy_list.append(analysis_first.filter(introduce_month=11, introduction_type='直依頼　友人').count()) #11月
    cy_list.append(analysis_first.filter(introduce_month=12, introduction_type='直依頼　友人').count()) #12月
    cy_list.append(analysis_latter.filter(introduce_month=1, introduction_type='直依頼　友人').count()) #1月
    cy_list.append(analysis_latter.filter(introduce_month=2, introduction_type='直依頼　友人').count()) #2月
    cy_list.append(analysis_latter.filter(introduce_month=3, introduction_type='直依頼　友人').count()) #3月
    cy_list.append(analysis_latter.filter(introduce_month=4, introduction_type='直依頼　友人').count()) #4月
    cy_list.append(analysis_latter.filter(introduce_month=5, introduction_type='直依頼　友人').count()) #5月
    cy_list.append(analysis_latter.filter(introduce_month=6, introduction_type='直依頼　友人').count()) #6月
    cy_list.append(analysis_latter.filter(introduce_month=7, introduction_type='直依頼　友人').count()) #7月
    cy_list.append(analysis_latter.filter(introduce_month=8, introduction_type='直依頼　友人').count()) #8月
    cy_list.append(analysis_latter.filter(introduce_month=9, introduction_type='直依頼　友人').count()) #9月
    cy_list_sum = sum(cy_list)
    # ②直依頼　リピート
    cr_list.append(analysis_first.filter(introduce_month=10, introduction_type='直依頼　リピート').count()) #10月
    cr_list.append(analysis_first.filter(introduce_month=11, introduction_type='直依頼　リピート').count()) #11月
    cr_list.append(analysis_first.filter(introduce_month=12, introduction_type='直依頼　リピート').count()) #12月
    cr_list.append(analysis_latter.filter(introduce_month=1, introduction_type='直依頼　リピート').count()) #1月
    cr_list.append(analysis_latter.filter(introduce_month=2, introduction_type='直依頼　リピート').count()) #2月
    cr_list.append(analysis_latter.filter(introduce_month=3, introduction_type='直依頼　リピート').count()) #3月
    cr_list.append(analysis_latter.filter(introduce_month=4, introduction_type='直依頼　リピート').count()) #4月
    cr_list.append(analysis_latter.filter(introduce_month=5, introduction_type='直依頼　リピート').count()) #5月
    cr_list.append(analysis_latter.filter(introduce_month=6, introduction_type='直依頼　リピート').count()) #6月
    cr_list.append(analysis_latter.filter(introduce_month=7, introduction_type='直依頼　リピート').count()) #7月
    cr_list.append(analysis_latter.filter(introduce_month=8, introduction_type='直依頼　リピート').count()) #8月
    cr_list.append(analysis_latter.filter(introduce_month=9, introduction_type='直依頼　リピート').count()) #9月
    cr_list_sum = sum(cr_list)
    # ③直依頼　PP
    cp_list.append(analysis_first.filter(introduce_month=10, introduction_type='直依頼　PP').count()) #10月
    cp_list.append(analysis_first.filter(introduce_month=11, introduction_type='直依頼　PP').count()) #11月
    cp_list.append(analysis_first.filter(introduce_month=12, introduction_type='直依頼　PP').count()) #12月
    cp_list.append(analysis_latter.filter(introduce_month=1, introduction_type='直依頼　PP').count()) #1月
    cp_list.append(analysis_latter.filter(introduce_month=2, introduction_type='直依頼　PP').count()) #2月
    cp_list.append(analysis_latter.filter(introduce_month=3, introduction_type='直依頼　PP').count()) #3月
    cp_list.append(analysis_latter.filter(introduce_month=4, introduction_type='直依頼　PP').count()) #4月
    cp_list.append(analysis_latter.filter(introduce_month=5, introduction_type='直依頼　PP').count()) #5月
    cp_list.append(analysis_latter.filter(introduce_month=6, introduction_type='直依頼　PP').count()) #6月
    cp_list.append(analysis_latter.filter(introduce_month=7, introduction_type='直依頼　PP').count()) #7月
    cp_list.append(analysis_latter.filter(introduce_month=8, introduction_type='直依頼　PP').count()) #8月
    cp_list.append(analysis_latter.filter(introduce_month=9, introduction_type='直依頼　PP').count()) #9月
    cp_list_sum = sum(cp_list)
    # ④紹介　友人
    sy_list.append(analysis_first.filter(introduce_month=10, introduction_type='紹介　友人').count()) #10月
    sy_list.append(analysis_first.filter(introduce_month=11, introduction_type='紹介　友人').count()) #11月
    sy_list.append(analysis_first.filter(introduce_month=12, introduction_type='紹介　友人').count()) #12月
    sy_list.append(analysis_latter.filter(introduce_month=1, introduction_type='紹介　友人').count()) #1月
    sy_list.append(analysis_latter.filter(introduce_month=2, introduction_type='紹介　友人').count()) #2月
    sy_list.append(analysis_latter.filter(introduce_month=3, introduction_type='紹介　友人').count()) #3月
    sy_list.append(analysis_latter.filter(introduce_month=4, introduction_type='紹介　友人').count()) #4月
    sy_list.append(analysis_latter.filter(introduce_month=5, introduction_type='紹介　友人').count()) #5月
    sy_list.append(analysis_latter.filter(introduce_month=6, introduction_type='紹介　友人').count()) #6月
    sy_list.append(analysis_latter.filter(introduce_month=7, introduction_type='紹介　友人').count()) #7月
    sy_list.append(analysis_latter.filter(introduce_month=8, introduction_type='紹介　友人').count()) #8月
    sy_list.append(analysis_latter.filter(introduce_month=9, introduction_type='紹介　友人').count()) #9月
    sy_list_sum = sum(sy_list)
    # ⑤紹介　顧客
    sk_list.append(analysis_first.filter(introduce_month=10, introduction_type='紹介　顧客').count()) #10月
    sk_list.append(analysis_first.filter(introduce_month=11, introduction_type='紹介　顧客').count()) #11月
    sk_list.append(analysis_first.filter(introduce_month=12, introduction_type='紹介　顧客').count()) #12月
    sk_list.append(analysis_latter.filter(introduce_month=1, introduction_type='紹介　顧客').count()) #1月
    sk_list.append(analysis_latter.filter(introduce_month=2, introduction_type='紹介　顧客').count()) #2月
    sk_list.append(analysis_latter.filter(introduce_month=3, introduction_type='紹介　顧客').count()) #3月
    sk_list.append(analysis_latter.filter(introduce_month=4, introduction_type='紹介　顧客').count()) #4月
    sk_list.append(analysis_latter.filter(introduce_month=5, introduction_type='紹介　顧客').count()) #5月
    sk_list.append(analysis_latter.filter(introduce_month=6, introduction_type='紹介　顧客').count()) #6月
    sk_list.append(analysis_latter.filter(introduce_month=7, introduction_type='紹介　顧客').count()) #7月
    sk_list.append(analysis_latter.filter(introduce_month=8, introduction_type='紹介　顧客').count()) #8月
    sk_list.append(analysis_latter.filter(introduce_month=9, introduction_type='紹介　顧客').count()) #9月
    sk_list_sum = sum(sk_list)
    # ⑥紹介　PP
    sp_list.append(analysis_first.filter(introduce_month=10, introduction_type='紹介　PP').count()) #10月
    sp_list.append(analysis_first.filter(introduce_month=11, introduction_type='紹介　PP').count()) #11月
    sp_list.append(analysis_first.filter(introduce_month=12, introduction_type='紹介　PP').count()) #12月
    sp_list.append(analysis_latter.filter(introduce_month=1, introduction_type='紹介　PP').count()) #1月
    sp_list.append(analysis_latter.filter(introduce_month=2, introduction_type='紹介　PP').count()) #2月
    sp_list.append(analysis_latter.filter(introduce_month=3, introduction_type='紹介　PP').count()) #3月
    sp_list.append(analysis_latter.filter(introduce_month=4, introduction_type='紹介　PP').count()) #4月
    sp_list.append(analysis_latter.filter(introduce_month=5, introduction_type='紹介　PP').count()) #5月
    sp_list.append(analysis_latter.filter(introduce_month=6, introduction_type='紹介　PP').count()) #6月
    sp_list.append(analysis_latter.filter(introduce_month=7, introduction_type='紹介　PP').count()) #7月
    sp_list.append(analysis_latter.filter(introduce_month=8, introduction_type='紹介　PP').count()) #8月
    sp_list.append(analysis_latter.filter(introduce_month=9, introduction_type='紹介　PP').count()) #9月
    sp_list_sum = sum(sp_list)
    # ⑦社内紹介
    ss_list.append(analysis_first.filter(introduce_month=10, introduction_type='社内紹介').count()) #10月
    ss_list.append(analysis_first.filter(introduce_month=11, introduction_type='社内紹介').count()) #11月
    ss_list.append(analysis_first.filter(introduce_month=12, introduction_type='社内紹介').count()) #12月
    ss_list.append(analysis_latter.filter(introduce_month=1, introduction_type='社内紹介').count()) #1月
    ss_list.append(analysis_latter.filter(introduce_month=2, introduction_type='社内紹介').count()) #2月
    ss_list.append(analysis_latter.filter(introduce_month=3, introduction_type='社内紹介').count()) #3月
    ss_list.append(analysis_latter.filter(introduce_month=4, introduction_type='社内紹介').count()) #4月
    ss_list.append(analysis_latter.filter(introduce_month=5, introduction_type='社内紹介').count()) #5月
    ss_list.append(analysis_latter.filter(introduce_month=6, introduction_type='社内紹介').count()) #6月
    ss_list.append(analysis_latter.filter(introduce_month=7, introduction_type='社内紹介').count()) #7月
    ss_list.append(analysis_latter.filter(introduce_month=8, introduction_type='社内紹介').count()) #8月
    ss_list.append(analysis_latter.filter(introduce_month=9, introduction_type='社内紹介').count()) #9月
    ss_list_sum = sum(ss_list)
    # ⑦未分類
    st_list.append(analysis_first.filter(introduce_month=10, introduction_type='').count()) #10月
    st_list.append(analysis_first.filter(introduce_month=11, introduction_type='').count()) #11月
    st_list.append(analysis_first.filter(introduce_month=12, introduction_type='').count()) #12月
    st_list.append(analysis_latter.filter(introduce_month=1, introduction_type='').count()) #1月
    st_list.append(analysis_latter.filter(introduce_month=2, introduction_type='').count()) #2月
    st_list.append(analysis_latter.filter(introduce_month=3, introduction_type='').count()) #3月
    st_list.append(analysis_latter.filter(introduce_month=4, introduction_type='').count()) #4月
    st_list.append(analysis_latter.filter(introduce_month=5, introduction_type='').count()) #5月
    st_list.append(analysis_latter.filter(introduce_month=6, introduction_type='').count()) #6月
    st_list.append(analysis_latter.filter(introduce_month=7, introduction_type='').count()) #7月
    st_list.append(analysis_latter.filter(introduce_month=8, introduction_type='').count()) #8月
    st_list.append(analysis_latter.filter(introduce_month=9, introduction_type='').count()) #9月
    st_list_sum = sum(st_list)
    # 紹介数合計
    sum_list.append(cy_list[0] + cr_list[0] + cp_list[0] + sy_list[0] + sk_list[0] + sp_list[0] + ss_list[0] + st_list[0]) #10月
    sum_list.append(cy_list[1] + cr_list[1] + cp_list[1] + sy_list[1] + sk_list[1] + sp_list[1] + ss_list[1] + st_list[1]) #11月
    sum_list.append(cy_list[2] + cr_list[2] + cp_list[2] + sy_list[2] + sk_list[2] + sp_list[2] + ss_list[2] + st_list[2]) #12月
    sum_list.append(cy_list[3] + cr_list[3] + cp_list[3] + sy_list[3] + sk_list[3] + sp_list[3] + ss_list[3] + st_list[3]) #1月
    sum_list.append(cy_list[4] + cr_list[4] + cp_list[4] + sy_list[4] + sk_list[4] + sp_list[4] + ss_list[4] + st_list[4]) #2月
    sum_list.append(cy_list[5] + cr_list[5] + cp_list[5] + sy_list[5] + sk_list[5] + sp_list[5] + ss_list[5] + st_list[5]) #3月
    sum_list.append(cy_list[6] + cr_list[6] + cp_list[6] + sy_list[6] + sk_list[6] + sp_list[6] + ss_list[6] + st_list[6]) #4月
    sum_list.append(cy_list[7] + cr_list[7] + cp_list[7] + sy_list[7] + sk_list[7] + sp_list[7] + ss_list[7] + st_list[7]) #5月
    sum_list.append(cy_list[8] + cr_list[8] + cp_list[8] + sy_list[8] + sk_list[8] + sp_list[8] + ss_list[8] + st_list[8]) #6月
    sum_list.append(cy_list[9] + cr_list[9] + cp_list[9] + sy_list[9] + sk_list[9] + sp_list[9] + ss_list[9] + st_list[9]) #7月
    sum_list.append(cy_list[10] + cr_list[10] + cp_list[10] + sy_list[10] + sk_list[10] + sp_list[10] + ss_list[10] + st_list[10]) #8月
    sum_list.append(cy_list[11] + cr_list[11] + cp_list[11] + sy_list[11] + sk_list[11] + sp_list[11] + ss_list[11] + st_list[11])  #9月
    sum_list_sum = sum(sum_list)

    # RENDER
    if pk == request.user.id:
        user = User.objects.get(pk=pk)
        context = {
            'b_c_data': b_c_data,
            'first_term_yer':first_term_yer,
            'mandatory_list': mandatory_list,
            'mandatory_sum': mandatory_sum,
            'stretch_list': stretch_list,
            'stretch_sum': stretch_sum,
            'achievement_list':achievement_list,
            'achievement_sum':achievement_sum,
            'amds':amds,
            'amar':amar,
            'acds':acds,
            'smds':smds,
            'smar':smar,
            'scds':scds,
            'cy_list':cy_list,
            'cy_list_sum':cy_list_sum,
            'cr_list':cr_list,
            'cr_list_sum':cr_list_sum,
            'cp_list':cp_list,
            'cp_list_sum':cp_list_sum,
            'sy_list':sy_list,
            'sy_list_sum':sy_list_sum,
            'sk_list':sk_list,
            'sk_list_sum':sk_list_sum,
            'sp_list':sp_list,
            'sp_list_sum':sp_list_sum,
            'ss_list':ss_list,
            'ss_list_sum':ss_list_sum,
            'st_list':st_list,
            'st_list_sum':st_list_sum,
            'sum_list':sum_list,
            'sum_list_sum':sum_list_sum,
        }
        return render(request, 'c_data/budget_control.html', context)
    else:
        return redirect('accounts:logout')

# 紹介管理【完了】
@login_required
def data(request, pk):
    # 【紹介者一覧】用
    i_count = CustomerData.objects.filter(user_id=request.user.id).annotate(Count('introducer_name'))
    if i_count.exists():
        list =[]
        for l in i_count:
            list.append(l.introducer_name)
        # res = {e : list.count(e) for e in set(list) if list.count(e) > 0}
            res = [{e : list.count(e) }for e in set(list) if list.count(e) > 0]
        page_obj = paginate_queryset(request, res, 10).object_list
    else:
        page_obj = None
        res = None


    # 【月別紹介数】用
    # 今年&今月
    form = ListSearchForm()
    this_year = datetime.date.today().year
    this_month = datetime.date.today().month
    if request.method=='POST':
        # 申込予定検索
        if 'intro' in request.POST:
            # フォームの値を受け取る
            this_year = request.POST["introduce_year"]
            this_month = request.POST["introduce_month"]
            monthly_introduce = CustomerData.objects.filter(user_id=request.user.id, introduce_year=this_year, introduce_month=this_month).order_by('id').reverse()
        #クリアボタン処理
        if 'clear' in request.POST:
            monthly_introduce = CustomerData.objects.filter(user_id=request.user.id, introduce_year=this_year, introduce_month=this_month).order_by('id').reverse()
    # 今月紹介一覧
    else:
        monthly_introduce = CustomerData.objects.filter(user_id=request.user.id, introduce_year=this_year, introduce_month=this_month).order_by('id').reverse()

    login_user = request.user
    if pk == login_user.id:
        user = User.objects.get(pk=pk)
        context = {
            'post_list': page_obj,
            'page_obj': page_obj,
            'res': res,
            'form': form,
            'monthly_introduce': monthly_introduce,
            'this_month': this_month,
            'this_year': this_year,
        }
        return render(request, 'c_data/data.html', context)
    else:
        return redirect('accounts:logout')

# 条件検索画面
@login_required
def conditions(request, CustomerData_id, pk):
    if request.method == 'GET':
        # フォームに初期値を流し込む
        detail_data = CustomerData.objects.get(id=CustomerData_id)
        form = DetailDataForm(initial={
            "user_id": detail_data.user_id,
            "status": detail_data.status,
            "introduce_year": detail_data.introduce_year,
            "introduce_month": detail_data.introduce_month,
            "apply_year": detail_data.apply_year,
            "apply_month": detail_data.apply_month,
            "accuracy": detail_data.accuracy,
            "reading": detail_data.reading,
            "customer_name": detail_data.customer_name,
            "progress": detail_data.progress,
            "introducer": detail_data.introducer,
            "introducer_name": detail_data.introducer_name,
            "introduction_type": detail_data.introduction_type,
            "brokerage_fee": detail_data.brokerage_fee,
            "advertising_fee": detail_data.advertising_fee,
            "discount": detail_data.discount,
            "bf_payment_schedule_year": detail_data.bf_payment_schedule_year,
            "bf_payment_schedule_month": detail_data.bf_payment_schedule_month,
            "bf_payment_check": detail_data.bf_payment_check,
            "bf_payment_amount": detail_data.bf_payment_amount,
            "bf_payment_nen": detail_data.bf_payment_nen,
            "bf_payment_month": detail_data.bf_payment_month,
            "bf_payment_day": detail_data.bf_payment_day,
            "ad_payment_schedule_year": detail_data.ad_payment_schedule_year,
            "ad_payment_schedule_month": detail_data.ad_payment_schedule_month,
            "ad_payment_check": detail_data.ad_payment_check,
            "ad_payment_amount": detail_data.ad_payment_amount,
            "ad_payment_nen": detail_data.ad_payment_nen,
            "ad_payment_month": detail_data.ad_payment_month,
            "ad_payment_day": detail_data.ad_payment_day,
            "apartment_name": detail_data.apartment_name,
            "room_number": detail_data.room_number,
            "postal_code": detail_data.postal_code,
            "address1": detail_data.address1,
            "address2": detail_data.address2,
            "real_estate_agent": detail_data.real_estate_agent,
            "tel": detail_data.tel,
            "fax": detail_data.fax,
            "person_in_charge": detail_data.person_in_charge,
            "contract_start_year": detail_data.contract_start_year,
            "contract_start_month": detail_data.contract_start_month,
            "contract_start_day": detail_data.contract_start_day,
            "contract_end_year": detail_data.contract_end_year,
            "contract_end_month": detail_data.contract_end_month,
            "contract_end_day": detail_data.contract_end_day,
            "remarks": detail_data.remarks,
            "progress": detail_data.progress,
            "sex": detail_data.sex,
            "birthday": detail_data.birthday,
            "age": detail_data.age,
            "born": detail_data.born,
            "partner": detail_data.partner,
            "child": detail_data.child,
            "partner_name": detail_data.partner_name,
            "partner_birthday": detail_data.partner_birthday,
            "child1_name": detail_data.child1_name,
            "child1_birthday": detail_data.child1_birthday,
            "child2_name": detail_data.child2_name,
            "child2_birthday": detail_data.child2_birthday,
            "relation": detail_data.relation,
            "encount": detail_data.encount,
            "hope": detail_data.hope,
            "job": detail_data.job,
            "position": detail_data.position,
            "hoby": detail_data.hoby,
            "dream": detail_data.dream,
            "other": detail_data.other,
            "required_documents": detail_data.required_documents,
            "contract_location": detail_data.contract_location,
            "settlement": detail_data.settlement,
            "life_line": detail_data.life_line,
            "confirmation": detail_data.confirmation,
            "guarantor": detail_data.guarantor,
            "hand_ovre_kye": detail_data.hand_ovre_kye,
            "contract_procedures": detail_data.contract_procedures,
            "ADs_invoice": detail_data.ADs_invoice,
        })
        bf_tax_included = math.floor(detail_data.brokerage_fee * 1.08)
        ad_tax_included = math.floor(detail_data.advertising_fee * 1.08)
        if pk == request.user.id:
            user = User.objects.get(pk=pk)
            c_data = CustomerData.objects.get(id=CustomerData_id)
            return render(request, 'c_data/conditions.html', {'c_data': c_data, 'form': form, 'bf_tax_included': bf_tax_included, 'ad_tax_included': ad_tax_included})
    if request.method == 'POST':
        use_selenium.rainsOpen()
    return redirect('c_data:conditions', pk=request.user.id, CustomerData_id=CustomerData_id)
