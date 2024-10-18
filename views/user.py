from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from sqlalchemy.sql import func

master = Blueprint('master', __name__)
from models import Following,User, db
from flask_login import login_required
@master.route('/profile.html')
@login_required
def profile():
    if 'username' in session:
        logged_in_user = User.query.filter(User.username == session['username']).first()
        if logged_in_user is None:
            return redirect( url_for('main.login'))
        total_following = Following.query.filter(Following.follower_id == logged_in_user.user_id).count()
        total_followers = Following.query.filter(Following.followed_id == logged_in_user.user_id).count()
        suggested_people = get_suggested_people(logged_in_user)
        return render_template('profile.html', following = total_following, followers = total_followers, suggested_people = suggested_people)
    else:
        flash("You are not logged in")
        return redirect( url_for('main.login'))
    
@master.route('/follow.html', methods=['POST'])
@login_required
def follow():
    user_id = request.form.get('user_id')
    current_user = User.query.filter(User.username == session['username']).first()
    if user_id:
        user_to_follow = User.query.get(user_id)
        if user_to_follow and current_user and user_to_follow != current_user:
            existing_follow = Following.query.filter_by(follower_id=current_user.user_id, followed_id=user_id).first()
            if not existing_follow:
                new_follow = Following(follower_id = current_user.user_id, followed_id = user_to_follow.user_id)
                db.session.add(new_follow)
                db.session.commit()
                flash(f"You are now following {user_to_follow.username}")
            else:
                flash(f'You are already following {user_to_follow.username}')
        else:
            flash("User not found or you cannot follow yourself")
    return redirect(url_for('master.profile'))


from sqlalchemy.orm import aliased

def get_suggested_people(logged_in_user, limit=5):
    # Create an alias for the User model
    FollowedUser = aliased(User)

    # Subquery to fetch the users that the logged-in user is following
    followed_subquery = db.session.query(Following.followed_id).filter(
        Following.follower_id == logged_in_user.user_id
    ).subquery()

    # Main query to fetch suggested users
    suggested_people = (
        db.session.query(User)
        .filter(
            User.user_id != logged_in_user.user_id,  # Exclude logged-in user
            ~User.user_id.in_(followed_subquery)     # Exclude already followed users
        )
        .order_by(func.random())
        .limit(limit)
    ).all()

    # Check if we need to fetch additional users
    if len(suggested_people) < limit:
        remaining_count = limit - len(suggested_people)
        
        # Fetch additional random users, still excluding the logged-in user
        additional_people = (
            db.session.query(User)
            .filter(
                User.user_id != logged_in_user.user_id,  # Exclude logged-in user
                ~User.user_id.in_(followed_subquery)     # Also exclude followed users
            )
            .order_by(func.random())
            .limit(remaining_count)
        ).all()

        # Combine the lists, avoiding duplicates
        suggested_people.extend(user for user in additional_people if user not in suggested_people)

    return suggested_people
