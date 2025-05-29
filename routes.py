from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from models import User, Idea, Bid, Message, Transaction
from ai_service import analyze_and_rank_idea
import json

def register_routes(app):
    
    @app.route('/')
    def index():
        # Get featured ideas (highest rated by AI)
        featured_ideas = Idea.query.filter_by(is_sold=False).order_by(Idea.ai_rating.desc()).limit(6).all()
        
        # Get recent ideas
        recent_ideas = Idea.query.filter_by(is_sold=False).order_by(Idea.created_at.desc()).limit(6).all()
        
        return render_template('index.html', featured_ideas=featured_ideas, recent_ideas=recent_ideas)

    # Authentication routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
        
        return render_template('auth/login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            is_seller = 'is_seller' in request.form
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return render_template('auth/register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('auth/register.html')
            
            # Create new user
            user = User(username=username, email=email, is_seller=is_seller)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('index'))
        
        return render_template('auth/register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('index'))

    # Idea routes
    @app.route('/submit', methods=['GET', 'POST'])
    @login_required
    def submit_idea():
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            category = request.form['category']
            price = float(request.form['price'])
            
            # Create new idea
            idea = Idea(
                title=title,
                description=description,
                category=category,
                price=price,
                user_id=current_user.id
            )
            
            # Analyze with AI
            try:
                ai_analysis = analyze_and_rank_idea(title, description, category)
                idea.ai_rating = ai_analysis['rating']
                idea.ai_tags = json.dumps(ai_analysis['tags'])
                idea.ai_cluster = ai_analysis['cluster']
            except Exception as e:
                app.logger.error(f"AI analysis failed: {e}")
                # Set default values if AI fails
                idea.ai_rating = 5.0
                idea.ai_tags = json.dumps([])
                idea.ai_cluster = "General"
            
            db.session.add(idea)
            db.session.commit()
            
            flash('Idea submitted successfully!', 'success')
            return redirect(url_for('idea_detail', id=idea.id))
        
        return render_template('ideas/submit.html')

    @app.route('/browse')
    def browse_ideas():
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort', 'recent')
        
        query = Idea.query.filter_by(is_sold=False)
        
        # Apply filters
        if category:
            query = query.filter_by(category=category)
        
        if search:
            query = query.filter(Idea.title.contains(search) | Idea.description.contains(search))
        
        # Apply sorting
        if sort_by == 'rating':
            query = query.order_by(Idea.ai_rating.desc())
        elif sort_by == 'price_low':
            query = query.order_by(Idea.price.asc())
        elif sort_by == 'price_high':
            query = query.order_by(Idea.price.desc())
        else:  # recent
            query = query.order_by(Idea.created_at.desc())
        
        ideas = query.paginate(page=page, per_page=12, error_out=False)
        
        return render_template('ideas/browse.html', ideas=ideas, 
                             current_category=category, current_search=search, current_sort=sort_by)

    @app.route('/idea/<int:id>')
    def idea_detail(id):
        idea = Idea.query.get_or_404(id)
        bids = Bid.query.filter_by(idea_id=id).order_by(Bid.amount.desc()).all()
        
        # Parse AI tags
        ai_tags = []
        if idea.ai_tags:
            try:
                ai_tags = json.loads(idea.ai_tags)
            except:
                ai_tags = []
        
        return render_template('ideas/detail.html', idea=idea, bids=bids, ai_tags=ai_tags)

    # Bidding routes
    @app.route('/bid/<int:idea_id>', methods=['GET', 'POST'])
    @login_required
    def place_bid(idea_id):
        idea = Idea.query.get_or_404(idea_id)
        
        if idea.user_id == current_user.id:
            flash("You cannot bid on your own idea", 'error')
            return redirect(url_for('idea_detail', id=idea_id))
        
        if idea.is_sold:
            flash("This idea has already been sold", 'error')
            return redirect(url_for('idea_detail', id=idea_id))
        
        if request.method == 'POST':
            amount = float(request.form['amount'])
            message = request.form.get('message', '')
            
            # Check if bid is higher than current highest
            highest_bid = idea.get_highest_bid()
            if highest_bid and amount <= highest_bid.amount:
                flash(f"Your bid must be higher than ${highest_bid.amount:.2f}", 'error')
                return render_template('bidding/place_bid.html', idea=idea)
            
            if amount < idea.price:
                flash(f"Your bid must be at least ${idea.price:.2f}", 'error')
                return render_template('bidding/place_bid.html', idea=idea)
            
            # Create bid
            bid = Bid(
                amount=amount,
                message=message,
                user_id=current_user.id,
                idea_id=idea_id
            )
            
            db.session.add(bid)
            db.session.commit()
            
            flash('Bid placed successfully!', 'success')
            return redirect(url_for('idea_detail', id=idea_id))
        
        return render_template('bidding/place_bid.html', idea=idea)

    @app.route('/accept_bid/<int:bid_id>')
    @login_required
    def accept_bid(bid_id):
        bid = Bid.query.get_or_404(bid_id)
        idea = bid.idea
        
        if idea.user_id != current_user.id:
            flash("You can only accept bids on your own ideas", 'error')
            return redirect(url_for('idea_detail', id=idea.id))
        
        if idea.is_sold:
            flash("This idea has already been sold", 'error')
            return redirect(url_for('idea_detail', id=idea.id))
        
        # Mark bid as accepted and idea as sold
        bid.is_accepted = True
        idea.is_sold = True
        
        # Create transaction record
        transaction = Transaction(
            amount=bid.amount,
            status='completed',
            buyer_id=bid.user_id,
            seller_id=current_user.id,
            idea_id=idea.id,
            bid_id=bid.id
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Bid accepted! You sold "{idea.title}" for ${bid.amount:.2f}', 'success')
        return redirect(url_for('dashboard'))

    # Profile routes
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get user's ideas
        user_ideas = Idea.query.filter_by(user_id=current_user.id).order_by(Idea.created_at.desc()).all()
        
        # Get user's bids
        user_bids = Bid.query.filter_by(user_id=current_user.id).order_by(Bid.created_at.desc()).all()
        
        # Get user's transactions
        purchases = Transaction.query.filter_by(buyer_id=current_user.id).order_by(Transaction.created_at.desc()).all()
        sales = Transaction.query.filter_by(seller_id=current_user.id).order_by(Transaction.created_at.desc()).all()
        
        return render_template('profile/dashboard.html', 
                             user_ideas=user_ideas, 
                             user_bids=user_bids,
                             purchases=purchases,
                             sales=sales)

    @app.route('/profile/<username>')
    def user_profile(username):
        user = User.query.filter_by(username=username).first_or_404()
        user_ideas = Idea.query.filter_by(user_id=user.id, is_sold=False).order_by(Idea.created_at.desc()).limit(10).all()
        
        return render_template('profile/public.html', user=user, user_ideas=user_ideas)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
