from flask import Flask, render_template, url_for, request, redirect, flash, send_from_directory
from flask_security import login_required

from .models import db, Content
from .forms import ContentForm
from .utils import find_content, OpenGraphImage

fbapp = Flask(__name__)

# Config options - Make sure you created a 'config.py' file.
fbapp.config.from_object('config')
# app.config.from_envvar('YOURAPPLICATION_SETTINGS')

@fbapp.route('/')
@fbapp.route('/index')
def index():
    description = "Toi, tu sais comment utiliser la console ! Jamais à court d'idées pour réaliser ton objectif, tu es déterminé-e et persévérant-e. Tes amis disent d'ailleurs volontiers que tu as du caractère et que tu ne te laisses pas marcher sur les pieds. Un peu hacker sur les bords, tu aimes trouver des solutions à tout problème. N'aurais-tu pas un petit problème d'autorité ? ;-)"
    return render_template('index.html', page_title='Le test ultime !',
                                         user_image='static/img/profile.png',
                                         user_name='Julio',
                                         fb_app_id=fbapp.config['FB_APP_ID'],
                                         blur=True,
                                         description=description)

@fbapp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/index.html')

@fbapp.route('/dashboard/contents/new', methods=['GET', 'POST'])
@login_required
def new_content():
    form = ContentForm()
    content = Content('A description', 'Male')
    if form.validate_on_submit():
        c = Content(form.description.data, form.sex.data)
        db.session.add(c)
        db.session.commit()
        flash('Une nouvelle description a été ajoutée avec succès ! Description : {} Sexe : {}'.format(
            form.description.data, form.sex.data
        ))
        return redirect(url_for('new_content', method='GET'))

    return render_template('contents/form.html', \
                           path=url_for('new_content'), \
                           title='Nouvelle description', \
                           method='POST',
                           form=form,
                           description=content.description,
                           sex=content.sex)

@fbapp.route('/dashboard/contents')
@login_required
def contents():
    all_contents = Content.query.all()
    total = len(all_contents)
    return render_template('contents/index.html', contents=all_contents, total=total)

@fbapp.route('/dashboard/contents/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def update_content(id):
    content = Content.query.get(id)
    form = ContentForm()
    if form.validate_on_submit():
        content.description = form.description.data
        content.sex = form.sex.data
        db.session.add(content)
        db.session.commit()
        flash('La description a bien été modifiée ! Description : {} Sexe : {}'.format(
            form.description.data, form.sex.data
        ))
        return redirect(url_for('contents'))

    return render_template('contents/form.html',
                           path=url_for('update_content', id=id),
                           title='Mise à jour',
                           method='POST',
                           form=form,
                           description=content.description,
                           sex=content.sex)

@fbapp.route('/dashboard/contents/<int:id>/delete')
@login_required
def delete_content(id):
    content = Content.query.get(id)
    db.session.delete(content)
    db.session.commit()
    if Content.query.get(id) is None:
        flash('La description a bien été supprimée')
    else:
        flash("Une erreur s'est produite. Merci de recommencer.")
    return redirect(url_for('contents'))

###############################
########## Test ###############
###############################

@fbapp.route('/result')
def result():
    content = find_content(Content.GENDER_FEMALE)
    description = content.description
    first_name = request.args['first_name']
    uid = request.args['id']
    base_url = fbapp.config['BASE_URL']
    profile_pic = 'http://graph.facebook.com/' + uid + '/picture?type=large'
    fb_img = OpenGraphImage(first_name, profile_pic, uid, description)
    og_image = base_url + fb_img.location

    return render_template('result.html', page_title='Voici qui je suis vraiment !', \
                                   user_image=fb_img.cover_location, \
                                   user_name=first_name, \
                                   fb_app_id=fbapp.config['FB_APP_ID'], \
                                   description=description, \
                                   og_image=og_image, \
                                   og_url=base_url, \
                                   og_description='Toi aussi, fais le test !')
