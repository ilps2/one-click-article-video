#!/usr/bin/env python3
"""9:16 (1080×1920) composition → 3:4 (1080×1440) 自适应转换。

关键规则:3:4 与 9:16 **宽度相同(1080)**,所以字号/卡片宽度/水平间距全部保持,
只压缩垂直尺寸 —— 等比 ×0.75 缩放是错的(内容变小、观感像裁切)。

用法:
  python3 scale-to-34.py index.html -o compositions/redbook-34.html
  # 可选:大图形 id 额外缩小(--shrink-seal #seal 0.85),长标题字号(--font-shrink '#s1-title-1:0.85')
"""
import argparse
import re
import sys

VERT_FACTOR = 0.72      # margin/padding 垂直值压缩比
HEIGHT_FACTOR = 0.78    # 元素 height >100px 压缩比
FONT_KEEP = True        # 字号保持(3:4 与 9:16 同宽)


def parse_args():
    ap = argparse.ArgumentParser(description="9:16 → 3:4 自适应转换")
    ap.add_argument("src", help="9:16 源文件")
    ap.add_argument("-o", "--out", default="compositions/redbook-34.html")
    ap.add_argument("--shrink", action="append", default=[],
                    help="大图形缩小: '#seal,0.85'(id/选择器,比例)")
    ap.add_argument("--font-shrink", action="append", default=[],
                    help="长标题字号缩小: '#s1-title-1,0.85'")
    return ap.parse_args()


def scale_vertical_css(out):
    """垂直 margin/padding 压缩,水平值保持。"""
    out = re.sub(r'(margin-(?:top|bottom)): (\d+)px',
                 lambda m: f'{m.group(1)}: {max(1, round(int(m.group(2))*VERT_FACTOR))}px', out)

    def pad(m):
        vals = m.group(2).split()
        n = len(vals)
        if n in (2, 3):
            vals[0] = str(max(1, round(int(vals[0])*VERT_FACTOR)))
            vals[-1] = str(max(1, round(int(vals[-1])*VERT_FACTOR)))
        elif n == 4:
            vals[0] = str(max(1, round(int(vals[0])*VERT_FACTOR)))
            vals[2] = str(max(1, round(int(vals[2])*VERT_FACTOR)))
        return f'padding: {" ".join(vals)}'
    return re.sub(r'(padding): ([\d\s]+px)', pad, out)


def scale_heights(out):
    """高度 >100px 的元素(图形/卡片)压缩。"""
    return re.sub(r'height: (\d+)px;',
                  lambda m: f'height: {max(1, round(int(m.group(1))*HEIGHT_FACTOR))}px;'
                  if int(m.group(1)) > 100 else m.group(0), out)


def shrink_selectors(out, specs, kind):
    for spec in specs:
        sel, ratio = spec.split(',')
        ratio = float(ratio)
        if kind == 'shrink':
            # 缩 width/height 与 font-size(图形内文字)
            out = re.sub(rf'({re.escape(sel)} \{{[^}}]*?)width: (\d+)px;',
                         lambda m, r=ratio: f'{m.group(1)}width: {max(1, round(int(m.group(2))*r))}px;', out)
            out = re.sub(rf'({re.escape(sel)} \{{[^}}]*?)height: (\d+)px;',
                         lambda m, r=ratio: f'{m.group(1)}height: {max(1, round(int(m.group(2))*r))}px;', out)
            out = re.sub(rf'({re.escape(sel)} \{{[^}}]*?)font-size: (\d+)px;',
                         lambda m, r=ratio: f'{m.group(1)}font-size: {max(1, round(int(m.group(2))*r))}px;', out)
        else:  # font-shrink
            out = re.sub(rf'({re.escape(sel)} \{{[^}}]*?)font-size: (\d+)px;',
                         lambda m, r=ratio: f'{m.group(1)}font-size: {max(1, round(int(m.group(2))*r))}px;', out)
    return out


def main():
    args = parse_args()
    src = open(args.src, encoding='utf-8').read()
    out = src
    out = scale_vertical_css(out)
    out = scale_heights(out)
    for spec in args.shrink:
        out = shrink_selectors(out, [spec], 'shrink')
    for spec in args.font_shrink:
        out = shrink_selectors(out, [spec], 'font')
    # 画布尺寸
    out = out.replace('width: 1080px; height: 1920px', 'width: 1080px; height: 1440px')
    out = out.replace('content="width=1080, height=1920"', 'content="width=1080, height=1440"')
    out = out.replace('data-height="1920"', 'data-height="1440"')
    out = out.replace('9:16', '3:4')
    open(args.out, 'w', encoding='utf-8').write(out)
    print(f'✅ 3:4 自适应版: {args.out}')


if __name__ == '__main__':
    main()
