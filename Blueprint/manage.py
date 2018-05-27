from flask import Flask
from users import user_blue
from orders import order_blue

app = Flask(__name__)

# 将蓝图注册到app
app.register_blueprint(user_blue)
app.register_blueprint(order_blue)


if __name__ == '__main__':
    app.run(debug=True)