from flask import Blueprint, render_template, abort

main_bp = Blueprint('main', __name__)

BLOG_POSTS = [
    {
        'slug': 'why-custom-coded-websites-beat-wordpress',
        'title': 'Why Custom-Coded Websites Beat WordPress, Wix, Squarespace, and GoDaddy',
        'description': 'Discover why a hand-coded website outperforms page builders in speed, SEO, security, and long-term value for your business.',
        'date': 'August 26, 2026',
        'read_time': '6 min read',
        'image': 'blog-custom-vs-builders.jpg',
        'template': 'blog/why-custom-coded-websites-beat-wordpress.html'
    },
]

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
        },

        {
            'name': 'Pixel Flip',
            'url': 'https://pixelflip.app/',
            'image': 'pixelflip-preview.jpg',
            'technologies': ['React', 'NodeJS', 'JavaScript', 'Python', 'HTML', 'CSS']
        },

        {
            'name': 'Amor Frames',
            'url': 'https://amorframesbyluv.com/',
            'image': 'af-preview.jpg',
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

@main_bp.route('/blog')
def blog():
    """Blog listing page"""
    return render_template('blog.html', posts=BLOG_POSTS)

@main_bp.route('/blog/<slug>')
def blog_post(slug):
    """Individual blog post"""
    post = next((p for p in BLOG_POSTS if p['slug'] == slug), None)
    if not post:
        abort(404)
    return render_template(post['template'], post=post)