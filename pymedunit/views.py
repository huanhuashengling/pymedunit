from django.shortcuts import render, HttpResponseRedirect
from testSheets.models import TestSheet, LaboratoryReport, LaboratoryLog, LaboratoryItem, LabInfoETZ
import datetime
import time
from bs4 import BeautifulSoup
from lxml import etree
from django.conf import settings
from django.conf.urls.static import static
from datetime import datetime
import os
from django.http import JsonResponse
from django.db.models import Count

def hello(request):
  return HttpResponse("Hello world")

def current_datetime(request):
  current_date = datetime.datetime.now()
  #html = t.render({'current_date': now}) # Context({'current_date': now}) context must be a dict rather than Context.
  return render(request, 'dateapp/current_datetime.html', locals())

def hours_ahead(request, hour_offset):
  try:
    hour_offset = int(hour_offset)
  except ValueError:
    raise Http404()
  next_time = datetime.datetime.now() + datetime.timedelta(hours=hour_offset)
  return render(request, 'dateapp/hours_ahead.html', locals())

  # Create your views here.
def home(request):
    # 主页将所有的数据库数据返回
    return render(request, 'dateapp/home.html', {"show_title": "所有诗词信息", "testSheets": TestSheet.objects.all()})

def insert(request):
  LabInfoETZData = LabInfoETZ.objects.values('lab_info_Z', 'lab_info_E')
  LabInfoETZArr = {}
  for LabInfoETZItem in LabInfoETZData:
    LabInfoETZArr[LabInfoETZItem['lab_info_Z']] = LabInfoETZItem['lab_info_E']
  
  # print('details:', LabInfoETZArr)
  files= os.listdir(os.path.join(settings.BASE_DIR, 'pymedunit/static'))
  for filename in files: #遍历文件夹
    hasTheSameReport = False
    if "mht" in filename:
      continue
    if not os.path.isdir(filename): #判断是否是文件夹，不是文件夹才打开
      print(filename)

      file = os.path.join(settings.BASE_DIR, 'pymedunit/static', filename)
      # file = os.path.join(settings.BASE_DIR, 'pymedunit/static', "LisResult8.htm")
      with open(file, 'r', encoding='gbk') as f:
          html = f.read()

      labReport = LaboratoryReport()    
      soup = BeautifulSoup(html, 'html.parser')
      tables = soup.find_all("table")
      title = tables[1].find('b').text.strip()
      labReport.title = title

      table2tds = tables[2].find_all('font')
      # print(table2tds)
      for i in range(0, len(table2tds), 2):
          key = table2tds[i].text.strip().replace(u'\xa0', '').replace(' ', '').replace(':', '')
          value = table2tds[i+1].text.strip().replace(u'\xa0', '').replace(' ', '')
          # print("key", key, " value ", value)
          
          if "申请单号" == key:
            tLabReport = LaboratoryReport.objects.filter(apply_num=value).first()
            if tLabReport:
              print("tLabReport.id", tLabReport.id)
              hasTheSameReport = True
          setattr(labReport, LabInfoETZArr[key], value)

      if hasTheSameReport:
        # print("break")
        continue

      table3tds = tables[3].find_all('font')
      for i in range(0, len(table3tds), 2):
          # print(i)
          key = table3tds[i].text.strip().replace(u'\xa0', '').replace(' ', '').replace(':', '')
          if "日期" in key :
            value = table3tds[i+1].text.strip().replace(u'\xa0', '').replace(u'\n', '').replace('        ', '')
            if len(value) == 9:
              value = value + " 00:00:00"
            elif "<%" in value:
              value = "1937-1-1 00:00:00"

            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
          else:
            value = table3tds[i+1].text.strip().replace(u'\xa0', '').replace(' ', '')

          setattr(labReport, LabInfoETZArr[key], value)

      labReport.save();
      
      table4tds = tables[4].find_all('font')
      hasNum = "true"

      step = 5
      tItemLabel = table4tds[0].text.strip().replace(u'\xa0', '').replace(' ', '')
      if(tItemLabel == "项目"):
        step = 4
        hasNum = "false"
      elif(tItemLabel == "细菌名称"):
        continue

      for i in range(0, len(table4tds), step):
          # print(i)
          itemLabel = table4tds[i].text.strip().replace(u'\xa0', '').replace(' ', '')
          if(itemLabel == "NO."):
            continue

          if(itemLabel == "项目"):
            continue

          if(hasNum == "false"):
            resultValue = table4tds[i+1].text.strip().replace(u'\xa0', '').replace(' ', '')
            referValue = table4tds[i+2].text.strip().replace(u'\xa0', '').replace(' ', '')
            itemUnit = table4tds[i+3].text.strip().replace(u'\xa0', '').replace(' ', '')
            # print("aaa", table4tds[i+1].get("color"))

            if table4tds[i+1]:
              if table4tds[i+1].get("color") == "red":
                towards = "high"
              elif table4tds[i+1].get("color") == "blue":
                towards = "low"
              else:
                towards = "-"
          else:
            itemLabel = table4tds[i+1].text.strip().replace(u'\xa0', '').replace(' ', '')
            resultValue = table4tds[i+2].text.strip().replace(u'\xa0', '').replace(' ', '')
            # print("bbb", table4tds[i+2].get("color"))
            # print("bbb", table4tds[i+2])
            if table4tds[i+2]:
              if table4tds[i+2].get("color") == "red":
                towards = "high"
              elif table4tds[i+2].get("color") == "blue":
                towards = "low"
              else:
                towards = "-"
            referValue = table4tds[i+3].text.strip().replace(u'\xa0', '').replace(' ', '')
            itemUnit = table4tds[i+4].text.strip().replace(u'\xa0', '').replace(' ', '')

          resultValue

          labItem = LaboratoryItem.objects.filter(laboratory_item_label=itemLabel).first()
          if not labItem:
            # print("没有这个项目第一次", itemLabel)
            # splitData = splitReferValue(referValue)
            # if splitData:
            #   # print("splitData", splitData)
            #   referStart = splitData[0]
            #   referEnd = splitData[1]
            # else:
            #   referStart = 0.00
            #   referEnd = 0.00
            result = LaboratoryItem.objects.create(laboratory_item_label=itemLabel, refer_value=referValue, item_unit=itemUnit)
              # print(result)

          labItem = LaboratoryItem.objects.filter(laboratory_item_label=itemLabel).first()
          # print("输出目前结果", labItem.id, resultValue, towards, referValue)

          # if not labItem:
          #   print("没有这个项目第二次", labItem, resultValue, towards, referValue)
          #   print("itemLabel", itemLabel)
          #   
          labLog = LaboratoryLog()
          labLog.laboratory_reports_id = labReport.id
          labLog.laboratory_items_id = labItem.id
          labLog.result_value = resultValue
          labLog.towards = towards

          labLog.save()
    # break
  return render(request, 'dateapp/home.html', {"show_title": title, 'current_date': title})

def splitReferValue(str):
  if "～" in str: 
    return [str.split("～")[0], str.split("～")[1].replace('u/l', '')]
  elif "<" in str:
    return [0, str.split("<")[1].replace('u/l', '')]

def chart(request):
  # labItems = LaboratoryItem.objects.raw('SELECT * FROM laboratory_reports GROUP BY patient_name')
  patientData = LaboratoryReport.objects.values('patient_name').annotate(dcount=Count('patient_name'))
  print(patientData)
  labItems = LaboratoryItem.objects.values_list("laboratory_item_label", "refer_value" ).first()
  return render(request, 'dateapp/chart.html', {"show_title": "Chart趋势图表", 'patientData': "patientData!"})

def get_data(request, *args, **kwargs):
  filterItem = "白细胞计数"
  patientName = "谢申贵"
  data = []
  labels = []

  labItem = LaboratoryItem.objects.filter(laboratory_item_label=filterItem).first()
  print(labItem.id, filterItem)
  labReports = LaboratoryReport.objects.filter(patient_name="谢申贵").order_by("collect_time").all()
  # print(labReports)
  for labReport in labReports:
    labLog = LaboratoryLog.objects.filter(laboratory_reports_id=labReport.id).filter(laboratory_items_id=labItem.id).first()
    if labLog:
      data.append(labLog.result_value)
      # value = datetime.strptime(labReport.collect_time, "%Y-%m-%d %H:%M:%S")
      tCollectTime = labReport.collect_time.strftime("%m月%d日 %H:%M")
      labels.append(tCollectTime)
      print(labReport.id, labLog.id, labItem.refer_value, labLog.result_value, labLog.towards, tCollectTime)
    
  content = {
      'data': data,
      'labels': labels,
      'title': patientName + " - " + filterItem
  }
  print(data)
  return JsonResponse(content)


def patient_list(request):
  patientDatas = LaboratoryReport.objects.values('patient_name', "patient_age", "patient_gender", "medical_record_num", "department", "bed_no", "clinical_diagnosis").annotate(dcount=Count('patient_name'))
  print(patientDatas[0]["patient_name"])
  # print(patientDatas[0])
  return render(request, 'dateapp/patient_list.html', {"show_title": "Patient List", 'patientDatas': patientDatas})

def patient_info(request, username):
  patientData = LaboratoryReport.objects.filter(patient_name=username).first()

  LabInfoETZData = LabInfoETZ.objects.values('lab_info_Z', 'lab_info_E')
  LabInfoETZArr = {}
  for LabInfoETZItem in LabInfoETZData:
    # print(LabInfoETZItem['lab_info_E'])
    # itemname = LabInfoETZItem['lab_info_E']
    # print(getattr(patientData, itemname))
    LabInfoETZArr[LabInfoETZItem['lab_info_Z']] = getattr(patientData, LabInfoETZItem['lab_info_E'])
  print(LabInfoETZArr)
  return render(request, 'dateapp/patient_info.html', {"show_title": "Patient Info", 'patientData': LabInfoETZArr})

# def add(request):
#     if request.method == 'POST':
#         author = request.POST.get('author', "")
#         poem = Poem(author=author)
#         poem.save()
#         title = request.POST.get("title", "")
#         poem.title = title
#         # 如果添加数据库没有的数据，添加试成功的，但是这个tag是不会被保存的
#         poem.tag = 'tag'
#         poem.save()
#         return HttpResponseRedirect('/')
#     else:
#         return render(request, 'add.html')


# def search(request):
#     if request.method == 'POST':
#         author = request.POST.get('author')
#         poems = Poem.show_newest(author=author)
#         # 此处的查询结果poems是一个list
#         return render(request, 'home.html', {"show_title": "查询结果", "poems": poems})

#     else:
#         return render(request, 'search.html')


# def modify(request):
#     if request.method == 'POST':
#         id = request.POST.get('id')
#         author = request.POST.get('author', "")
#         title = request.POST.get("title", "")
#         poems = Poem.objects(poem_id=id)
#         for poem in poems:
#             poem.update(author=author, title=title)
#         return HttpResponseRedirect('/')
#     else:
#         return render(request, 'modify.html')


# def delete(request):
#     if request.method == 'POST':
#         id = request.POST.get('id')
#         poems = Poem.objects(poem_id=id)
#         for poem in poems:
#             poem.delete()
#         return HttpResponseRedirect('/')
#     else:
#         return render(request, 'delete.html')



