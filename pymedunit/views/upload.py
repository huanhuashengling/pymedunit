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

def sheet_upload(request):
  # patientDatas = LaboratoryReport.objects.values('patient_name', "patient_age", "patient_gender", "medical_record_num", "department", "bed_no", "clinical_diagnosis").annotate(dcount=Count('patient_name'))
  return render(request, 'test_sheet/sheet_upload.html', {"show_title": "Sheet Upload" })

def attachment_upload(request):
  att_file = request.FILES.get('attachment', None)
  doc_uuid = request.POST.get('doc_uuid', None)
  sheet_num = request.POST.get('sheet_num', None)
  relative_path = request.POST.get('relative_path', None)
  patient_name = relative_path.split("_")[0]
  medical_record_num = relative_path.split("_")[1]
  
  uploadSheetDir = UploadSheetDir.objects.filter(patient_name=patient_name).filter(medical_record_num=medical_record_num).first()

  if not uploadSheetDir:
    result = UploadSheetDir.objects.create(patient_name=patient_name, 
      medical_record_num=medical_record_num, 
      dir_str=relative_path, 
      sheet_num=sheet_num)

  if att_file:
      currPath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media' + "/" + relative_path)
      if not os.path.exists(currPath):
        os.makedirs(currPath)
      # 保存文件到硬盘中
      # file_dir = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files' + "/" + relative_path), att_file.name)
      file_dir = os.path.join(currPath, att_file.name)
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