from flask import render_template, url_for, flash, redirect, request, Response
from App import app, db, bcrypt
from App.forms import RegistrationForm, LoginForm, PostForm,PatientForm
from App.models import Worker, Patient, Care_Post, Notice_Post
from flask_login import login_user, current_user, logout_user, login_required

from keras.models import load_model
from keras.preprocessing.image import img_to_array
import cv2
import numpy as np


@app.route("/")
@app.route("/home")
def home():
    posts = Care_Post.query.all()
    notice = Notice_Post.query.all()
    return render_template('home.html', posts=posts, notice=notice)


@app.route("/login", methods=['GET', 'POST'])
def login():
    notice = Notice_Post.query.all()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()

    if form.validate_on_submit():
        user = Worker.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if form.email.data == 'admin@gmail.com' and form.password.data == 'admin':
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('admin'))
            else:
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Pleach check again', 'danger')
    return render_template('login.html', title='Login', form=form, notice=notice)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        worker = Worker(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(worker)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/post/report", methods=['GET', 'POST'])
@login_required
def new_post():
    notice = Notice_Post.query.all()
    form = PostForm()
    if form.validate_on_submit():
        post = Care_Post(title=form.title.data, content=form.content.data, worker=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, notice=notice, legend='New Post')


@app.route("/post/<int:c_post_id>")
def c_post(c_post_id):
    notice = Notice_Post.query.all()
    post = Care_Post.query.get_or_404(c_post_id)
    return render_template('c_post.html', title=post.title,notice=notice, c_post=post)


@app.route("/post/<int:c_post_id>/update", methods=['GET', 'POST'])
def update_c_post(c_post_id):
    notice = Notice_Post.query.all()
    post = Care_Post.query.get_or_404(c_post_id)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been update!', 'success')
        return redirect(url_for('c_post', c_post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form,notice=notice, legend='Update Post')\


@app.route("/post/<int:c_post_id>/delete", methods=['POST'])
def delete_c_post(c_post_id):
    post = Care_Post.query.get_or_404(c_post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/manage/patient", methods=['GET', 'POST'])
@login_required
def patient_manage():
    notice = Notice_Post.query.all()
    patient = Patient.query.all()
    form = PatientForm()
    if form.validate_on_submit():
        post = Patient(name=form.name.data, sex=form.sex.data, age=form.age.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('patient_manage'))
    return render_template('manage_patient.html', notice=notice, patient=patient, form=form, title='Patient Management', legend='Register Patient')


@app.route("/manage/patient_delete", methods=['GET', 'POST'])
@login_required
def patient_delete():
    id = request.args.get('id')
    patient = Patient.query.filter_by(id=id).first()
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('patient_manage'))
    return render_template('manage_patient.html', title='Delete Patient List')


@app.route("/admin")
def admin():
    notice = Notice_Post.query.all()
    return render_template('admin.html', title='Administrator Only', notice=notice)


@app.route("/admin/notice/new", methods=['GET', 'POST'])
def notice_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Notice_Post(title=form.title.data, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('admin'))
    return render_template('notice_post.html', form=form, legend='Notice Post')


@app.route("/admin/notice/<int:n_post_id>")
def n_post(n_post_id):
    post = Notice_Post.query.get_or_404(n_post_id)
    return render_template('n_post.html', title=post.title, n_post=post)


@app.route("/admin/notice/<int:n_post_id>/update", methods=['GET', 'POST'])
def update_n_post(n_post_id):
    post = Notice_Post.query.get_or_404(n_post_id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been update!', 'success')
        return redirect(url_for('admin', n_post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('notice_post.html', title='Update Notice', form=form, legend='Update Notice')


@app.route("/admin/notice/<int:n_post_id>/delete", methods=['POST'])
def delete_n_post(n_post_id):
    post = Notice_Post.query.get_or_404(n_post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('admin'))


@app.route("/manage/staff", methods=['GET', 'POST'])
def worker_manage():
    worker = Worker.query.all()
    return render_template('manage_worker.html', worker=worker)


@app.route("/manage/worker_delete", methods=['GET', 'POST'])
def worker_delete():
    id = request.args.get('id')
    worker = Worker.query.filter_by(id=id).first()
    db.session.delete(worker)
    db.session.commit()
    return redirect(url_for('worker_manage'))


@app.route("/emotioncheck")
def emotioncheck():
    notice = Notice_Post.query.all()
    return render_template('emotioncheck.html', notice=notice, title='Emotion Check')


@app.route('/emotioncheck/video_feed')
def video_feed():
    # set local or full pathname for the haarcascades and vgg.h5 files
    face_classifier = cv2.CascadeClassifier('/Users/alex/Documents/GitHub/Intelligent-Care-System/App/model/haarcascade_frontalface_default.xml')
    classifier = load_model('/Users/alex/Documents/GitHub/Intelligent-Care-System/App/model/Emotion_little_vgg_epoch25.h5')

    def gen():
        cap = cv2.VideoCapture(0)

        # set variable for falling check
        arrHeights = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        count = 0
        fallen = False

        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray,1.3,5)

            for (x, y, w, h) in faces:

                # Falling check
                arrHeights.append(y)  # append array of y coordinates for each face
                size = len(arrHeights)

                # loop through the last 10 x coordinates to check for downward trend
                for s in range(size - 11, size - 1):
                    if arrHeights[s] > arrHeights[s - 1]:
                        count = count + 1
                    else:
                        count = 0
                        fallen = False
                        # if user comes back into screen, the fallen message should disappear

                    # make sure that the fall is large/fast enough and the user wan't just moving their head downward
                    if count >= 6 and arrHeights[s] - arrHeights[s - 5] >= 175:
                        fallen = True
                        break

                # draw rectangle
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
                roi = roi_gray.astype('float')/255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)

                preds = classifier.predict(roi)
                class_labels = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']
                label = class_labels[np.argmax(preds[0])]
                print(label)

                if fallen:
                    cv2.putText(frame, 'FALLEN', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                else:
                    cv2.putText(frame, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 3)
                break
                
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(jpeg) + b'\r\n\r\n')
        cap.release()
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')