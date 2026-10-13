from flask import Blueprint, render_template, abort
from projects import PROJECTS, PAGESPEED_MEASURED

main_bp = Blueprint('main', __name__)

BLOG_POSTS = [
    {
        'slug': 'why-custom-coded-websites-beat-wordpress',
        'title': 'Why Custom-Coded Websites Beat WordPress, Wix, Squarespace, and GoDaddy',
        'description': 'Discover why a custom-coded website outperforms page builders in speed, SEO, security, and long-term value for your business.',
        'date': 'August 26, 2026',
        'read_time': '6 min read',
        'image': 'blog-custom-vs-builders.jpg',
        'template': 'blog/why-custom-coded-websites-beat-wordpress.html'
    },
]

@main_bp.route('/')
def home():
    """Home page with hero, services preview, portfolio preview"""
    return render_template('index.html', projects=PROJECTS)

@main_bp.route('/portfolio')
def portfolio():
    """Full portfolio grid page"""
    return render_template('portfolio.html', projects=PROJECTS)

@main_bp.route('/portfolio/<slug>')
def project(slug):
    """Single project page with screenshots, write-up, and links to the neighboring projects"""
    index = next((i for i, p in enumerate(PROJECTS) if p['slug'] == slug), None)
    if index is None:
        abort(404)
    return render_template(
        'project.html',
        project=PROJECTS[index],
        prev_project=PROJECTS[index - 1],
        next_project=PROJECTS[(index + 1) % len(PROJECTS)],
        measured=PAGESPEED_MEASURED,
    )

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