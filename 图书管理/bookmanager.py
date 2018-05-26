from flask import Flask,render_template,request,flash, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired



app = Flask(__name__)

# 配置MySQL数据库
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:mysql@127.0.0.1:3306/flask_book_29'
# 是否追踪数据库的修改：不追踪，因为会明显消耗数据库的性能
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 配置密钥
app.secret_key = 'xiagjsijgloiqiehjoaihf'

db = SQLAlchemy(app)

class Author(db.Model):
    '''作者模型类'''
    __tablename__ = 'tb_authors'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    # 通过作者得到他的所有书籍，及通过书籍找到对应的作者
    books = db.relationship('Book',backref='author',lazy='dynamic')

class Book(db.Model):
    '''书籍类'''
    __tablename__='tb_books'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    # 外键
    author_id = db.Column(db.Integer, db.ForeignKey(Author.id))

class BookForm(FlaskForm):
    '''WTF'''
    author = StringField(u'作者：',validators=[DataRequired()])
    book = StringField(u'书名：',validators=[DataRequired()])
    submit = SubmitField(u'提交')


@app.route("/delete/author/<int:author_id>")
def delete_author(author_id):
    '''删除作者：同步删除作者对应的书籍， 需要先删除书籍在删除书籍对应的作者'''
    # 使用author_id查询出要删除的作者
    author = Author.query.get(author_id)

    # 判断作者是否存在
    if author:
        try:
            # 如果作者存在，先删除作者对应的书籍，在删除作者
            Book.query.filter(Book.author_id==author.id).delete()

            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

        # 同步到数据库
    else:
        flash(u'作者不存在')


    return redirect(url_for('index'))

@app.route('/delete/book/<int:book_id>')
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

    else:
        flash(u'作者不存在')
    return redirect(url_for('index'))




@app.route('/',methods=['GET','POST'])
def index():
    # 创建自定义表单对象
    book_form = BookForm()

    # 如果是POST表示正在新增数据
    if request.method=='POST':
        # 判断表单是否通过了验证
        if book_form.validate_on_submit():
            # 获取作者和书名
            author_name = book_form.author.data
            book_name = book_form.book.data

            # 查询作者
            author = Author.query.filter(Author.name==author_name).first()

            # 判断作者是否存在
            if author:
                # 查询书籍
                book = Book.query.filter(Book.name==book_name,Book.author_id==author.id).first()

                # 判断书籍是否存在
                if book:
                    flash(u'书名已经存在')
                else:
                    # 添加新的书籍到对应的作者
                    book = Book(name=book_name,author_id=author.id)

                    try:
                        db.session.add(book)
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        print(e)


            else:
                # 作者不存在
                # 添加新的作者
                author_new = Author(name=author_name)
                # 添加新的书籍
                book = Book(name=book_name)
                # 利用relationship里面的backref=author,直接将author和book建立关联，只需要提交一次
                book.author = author_new

                try:
                    db.session.add(book)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(e)

        else:
            flash(u'输入有误')

    # 数据查询
    authors = Author.query.all()

    return render_template('bookmanager.html',form=book_form,authors=authors)
    # return render_template('bookmanager.html', form=book_form, authors=authors)

if __name__ == '__main__':
    db.drop_all()
    db.create_all()

    # 生成数据
    au1 = Author(name='老王')
    au2 = Author(name='老尹')
    au3 = Author(name='老刘')
    # 把数据提交给用户会话
    db.session.add_all([au1, au2, au3])
    # 提交会话
    db.session.commit()
    bk1 = Book(name='老王回忆录', author_id=au1.id)
    bk2 = Book(name='我读书少，你别骗我', author_id=au1.id)
    bk3 = Book(name='如何才能让自己更骚', author_id=au2.id)
    bk4 = Book(name='怎样征服美丽少女', author_id=au3.id)
    bk5 = Book(name='如何征服英俊少男', author_id=au3.id)
    # 把数据提交给用户会话
    db.session.add_all([bk1, bk2, bk3, bk4, bk5])
    # 提交会话
    db.session.commit()

    app.run(debug=True)