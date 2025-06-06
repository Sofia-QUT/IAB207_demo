from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Destination, Comment
from .forms import DestinationForm, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename
#additional import:
from flask_login import login_required, current_user

import logging


destbp = Blueprint('destination', __name__, url_prefix='/destinations')

@destbp.route('/<id>')
def show(id):
    destination = db.session.scalar(db.select(Destination).where(Destination.id==id))
    # create the comment form
    form = CommentForm()    
    return render_template('destinations/show.html', destination=destination, form=form)

@destbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  # print('Method type: ', request.method)
  logging.basicConfig(level=logging.DEBUG)
  logging.debug(f"Method type: {request.method}")
  form = DestinationForm()
  if form.validate_on_submit():
    #call the function that checks and returns image
    db_file_path = check_upload_file(form)
    destination = Destination(name=form.name.data,description=form.description.data, 
    image=db_file_path,currency=form.currency.data)
    # add the object to the db session
    db.session.add(destination)
    # commit to the database
    db.session.commit()
    flash('Successfully created new travel destination', 'success')
    #Always end with redirect when form is valid
    return redirect(url_for('destination.create'))
  return render_template('destinations/create.html', form=form)

def check_upload_file(form):
    fp = form.image.data
    filename = secure_filename(fp.filename)

    BASE_PATH = os.path.dirname(__file__)
    upload_dir = os.path.join(BASE_PATH, 'static/image')
    os.makedirs(upload_dir, exist_ok=True)  # <-- always safe and avoids crash

    upload_path = os.path.join(upload_dir, filename)
    db_upload_path = '/static/image/' + filename

    fp.save(upload_path)
    return db_upload_path


@destbp.route('/<id>/comment', methods=['GET', 'POST'])  
@login_required
def comment(id):  
    form = CommentForm()  
    #get the destination object associated to the page and the comment
    destination = db.session.scalar(db.select(Destination).where(Destination.id==id))
    if form.validate_on_submit():  
      #read the comment from the form
      comment = Comment(text=form.text.data, destination=destination,
                        user=current_user) 
      #here the back-referencing works - comment.destination is set
      # and the link is created
      db.session.add(comment) 
      db.session.commit() 
      #flashing a message which needs to be handled by the html
      flash('Your comment has been added', 'success')  
      # print('Your comment has been added', 'success') 
    # using redirect sends a GET request to destination.show
    return redirect(url_for('destination.show', id=id))