from . import user_blue

# 用户模块
@user_blue.route('/user')
def user_info():
    return 'user_info'
