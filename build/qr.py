"""Generate the QR code for the live map, plus a ready-to-print card.

Written for flyers and for signs taped to poles on the morning: nobody types a
URL off a piece of paper.

Error correction is Q (25%), not the usual M -- these get printed small, taped
outdoors and photographed at an angle, and the URL is short enough that the extra
redundancy costs almost no density.

Needs `segno` (pip3 install segno). Build-time only; nothing here ships in the
page. Run it from build/, like everything else here.

  python3 qr.py
"""
import io, os
import segno

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'share')

URL = 'https://jimbarnthouse-psf.github.io/hill-yard-sale-map/'
BRICK = '#A63328'
INK = '#241A17'
PAPER = '#FFFFFF'


def card(qr_svg_inner, w=600, h=780):
    """The QR with the title and date around it, sized to print at 2x3 inches."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">'
        '<rect width="%d" height="%d" fill="%s"/>'
        '<style>'
        '.t{font-family:"Archivo Black","Arial Black",sans-serif;fill:%s}'
        '.m{font-family:"DM Mono",ui-monospace,Menlo,monospace;fill:%s}'
        '</style>'
        '<text class="t" x="%d" y="86" text-anchor="middle" font-size="44">THE HILL</text>'
        # style=, not fill=: the .t rule is a CSS declaration and would win over a
        # presentation attribute, which silently turned the brick line black
        '<text class="t" x="%d" y="136" text-anchor="middle" font-size="44" '
        'style="fill:%s">YARD SALE</text>'
        '<text class="t" x="%d" y="182" text-anchor="middle" font-size="32">MAP</text>'
        '<g transform="translate(%d,216)">%s</g>'
        '<text class="m" x="%d" y="%d" text-anchor="middle" font-size="22" '
        'letter-spacing="1.5">SAT SEP 26 &#183; 8AM-NOON</text>'
        '<text class="m" x="%d" y="%d" text-anchor="middle" font-size="15" '
        'style="fill:%s">Scan for the live walking map</text>'
        '</svg>'
    ) % (w, h, w, h, w, h, PAPER, INK, INK,
         w // 2, w // 2, BRICK, w // 2,
         (w - 420) // 2, qr_svg_inner,
         w // 2, 700, w // 2, 736, '#6C5D55')


def sign(qr_path, w=816, h=1056, qrsize=430):
    """Letter-proportioned sign: the QR plus how to keep it on your phone.

    No "works offline" anywhere -- there is a manifest and icons but no service
    worker, so a home-screen copy is a full-screen shortcut, not an offline app.
    Saying otherwise on a printed sign would be a promise nobody could take back.

    Everything is positioned off named baselines rather than magic numbers
    scattered through the string: the first draft had the caption sitting on top
    of the QR, because the code's height and the caption's y were set
    independently. No inline icons or box-drawing characters either -- the
    vertical-ellipsis glyph for Chrome's menu rendered as a colon in the fallback
    font, and an inline Share glyph collided with its own label.
    """
    mid = w // 2
    qr_y = 262
    cap_y = qr_y + qrsize + 42          # caption sits below the code, always
    sub_y = cap_y + 28
    rule_y = sub_y + 40
    head_y = rule_y + 40
    plat_y = head_y + 38
    # three short lines per column rather than two long ones: at two lines the
    # iPhone text ran past the midpoint and collided with the Android column
    l1_y, l2_y, l3_y = plat_y + 28, plat_y + 52, plat_y + 76
    colR = mid + 30
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %(w)d %(h)d" '
        'width="%(w)d" height="%(h)d">'
        '<rect width="%(w)d" height="%(h)d" fill="%(paper)s"/>'
        '<style>'
        '.t{font-family:"Archivo Black","Arial Black",sans-serif;fill:%(ink)s}'
        '.m{font-family:"DM Mono",ui-monospace,Menlo,monospace;fill:%(ink)s}'
        '.b{font-family:"Public Sans",system-ui,sans-serif;fill:%(ink)s}'
        '</style>'
        '<text class="t" x="%(mid)d" y="96" text-anchor="middle" font-size="52">THE HILL</text>'
        '<text class="t" x="%(mid)d" y="154" text-anchor="middle" font-size="52" '
        'style="fill:%(brick)s">YARD SALE</text>'
        '<text class="t" x="%(mid)d" y="204" text-anchor="middle" font-size="36">MAP</text>'
        '<text class="m" x="%(mid)d" y="242" text-anchor="middle" font-size="21" '
        'letter-spacing="1.5">SAT SEP 26 &#183; 8AM-NOON</text>'
        '<g transform="translate(%(qrx)d,%(qry)d)">%(qr)s</g>'
        '<text class="b" x="%(mid)d" y="%(cap)d" text-anchor="middle" font-size="23" '
        'font-weight="600">Point your camera at the code</text>'
        '<text class="b" x="%(mid)d" y="%(sub)d" text-anchor="middle" font-size="16" '
        'style="fill:%(mute)s">Live map &#183; find the sales nearest you as you walk</text>'
        '<line x1="96" y1="%(rule)d" x2="%(rx)d" y2="%(rule)d" stroke="%(line)s" stroke-width="1"/>'
        '<text class="t" x="96" y="%(head)d" font-size="15">KEEP IT ON YOUR PHONE</text>'
        '<text class="m" x="96" y="%(plat)d" font-size="16">iPHONE</text>'
        '<text class="b" x="96" y="%(l1)d" font-size="15">Open in '
        '<tspan font-weight="600">Safari</tspan>, tap the Share</text>'
        '<text class="b" x="96" y="%(l2)d" font-size="15">icon (square with an arrow),</text>'
        '<text class="b" x="96" y="%(l3)d" font-size="15">then '
        '<tspan font-weight="600">Add to Home Screen</tspan>.</text>'
        '<text class="m" x="%(colR)d" y="%(plat)d" font-size="16">ANDROID</text>'
        '<text class="b" x="%(colR)d" y="%(l1)d" font-size="15">Open in '
        '<tspan font-weight="600">Chrome</tspan>, tap the</text>'
        '<text class="b" x="%(colR)d" y="%(l2)d" font-size="15">three-dot menu, then</text>'
        '<text class="b" x="%(colR)d" y="%(l3)d" font-size="15">'
        '<tspan font-weight="600">Add to Home screen</tspan>.</text>'
        '<text class="m" x="%(mid)d" y="%(url)d" text-anchor="middle" font-size="13" '
        'style="fill:%(mute)s">%(urltxt)s</text>'
        '</svg>'
    ) % {'w': w, 'h': h, 'mid': mid, 'paper': PAPER, 'ink': INK, 'brick': BRICK,
         'mute': '#6C5D55', 'line': '#E4DBD4', 'qr': qr_path,
         'qrx': (w - qrsize) // 2, 'qry': qr_y, 'cap': cap_y, 'sub': sub_y,
         'rule': rule_y, 'rx': w - 96, 'head': head_y, 'plat': plat_y,
         'l1': l1_y, 'l2': l2_y, 'l3': l3_y, 'colR': colR, 'url': h - 52,
         'urltxt': URL.replace('https://', '')}


def main():
    os.makedirs(OUT, exist_ok=True)
    qr = segno.make(URL, error='q')

    # Plain black on white: the version to drop into someone else's layout, and
    # the most reliable thing to scan.
    qr.save(os.path.join(OUT, 'qr.svg'), scale=10, border=2,
            dark=INK, light=PAPER)
    qr.save(os.path.join(OUT, 'qr.png'), scale=20, border=2,
            dark=INK, light=PAPER)

    # The QR body as one <path>, built from the module matrix at whatever pixel
    # size the layout needs. Nesting segno's own <svg> inside another SVG is
    # brittle across renderers; a path is not.
    rows = list(qr.matrix)
    mods = len(rows)

    def qr_path(size):
        unit = float(size) / mods
        d = []
        for y, row in enumerate(rows):
            x = 0
            while x < mods:
                if row[x]:
                    run = 1
                    while x + run < mods and row[x + run]:
                        run += 1
                    # one rect per horizontal run, so the path stays small
                    d.append('M%.3f %.3fh%.3fv%.3fh-%.3fz'
                             % (x * unit, y * unit, run * unit, unit, run * unit))
                    x += run
                else:
                    x += 1
        return '<path d="%s" fill="%s" shape-rendering="crispEdges"/>' % (''.join(d), INK)

    inner = qr_path(420)

    io.open(os.path.join(OUT, 'qr-card.svg'), 'w', encoding='utf-8').write(
        card(inner))

    io.open(os.path.join(OUT, 'qr-sign.svg'), 'w', encoding='utf-8').write(
        sign(qr_path(430)))

    print('share/qr.svg       plain, scalable  -> any layout')
    print('share/qr.png       plain, %d px      -> web, texts, social'
          % qr.symbol_size(scale=20, border=2)[0])
    print('share/qr-card.svg  ready-to-print card (prints well at 2x3 in)')
    print('share/qr-sign.svg  letter-size sign, QR + home-screen instructions')
    print('encodes: ' + URL)


if __name__ == '__main__':
    main()
