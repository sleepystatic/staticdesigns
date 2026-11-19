import os

from flask import Blueprint, render_template, abort, request, url_for, Response, current_app, send_from_directory
from projects import PROJECTS, CATEGORIES, PAGESPEED_MEASURED
from pagespeed import pagespeed_meter

main_bp = Blueprint('main', __name__)
main_bp.add_app_template_global(pagespeed_meter)
main_bp.add_app_template_global(CATEGORIES, 'project_categories')

# Newest first. image is the card picture on /blog in static/images; template is the post's page in templates/blog.
BLOG_POSTS = [
    {
        'slug': 'how-to-optimize-your-pagespeed-score',
        'title': "How to Optimize Your Website's PageSpeed Score",
        'description': "What Google's PageSpeed score measures, what its five numbers mean, and the fixes that raise it, with real examples from our own site.",
        'date': 'November 13, 2026',
        'read_time': '8 min read',
        'image': 'blog-pagespeed-scores.webp',
        'template': 'blog/how-to-optimize-your-pagespeed-score.html'
    },
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
    """Portfolio grid, optionally filtered to one category: /portfolio?type=software"""
    active = request.args.get('type')
    if active not in CATEGORIES:
        active = None
    shown = [p for p in PROJECTS if active is None or active in p['categories']]
    return render_template('portfolio.html', projects=shown, active=active)

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

# The About page photo. It appears as soon as this file exists (made by `scripts/optimize_images.py headshot`);
# until then the page shows initials in its place.
HEADSHOT = 'images/headshot.webp'

@main_bp.route('/about')
def about():
    """About page"""
    has_headshot = os.path.isfile(os.path.join(current_app.static_folder, HEADSHOT))
    return render_template('about.html', headshot=HEADSHOT if has_headshot else None)

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

@main_bp.route('/privacy')
def privacy():
    """Privacy policy, linked from the footer and the contact form"""
    return render_template('privacy.html')

@main_bp.route('/favicon.ico')
def favicon():
    """The {S} icon at the address browsers and other tools check when a page doesn't name its icon"""
    return send_from_directory(os.path.join(current_app.static_folder, 'images'), 'favicon.ico', mimetype='image/x-icon')

@main_bp.route('/robots.txt')
def robots():
    """Lets search engines crawl everything and points them to the sitemap"""
    return Response(render_template('robots.txt'), mimetype='text/plain')

@main_bp.route('/sitemap.xml')
def sitemap():
    """Every public page, so search engines find each project page and blog post"""
    paths = [url_for('main.home'), url_for('main.portfolio')]
    paths += [url_for('main.project', slug=p['slug']) for p in PROJECTS]
    paths += [url_for('main.services'), url_for('main.about'), url_for('main.blog')]
    paths += [url_for('main.blog_post', slug=p['slug']) for p in BLOG_POSTS]
    paths += [url_for('contact.contact'), url_for('main.privacy')]
    return Response(render_template('sitemap.xml', paths=paths), mimetype='application/xml')
