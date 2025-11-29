from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Home page with hero, services preview, portfolio preview"""
    return render_template('index.html')

@main_bp.route('/portfolio')
def portfolio():
    """Full portfolio grid page"""
    # Portfolio projects data - you can edit this directly
    projects = [
        {
            'name': 'Equalitie',
            'url': 'https://equalitieofficial.com',  # Replace with actual URL
            'image': 'equalitie-preview.jpg',
            'technologies': ['HTML', 'CSS', 'JavaScript', 'Python', 'Flask']
        },
        {
            'name': 'Moore Quality Builders',
            'url': 'https://moore-qualitybuilders.com',
            'image': 'mqb-preview.jpg',
            'technologies': ['HTML', 'CSS', 'JavaScript', 'Python', 'Flask']
        },
        {
            'name': 'Gameboy Retreat',
            'url': 'https://gameboyretreat.com',
            'image': 'gbr-preview.jpg',
            'technologies': ['HTML', 'CSS', 'JavaScript', 'Python', 'Flask']
        },

        {
            'name': 'Sleepy Static',
            'url': 'https://sleepystatic.com',
            'image': 'sleepystatic-preview.jpg',
            'technologies': ['HTML', 'CSS', 'JavaScript', 'Python', 'Flask']
        }
    ]
    return render_template('portfolio.html', projects=projects)

@main_bp.route('/services')
def services():
    """Services and pricing page with competitor comparison"""
    return render_template('services.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')