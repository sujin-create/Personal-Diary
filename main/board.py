
from main import *
from flask import Blueprint,send_from_directory

from string import digits, ascii_uppercase, ascii_lowercase
import random

blueprint = Blueprint("board",__name__,url_prefix = "/board")


@blueprint.route("/up_image",methods=["POST"])
def up_image():
    if request.method == "POST":
        file = request.files["image"]
        if file and file_ch(file.filename):
            filename = "{}.jpg".format(generator())
            savefilepath = os.path.join(app.config["BOARD_IMAGE_PATH"],filename)
            file.save(savefilepath)
            return url_for("board.images",filename=filename)

@blueprint.route("/images/<filename>")
def images(filename):
    return send_from_directory(app.config["BOARD_IMAGE_PATH"],filename)
#독립적인 폴더에 저장해서 접근


@blueprint.route("/list")
@login_required
def lists():
    #페이지넘버값
    page = request.args.get("page",default=1, type = int)
    #한 페이지당 게시물을 몇개출력할지 -> 10개출력
    limit = request.args.get("list",10,type=int)

    board = mongo.db.board
    datas = board.find({}).skip((page-1)*limit).limit(limit).sort("time",-1)
    
    #페이지 블록처리코드 구현
    #페이지 번호 넣기
    tot_count = board.find({}).count()
    #마지막 페이지 넘버
    last_page_num = math.ceil(tot_count/limit)
    block_size = 1
    block_num = int((page-1)/block_size)#현재 블록 위치
    block_start = int((block_size * block_num)+1)
    block_last = math.ceil(block_start + (block_size-1))
    
    return render_template("list.html", datas=datas,limit = limit,page=page,block_start = block_start,
                           block_last = block_last, last_page_num = last_page_num, title = "Diary 항목", )



@blueprint.route("/view/<idx>")
@login_required
def board_view(idx):
    if idx is not None:
        page = request.args.get("page")
        board = mongo.db.board
        # data = board.find_one({"_id" : ObjectId(idx)})
        data = board.find_one_and_update({"_id" : ObjectId(idx)},{"$inc" : {"view":1}}, return_document=True)
        if data is not None:
            result = {
                "id" : data.get("_id"),
                "keyw" : data.get("keyw"),
                "title" : data.get("title"),
                "contents" : data.get("contents"),
                "time" : data.get("time"),
                "view" : data.get("view"),
                "writer_id" : data.get("writer_id","")

            }

            return render_template("view.html",result = result,page=page,title="게시글보기")


    return abort(404)

@blueprint.route("/write",methods = ["GET","POST"])
@login_required
def board_write():
    if request.method == "POST":
        keyw = request.form.get("keyw")
        title = request.form.get("title")
        contents = request.form.get("contents")
        
        utc_time = round(datetime.utcnow().timestamp()*1000)
        board = mongo.db.board
        post = {
            "keyw" : keyw, "title" : title, "contents" : contents,
            "time" : utc_time, "view" : 0,
            "writer_id" : session.get("id"),
        }
        x = board.insert_one(post)
        print(x.inserted_id)
        return redirect(url_for("board.board_view",idx = x.inserted_id))#인자로 id를 넘겨줘야함
    else:
        return render_template("write.html",title="게시글 작성")



@blueprint.route("/edit/<idx>", methods = ["GET","POST"])
def board_edit(idx):
    if request.method == "GET":
        board = mongo.db.board
        data= board.find_one({"_id":ObjectId(idx)})
        if data is None:
            flash("게시물이 존재하지 않습니다")
            return redirect(url_for("board.lists"))
        else:
            if session.get("id") == data.get("writer_id"):
                return render_template("edit.html",data=data,title="글 수정")
            else:
                flash("글 수정 권한이 없습니다")
                return redirect(url_for("board.lists"))
    else:
        title = request.form.get("title")
        keyw = request.form.get("keyw")
        contents = request.form.get("contents")
        board = mongo.db.board
        data= board.find_one({"_id":ObjectId(idx)})
        if session.get("id") == data.get("writer_id"):
            board.update_one({"_id":ObjectId(idx)},{"$set" : {
                "title" : title,
                "contents" : contents,
                "keyw" : keyw,
                }
            })
            flash("수정이 완료되었습니다")
            return redirect(url_for("board.board_view",idx=idx))
        else:
            flash("글 수정 권한이 없습니다")
            return redirect(url_for("board.lists"))

@blueprint.route("/delete/<idx>")
def board_delete(idx):
    board = mongo.db.board
    data= board.find_one({"_id":ObjectId(idx)})
    if session.get("id") == data.get("writer_id"):
        board.delete_one({"_id" : ObjectId(idx)})
        flash("삭제완료")
    else:
        flash("삭제할 수 없음")
    return redirect(url_for("board.lists"))
