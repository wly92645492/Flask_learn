# 导入蓝图
from flask import Blueprint

# 创建蓝图对象
user_blue = Blueprint('user',__name__)

from . import views