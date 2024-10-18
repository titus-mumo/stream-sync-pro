from flask import Blueprint, session, request, flash, url_for, render_template
from flask_login import login_required
from models import Following, User, db
follow = Blueprint('follow', __name__)
from sqlalchemy.orm import aliased
from sqlalchemy import case

reciprocal = aliased(Following)

@follow.route('/followers.html')
@login_required
def followers():
    username = session['username']
    current_user = User.query.filter(User.username == username).first()
    #Annotate followers to include username
    followers = (db.session.query(Following, User.username,
                                case((reciprocal.follower_id.isnot(None), True), else_=False).label('is_following_back'))
                .join(User, User.user_id == Following.follower_id)  # Join User model to get the username
                .outerjoin(reciprocal, 
                            (reciprocal.follower_id == current_user.user_id) & 
                            (reciprocal.followed_id == Following.follower_id))  # Self-join to check if you're following back
                .filter(Following.followed_id == current_user.user_id)  # Filter to get the followers of the current user
                ).all()

    return render_template('followers.html', followers = followers)



