from django.shortcuts import render, HttpResponseRedirect
from testSheets.models import TestSheet, LaboratoryReport, LaboratoryLog, LaboratoryItem, LabInfoETZ
from testSheets.models import InvestigatePlate, InvestigateProject, InvestigateIndicator, InvestigateItem
import datetime
import time
from bs4 import BeautifulSoup
from lxml import etree
from django.conf import settings
from django.conf.urls.static import static
from datetime import datetime
import os
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.core import serializers
import re
import json

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
  return render(request, 'test_sheet/home.html', {"show_title": title, 'current_date': title})

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
  return render(request, 'test_sheet/chart.html', {"show_title": "Chart趋势图表", 'patientData': "patientData!"})

def get_items_chart_data(request, username, indicator_id):
  itemsData = []
  investigateItems =  InvestigateItem.objects.filter(investigate_indicators_id=indicator_id).all()
  for investigateItem in investigateItems:
    itemsData.append(get_item_chart_common(request, username, investigateItem.id))
  return JsonResponse(itemsData, safe=False)

def get_item_chart_data(request, username, item_id):
  content = get_item_chart_common(request, username, item_id)
  return JsonResponse(content)

def get_item_chart_common(request, username, item_id):
  data = []
  labels = []
  referValue = "";
  investigateItem =  InvestigateItem.objects.filter(id=item_id).first()

  labItem = LaboratoryItem.objects.filter(laboratory_item_label=investigateItem.item_title).first()
  jzLabItem = LaboratoryItem.objects.filter(laboratory_item_label="急诊" + investigateItem.item_title).first()
  query = ""
  
  if not labItem is None and not jzLabItem is None:
    query = Q(laboratory_items_id=labItem.id) | Q(laboratory_items_id=jzLabItem.id)
  elif not labItem is None:
    query = Q(laboratory_items_id=labItem.id)
  elif not jzLabItem is None:
    query = Q(laboratory_items_id=jzLabItem.id)
  # print(query)
  # print(labItem.id, labItem.laboratory_item_label, username)
  labReports = LaboratoryReport.objects.filter(patient_name=username).order_by("collect_time").all()
  # print(labReports)
  for labReport in labReports:
    # labLog = LaboratoryLog.objects.filter(laboratory_reports_id=labReport.id).filter(laboratory_items_id=labItem.id).first()
    labLog = LaboratoryLog.objects.filter(laboratory_reports_id=labReport.id).filter(query).first()
    if labLog:
      referValue = dealWithReferValue(labItem.refer_value)
      data.append(labLog.result_value)
      # value = datetime.strptime(labReport.collect_time, "%Y-%m-%d %H:%M:%S")
      tCollectTime = labReport.collect_time.strftime("%m月%d日 %H:%M")
      labels.append(tCollectTime)
      # print(labReport.id, labLog.id, labItem.refer_value, labLog.result_value, labLog.towards, tCollectTime)
    
  content = {
      'data': data,
      'labels': labels,
      'refer_value': referValue,
      'title': username + " - " + labItem.laboratory_item_label
  }
  return content;

def patient_list(request):
  patientDatas = LaboratoryReport.objects.values('patient_name', "patient_age", "patient_gender", "medical_record_num", "department", "bed_no", "clinical_diagnosis").annotate(dcount=Count('patient_name'))
  # print(patientDatas[0]["patient_name"])
  return render(request, 'test_sheet/patient_list.html', {"show_title": "Patient List"})

def patient_info(request, username):
  investigatePlates = InvestigatePlate.objects.all()
  return render(request, 'test_sheet/patient_info.html', {"show_title": "Patient Info", 'investigatePlates': investigatePlates, 'username': username})

def get_investigate_project_data(request, plate_id):
  # investigateProjects = serializers.serialize("json", InvestigateProject.objects.filter(investigate_plates_id=plate_id).all())
  investigateProjects =  InvestigateProject.objects.filter(investigate_plates_id=plate_id).all()
  projectSelectHtml = "<option value=''>请选择</option>";
  for investigateProject in investigateProjects:
    projectSelectHtml += "<option value='" + str(investigateProject.id) + "'>" + investigateProject.project_title + "</option>"
  # print(projectSelectHtml)
  return HttpResponse(projectSelectHtml)

def get_investigate_indicator_data(request, project_id):
  investigateIndicators =  InvestigateIndicator.objects.filter(investigate_projects_id=project_id).all()
  indicatorSelectHtml = "<option value=''>请选择</option>";
  for investigateIndicator in investigateIndicators:
    indicatorSelectHtml += "<option value='" + str(investigateIndicator.id) + "'>" + investigateIndicator.indicator_title + "</option>"
  # print(indicatorSelectHtml)
  return HttpResponse(indicatorSelectHtml)

def get_investigate_item_data(request, indicator_id):
  investigateItems =  InvestigateItem.objects.filter(investigate_indicators_id=indicator_id).all()
  itemSelectHtml = "<option value=''>请选择</option>";
  for investigateItem in investigateItems:
    itemSelectHtml += "<option value='" + str(investigateItem.id) + "'>" + investigateItem.item_title + "</option>"
  # print(itemSelectHtml)
  return HttpResponse(itemSelectHtml)

def dealWithReferValue(referValue):
  result = []
  if referValue.find("～"):
    result.append(referValue.split("～")[0])
    result.append(referValue.split("～")[1])
  return result

def sheet_upload(request):
  # patientDatas = LaboratoryReport.objects.values('patient_name', "patient_age", "patient_gender", "medical_record_num", "department", "bed_no", "clinical_diagnosis").annotate(dcount=Count('patient_name'))
  return render(request, 'test_sheet/sheet_upload.html', {"show_title": "Sheet Upload" })

def attachment_upload(request):
  att_file = request.FILES.get('attachment', None)
  doc_uuid = request.POST.get('doc_uuid', None)
  # print(request.FILES)
  if att_file:
      # 保存文件到硬盘中
      file_dir = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), att_file.name)
      f = open(file_dir, 'wb')
      for i in att_file.chunks():
          f.write(i)
      f.close()
      # 下载和预览的url
      url = settings.MEDIA_URL + att_file.name
      file_type = re.search(r'[^.]+\w$', att_file.name).group()   # 提前文件后缀名

      # 文件类型，可自行增删
      img_list = ['jpg', 'jpeg', 'jpe', 'gif', 'png', 'pns', 'bmp', 'png', 'tif']
      pdf_list = ['pdf']
      text_list = ['txt', 'md', 'csv', 'nfo', 'ini', 'json', 'php', 'js', 'css']
      htm_list = ['html', 'htm', 'mht']

      # bootstrap fileinput 上传文件的回显参数，initialPreview（列表），initialPreviewConfig（列表）
      initialPreview = []
      # 根据上传的文件类型，生成不同的HTML，
      #if file_type in img_list:
       #   initialPreview.append("<img src='" + url + "' class='file-preview-image' style='max-width:100%;max-height:100%;'>")
      #elif file_type in pdf_list:
       #   initialPreview.append("<div class='file-preview-frame'><div class='kv-file-content'><embed class='kv-preview-data file-preview-pdf' src='" + url +
       #                         "' type='application/pdf' style='width:100%;height:160px;'></div></div>")
      if file_type in htm_list:
          initialPreview.append("<div class='file-preview-frame'><div class='kv-file-content'><textarea class='kv-preview-data file-preview-text' title='" + att_file.name +
                                "' readonly style='width:213px;height:160px;'></textarea></div></div>")
      else:
          initialPreview.append("<div class='file-preview-other'><span class='file-other-icon'><i class='glyphicon glyphicon-file'></i></span></div>")

      initialPreviewConfig = [{
          'caption': att_file.name,    # 文件标题
          'type': file_type,    # 文件类型
          'downloadUrl': url,    # 下载地址
          'url': '/del_doc_file/',    # 预览中的删除按钮的url
          'size': os.path.getsize(file_dir),    # 文件大小
          'extra': {'doc_uuid': doc_uuid},      # 删除文件携带的参数
          'key': att_file.name,    # 删除时ajax携带的参数
      }]
      # 返回json数据，initialPreview initialPreviewConfig 会替换初始化插件时的这两个参数 append:True 将内容添加到初始化预览
      return HttpResponse(json.dumps({'initialPreview':initialPreview, 'initialPreviewConfig':initialPreviewConfig,'append': True}))
  else:
      return HttpResponse(json.dumps({'status': False}))

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



