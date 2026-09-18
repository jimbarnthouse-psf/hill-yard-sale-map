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


def main():
    os.makedirs(OUT, exist_ok=True)
    qr = segno.make(URL, error='q')

    # Plain black on white: the version to drop into someone else's layout, and
    # the most reliable thing to scan.
    qr.save(os.path.join(OUT, 'qr.svg'), scale=10, border=2,
            dark=INK, light=PAPER)
    qr.save(os.path.join(OUT, 'qr.png'), scale=20, border=2,
            dark=INK, light=PAPER)

    # The QR body as one <path>, built from the module matrix. Nesting segno's
    # own <svg> inside the card SVG is brittle across renderers; a path is not.
    rows = list(qr.matrix)
    mods = len(rows)
    unit = 420.0 / mods
    d = []
    for y, row in enumerate(rows):
        x = 0
        while x < mods:
            if row[x]:
                run = 1
                while x + run < mods and row[x + run]:
                    run += 1
                # one rect per horizontal run of dark modules, so the path stays small
                d.append('M%.3f %.3fh%.3fv%.3fh-%.3fz'
                         % (x * unit, y * unit, run * unit, unit, run * unit))
                x += run
            else:
                x += 1
    inner = '<path d="%s" fill="%s" shape-rendering="crispEdges"/>' % (''.join(d), INK)

    io.open(os.path.join(OUT, 'qr-card.svg'), 'w', encoding='utf-8').write(
        card(inner))

    print('share/qr.svg       plain, scalable  -> any layout')
    print('share/qr.png       plain, %d px      -> web, texts, social'
          % qr.symbol_size(scale=20, border=2)[0])
    print('share/qr-card.svg  ready-to-print card (prints well at 2x3 in)')
    print('encodes: ' + URL)


if __name__ == '__main__':
    main()
