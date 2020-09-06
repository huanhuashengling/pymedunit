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
import logging, traceback, pprint
from django.core import serializers

def patient_list(request):
  patientDatas = LaboratoryReport.objects.values('patient_name', "patient_age", "patient_gender", "medical_record_num", "department", "bed_no", "clinical_diagnosis").annotate(dcount=Count('patient_name'))
  # patientDatas = LaboratoryReport.objects.all()
  # print(patientDatas[0]["patient_name"])
  # patientName = patientDatas[0]["medical_record_num"]
  return render(request, 'test_sheet/patient_list.html', {"show_title": "Patient List", "patientDatas": patientDatas})

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
  return content