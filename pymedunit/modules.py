from mongoengine import *


# Create your models here.
class TestSheet(Document):
    # testSheet
    meta = {
        # 数据库中显示的名字
        'collection': 'test_sheet_data'
    }
    test_sheet_id = SequenceField(required=True, primary_key=True)
    author = StringField()
    title = StringField()

    # 可以定义查询集
    @queryset_manager
    def show_newest(doc_cls, queryset):
        # 通过test_sheet_id降序显示
        return queryset.order_by('-test_sheet_id')