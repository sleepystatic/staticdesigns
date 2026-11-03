from flask import Blueprint, render_template, abort, url_for, Response
from projects import PROJECTS, PAGESPEED_MEASURED
from pagespeed import pagespeed_meter

main_bp = Blueprint('main', __name__)
main_bp.add_app_template_global(pagespeed_meter)

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

@main_bp.route('/privacy')
def privacy():
    """Privacy policy, linked from the footer and the contact form"""
    return render_template('privacy.html')

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
