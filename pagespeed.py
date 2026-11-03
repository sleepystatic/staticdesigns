"""Builds the PageSpeed meter (templates/macros.html) from a project's `pagespeed` numbers in projects.py.

The meter copies Google PageSpeed Insights (Desktop tab): the Performance score in the middle, ringed by its
five metrics. Each metric's arc is as long as its weight in the score and filled as far as that metric scores.
"""
import math
from urllib.parse import quote

from projects import PAGESPEED_MIN_SHOWN

# Lighthouse's desktop scoring. A metric scores 0.9 at p10 and 0.5 at the median, in the units projects.py uses.
# key, abbreviation, name, weight in the Performance score (%), p10, median, unit
METRICS = (
    ('fcp', 'FCP', 'First Contentful Paint', 10, 0.934, 1.6, 's'),
    ('lcp', 'LCP', 'Largest Contentful Paint', 25, 1.2, 2.4, 's'),
    ('tbt', 'TBT', 'Total Blocking Time', 30, 150, 350, 'ms'),
    ('cls', 'CLS', 'Cumulative Layout Shift', 25, 0.1, 0.25, ''),
    ('si', 'SI', 'Speed Index', 10, 1.311, 2.3, 's'),
)

# Ring geometry in SVG units; the macro's viewBox is 120x120 centered on (60, 60).
CENTER = 60
RING_RADIUS = 40
LABEL_RADIUS = 52
GAP_DEGREES = 3


def metric_score(value, p10, median):
    """Lighthouse's log-normal curve: 1 at zero, 0.9 at p10, 0.5 at the median, falling toward 0 after."""
    if value <= 0:
        return 1.0
    x = math.log(value / median) * 0.9061938024368232 / math.log(median / p10)
    score = (1 - math.erf(x)) / 2
    if value <= p10:
        score = max(0.9, min(1.0, score))
        score += 0.05 * (score - 0.9)  # Lighthouse's boost that makes a perfect 1 reachable
    elif value <= median:
        score = max(0.5, min(0.8999999999999999, score))
    else:
        score = max(0.0, min(0.49999999999999994, score))
    return math.floor(score * 100) / 100


def rating(score):
    """Google's colors: 0.9 and up is green, 0.5 and up is orange, anything lower is red."""
    if score >= 0.9:
        return 'pass'
    if score >= 0.5:
        return 'average'
    return 'fail'


def point(degrees, radius):
    """A point on a circle around the center, measured clockwise from 12 o'clock."""
    radians = math.radians(degrees)
    return round(CENTER + radius * math.sin(radians), 2), round(CENTER - radius * math.cos(radians), 2)


def arc(start, end):
    """SVG path for a clockwise arc of the ring between two angles."""
    x1, y1 = point(start, RING_RADIUS)
    x2, y2 = point(end, RING_RADIUS)
    large = 1 if end - start > 180 else 0
    return f'M{x1} {y1}A{RING_RADIUS} {RING_RADIUS} 0 {large} 1 {x2} {y2}'


def display(value, unit):
    """Formats a metric the way PageSpeed Insights shows it: 1.2 s, 30 ms, 0.002."""
    if unit == 's':
        return f'{value:.1f} s'
    if unit == 'ms':
        return f'{value:,.0f} ms'
    return f'{value:g}'


def pagespeed_meter(pagespeed, url=None):
    """Everything the meter macro draws, or None when there's no result or it scores below PAGESPEED_MIN_SHOWN."""
    if not pagespeed or pagespeed['score'] < PAGESPEED_MIN_SHOWN:
        return None
    segments = []
    start = 0
    for key, abbr, name, weight, p10, median, unit in METRICS:
        value = pagespeed[key]
        score = metric_score(value, p10, median)
        end = start + weight * 3.6
        first, last = start + GAP_DEGREES / 2, end - GAP_DEGREES / 2
        filled = first + (last - first) * score
        label_x, label_y = point((start + end) / 2, LABEL_RADIUS)
        segments.append({
            'abbr': abbr,
            'name': name,
            'value': display(value, unit),
            'rating': rating(score),
            'track': arc(first, last),
            'fill': arc(first, filled) if score > 0 else None,
            'label_x': label_x,
            'label_y': label_y,
        })
        start = end
    return {
        'score': pagespeed['score'],
        'rating': rating(pagespeed['score'] / 100),
        'segments': segments,
        'report_url': f'https://pagespeed.web.dev/analysis?url={quote(url, safe="")}&form_factor=desktop' if url else None,
    }
