from . import order_blue


# 订单模块
@order_blue.route('/list')
def order_list():
    return 'order_list'