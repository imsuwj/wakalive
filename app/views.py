from app import app, models, login_manager, lecloud,leancloud,re
from flask import flash, render_template, redirect, url_for, session, abort, request
from flask.ext.login import current_user, login_required, login_user, logout_user

@login_manager.user_loader
def load_user(id):
    user = models.User.get(id)
    return user


@login_manager.unauthorized_handler
def unauthorized():
    flash('请先登录.')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        [user, flash_words] = models.User.login(
            request.form['email'], request.form['password'])
        flash(flash_words)
        if user:
            login_user(user)
            return redirect(url_for('manage'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['email'] != '' and request.form['password'] != '':
            if request.form['password'] != request.form['confirm_password']:
                flash('两次输入的密码不匹配.')
            elif models.User.add(request.form['email'], request.form['password'], request.form['nickname']):
                flash('你已成功注册.')
                return redirect(url_for('login'))
        else:
            flash('信息不完整.')
    return render_template('register.html')


@app.route('/')
def index():
    live_list = models.Live.list(id=None, uid=None, aid=None)
    return render_template('index.html', live_list=live_list)


@app.route('/manage')
@login_required
def manage():
    live = current_user.lives.first()
    if live is None:
        live_info = None
    else:
        live_info = lecloud.queryLive(live.aid)
        live_info['liveId'] = live.id
        live_info['createTime'] = fomart_date(live_info['createTime'])
        live_info['endTime'] = fomart_date(live_info['endTime'])
    return render_template('manage.html', live_info=live_info)


@app.route('/manage/user-update', methods=['POST'])
@login_required
def user_update():
    form_dict = {
        'id': current_user.id
    }
    if request.form['password'] != '':
        form_dict['password'] = request.form['password']
    if request.form['nickname'] != '':
        form_dict['nickname'] = request.form['nickname']
    models.User.update(form_dict)
    flash('个人信息更改成功!')
    return redirect(url_for('manage'))


@app.route('/live/create', methods=['POST'])
@login_required
def live_create():
    if (not current_user.lives.first()) and current_user.is_passed():
        form_dict = {
            'activityName': request.form['activity_name'],
            'description': request.form['description']
        }
        form_dict['codeRateTypes'] = ','.join(sorted(request.form.getlist(
            'code_rate_types'), reverse=True)) if request.form.getlist('code_rate_types') else '99'
        form_dict['codeRateTypes'] += ',13'
        activityId = lecloud.createLive(form_dict)
        room_id = leancloud.createRoom(request.form['activity_name'])
        models.Live.add(uid=current_user.id, aid=activityId,
                        name=form_dict['activityName'],roomid = room_id)
        flash('直播创建成功.')
    return redirect(url_for('manage'))


@app.route('/live/update', methods=['POST'])
@login_required
def live_update():
    if current_user.is_passed():
        form_dict = {
            'activityId': request.form['activity_id']
        }
        if request.form['activity_name'] != '':
            form_dict['activityName'] = request.form['activity_name']
            models.Live.update(current_user.lives.first().id,name =
                               request.form['activity_name'])
        if request.form['description'] != '':
            form_dict['description'] = request.form['description']
        if request.form.getlist('code_rate_types'):
            form_dict['codeRateTypes'] = ','.join(sorted(request.form.getlist(
                'code_rate_types'), reverse=True))
            form_dict['codeRateTypes'] += ',13'
        if request.form['add_live_time']:
            form_dict['add_live_time'] = True
        lecloud.modifyLive(form_dict)
        flash('直播设置更改成功.')
    return redirect(url_for('manage'))


@app.route('/live/cancel', methods=['POST'])
@login_required
def live_cancel():
    if current_user.is_passed():
        models.Live.delete(request.form['live_id'])
        lecloud.cancelLive(request.form['activity_id'])
        flash('直播取消成功.')
    return redirect(url_for('manage'))


@app.route('/live/stream/<id>')
@login_required
def live_stream(id):
    if current_user.is_passed():
        live = models.Live.list(id=id)
        url = lecloud.getPushUrl(live.aid)
        return url
    return redirect(url_for('manage'))


@app.route('/live/<id>')
def live(id):
    live = models.Live.list(id=id)
    if live.roomid == '':
        models.Live.update(id,roomid=leancloud.createRoom(live.name))
    live_info = lecloud.queryLive(live.aid)
    nickname = live.user.nickname
    print(live.roomid)
    return render_template('live.html', live=live_info, nickname=nickname, leancloud_appid=app.config['LEANCLOUD_APPID'], leancloud_appkey=app.config['LEANCLOUD_APPKEY'], leancloud_roomid=live.roomid)


@app.route('/admin')
@login_required
def admin():
    if current_user.is_admin():
        user_list = models.User.list()
        return render_template('admin.html', user_list=user_list)
    else:
        return redirect(url_for('manage'))


@app.route('/admin/delete-user', methods=['POST'])
@login_required
def admin_delete_user():
    if current_user.is_admin():
        if models.User.get(request.form['userid']).lives.first() is not None:
            models.Live.delete(models.User.get(
                request.form['userid']).lives.first().id)
            lecloud.cancelLive(request.form['activity_id'])
        models.User.delete(request.form['userid'])
    else:
        flash('权限不足!')
    return redirect(url_for('admin'))


@app.route('/admin/pass-user', methods=['POST'])
@login_required
def admin_pass_user():
    if current_user.is_admin():
        user_dict = {
            'id': request.form['userid'],
            'role': 1
        }
        models.User.update(user_dict)
    else:
        flash('权限不足!')
    return redirect(url_for('admin'))


@app.route('/admin/delete-live', methods=['POST'])
@login_required
def admin_delete_live():
    if current_user.is_admin():
        models.Live.delete(request.form['live_id'])
        lecloud.cancelLive(request.form['activity_id'])
    else:
        flash('权限不足!')
    return redirect(url_for('admin'))

'''
Some method
'''
def fomart_date(str_time):
    s = re.sub('(..)', r'/\1', str_time)
    return s[1:3]+s[4:]
