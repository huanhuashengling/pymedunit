from django.shortcuts import render, HttpResponseRedirect
from testSheets.models import TestSheet, LaboratoryReport, LaboratoryLog, LaboratoryItem, LabInfoETZ, UploadSheetDir
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

def list_upload_dirs(request):
  uploadSheetDirs = UploadSheetDir.objects.all()
  return render(request, 'test_sheet/list_upload_dirs.html', {"uploadSheetDirs": uploadSheetDirs, "show_title": "化验单上传列表"})

def parse_read_dir_sheet_data(request):
  uploadSheetDirId = request.GET.get('uploadSheetDirId', None)
  uploadSheetDir = UploadSheetDir.objects.get(id=uploadSheetDirId)
  dir_str = uploadSheetDir.dir_str

  currPath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media' + "/" + dir_str)

  LabInfoETZData = LabInfoETZ.objects.values('lab_info_Z', 'lab_info_E')
  LabInfoETZArr = {}
  for LabInfoETZItem in LabInfoETZData:
    LabInfoETZArr[LabInfoETZItem['lab_info_Z']] = LabInfoETZItem['lab_info_E']
  
  # print('details:', LabInfoETZArr)
  files= os.listdir(currPath)
  for filename in files: #遍历文件夹
    hasTheSameReport = False

    if "mht" in filename:
      continue
      
    if not os.path.isdir(filename): #判断是否是文件夹，不是文件夹才打开
      # print(filename)
      file = os.path.join(currPath, filename)
      # file = os.path.join(settings.BASE_DIR, 'pymedunit/static', filename)
      # file = os.path.join(settings.BASE_DIR, 'pymedunit/static', "LisResult8.htm")
      with open(file, 'r', encoding='gbk') as f:
          html = f.read()

      labReport = LaboratoryReport()    
      soup = BeautifulSoup(html, 'html.parser')
      tables = soup.find_all("table")

      if len(tables) == 0:
        continue

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
              # print("tLabReport.id", tLabReport.id)
              hasTheSameReport = True

          # print("key", key, " value ", value)
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
          elif "年龄" in key :
            value = table3tds[i+1].text.strip().replace(u'\xa0', '').replace(' ', '').replace('岁', '')
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
  
  uploadSheetDir.is_parsed = True
  uploadSheetDir.save()

  return HttpResponse("success")

def splitReferValue(str):
  if "～" in str: 
    return [str.split("～")[0], str.split("～")[1].replace('u/l', '')]
  elif "<" in str:
    return [0, str.split("<")[1].replace('u/l', '')]
