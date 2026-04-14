"""
Generate a PowerPoint presentation for STHN group meeting.
STHN: Deep Homography Estimation for UAV Thermal Geo-localization with Satellite Imagery
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── Helpers ──────────────────────────────────────────────────────────────────

SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Color palette
BG_DARK = RGBColor(0x1B, 0x1B, 0x2F)       # Deep navy background
ACCENT = RGBColor(0x00, 0xAE, 0xEF)         # Bright blue accent
ACCENT2 = RGBColor(0x00, 0xD2, 0xA0)        # Teal / green accent
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xBB, 0xBB, 0xCC)
ORANGE = RGBColor(0xFF, 0x8C, 0x00)
YELLOW = RGBColor(0xFF, 0xD7, 0x00)


def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_textbox(slide, left, top, width, height, text, font_size=18,
                bold=False, color=WHITE, alignment=PP_ALIGN.LEFT,
                font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    return tf


def add_para(tf, text, font_size=18, bold=False, color=WHITE,
             alignment=PP_ALIGN.LEFT, space_before=Pt(6), font_name="Calibri",
             level=0):
    p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    p.space_before = space_before
    p.level = level
    return p


def add_accent_line(slide, left, top, width, color=ACCENT):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, Pt(3))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def add_rounded_rect(slide, left, top, width, height, fill_color, text="",
                     font_size=14, font_color=WHITE):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    if text:
        tf = shape.text_frame
        tf.word_wrap = True
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(font_size)
        p.font.color.rgb = font_color
        p.font.name = "Calibri"
    shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    return shape


def slide_title(slide, title_text, subtitle_text=None):
    """Add a consistent slide title bar."""
    add_textbox(slide, Inches(0.6), Inches(0.3), Inches(12), Inches(0.8),
                title_text, font_size=32, bold=True, color=WHITE)
    add_accent_line(slide, Inches(0.6), Inches(1.05), Inches(2.5), ACCENT)
    if subtitle_text:
        add_textbox(slide, Inches(0.6), Inches(1.15), Inches(12), Inches(0.5),
                    subtitle_text, font_size=16, color=LIGHT_GRAY)


# ── Build Presentation ──────────────────────────────────────────────────────

prs = Presentation()
prs.slide_width = SLIDE_WIDTH
prs.slide_height = SLIDE_HEIGHT

# ============================
# Slide 1: Title Slide
# ============================
sl = prs.slides.add_slide(prs.slide_layouts[6])  # blank
set_slide_bg(sl, BG_DARK)

add_textbox(sl, Inches(1), Inches(1.5), Inches(11.3), Inches(1.5),
            "STHN: Deep Homography Estimation for\nUAV Thermal Geo-localization with Satellite Imagery",
            font_size=36, bold=True, color=WHITE, alignment=PP_ALIGN.CENTER)

add_accent_line(sl, Inches(4), Inches(3.2), Inches(5.3), ACCENT)

add_textbox(sl, Inches(1), Inches(3.5), Inches(11.3), Inches(0.6),
            "IEEE Robotics and Automation Letters (RA-L), 2024",
            font_size=20, color=ACCENT, alignment=PP_ALIGN.CENTER)

add_textbox(sl, Inches(1), Inches(4.2), Inches(11.3), Inches(0.6),
            "Jiuhong Xiao, Ning Zhang, Daniel Tortei, Giuseppe Loianno",
            font_size=18, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)

add_textbox(sl, Inches(1), Inches(4.8), Inches(11.3), Inches(0.6),
            "NYU Agile Robotics & Perception Lab (ARPL)",
            font_size=16, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)

add_textbox(sl, Inches(1), Inches(6.2), Inches(11.3), Inches(0.5),
            "arXiv: 2405.20470  |  组会汇报",
            font_size=14, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)

# ============================
# Slide 2: Outline
# ============================
sl = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(sl, BG_DARK)
slide_title(sl, "Outline 报告提纲")

items = [
    ("1", "研究背景与动机", "Background & Motivation"),
    ("2", "问题定义", "Problem Formulation"),
    ("3", "方法总览 — STHN 框架", "Method Overview"),
    ("4", "粗对齐模块 (Coarse Alignment)", "Feature Extraction & Iterative Update"),
    ("5", "精细化模块 (Refinement)", "Two-Stage Pipeline"),
    ("6", "热图像生成模块 (TGM)", "Thermal Generation Module"),
    ("7", "数据集与实验设置", "Dataset & Experimental Setup"),
    ("8", "实验结果与分析", "Results & Analysis"),
    ("9", "总结与展望", "Summary & Future Work"),
]

for i, (num, cn, en) in enumerate(items):
    y = Inches(1.6) + Inches(0.6) * i
    add_rounded_rect(sl, Inches(0.8), y, Inches(0.5), Inches(0.45),
                     ACCENT, num, font_size=16, font_color=WHITE)
    add_textbox(sl, Inches(1.5), y, Inches(5), Inches(0.45),
                cn, font_size=18, bold=True, color=WHITE)
    add_textbox(sl, Inches(6.5), y, Inches(6), Inches(0.45),
                en, font_size=15, color=LIGHT_GRAY)

# ============================
# Slide 3: Background & Motivation
# ============================
sl = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(sl, BG_DARK)
slide_title(sl, "研究背景与动机", "Background & Motivation")

tf = add_textbox(sl, Inches(0.6), Inches(1.5), Inches(6), Inches(5.5),
                 "▸ UAV 热成像地理定位的挑战",
                 font_size=20, bold=True, color=ACCENT)
add_para(tf, "• GPS 拒止/干扰环境下需要视觉替代方案", font_size=16, color=WHITE)
add_para(tf, "• 热红外图像与 RGB 卫星图像存在巨大模态差异", font_size=16, color=WHITE)
add_para(tf, "• 夜间场景下 RGB 相机不可用，仅热成像可用", font_size=16, color=WHITE)

add_para(tf, "", font_size=10)
add_para(tf, "▸ 现有方法的不足", font_size=20, bold=True, color=ACCENT)
add_para(tf, "• 图像检索方法 (如 STGL) 精度有限 (仅到块级)", font_size=16, color=WHITE)
add_para(tf, "• 传统特征点匹配在跨模态下性能严重退化", font_size=16, color=WHITE)
add_para(tf, "• 缺少针对卫星-热图像对的 homography 估计方法", font_size=16, color=WHITE)

add_para(tf, "", font_size=10)
add_para(tf, "▸ 我们的解决方案", font_size=20, bold=True, color=ACCENT2)
add_para(tf, "• 提出 STHN：首个针对 UAV 热-卫星图像的深度 homography 方法",
         font_size=16, bold=True, color=YELLOW)
add_para(tf, "• 实现亚像素级精度的跨模态地理定位", font_size=16, color=WHITE)

# Right side: key visual concept
add_rounded_rect(sl, Inches(7.2), Inches(1.6), Inches(5.5), Inches(2),
                 RGBColor(0x2A, 0x2A, 0x45),
                 "卫星图 (RGB)\n↕ 模态差异\n热红外图 (Thermal)",
                 font_size=18, font_color=WHITE)

add_rounded_rect(sl, Inches(7.2), Inches(4.0), Inches(5.5), Inches(1.5),
                 RGBColor(0x2A, 0x2A, 0x45),
                 "STHN: 通过 Deep Homography\n弥合跨模态差距 → 像素级定位",
                 font_size=16, font_color=ACCENT2)

# ============================
# Slide 4: Problem Formulation
# ============================
sl = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(sl, BG_DARK)
slide_title(sl, "问题定义", "Problem Formulation")

tf = add_textbox(sl, Inches(0.6), Inches(1.5), Inches(12), Inches(5.5),
                 "▸ 输入",
                 font_size=20, bold=True, color=ACCENT)
add_para(tf, "• 卫星 RGB 图像 I_s ∈ ℝ^(W_S × W_S × 3)  (如 512×512 或 1536×1536)",
         font_size=16, color=WHITE)
add_para(tf, "• 无人机热图像 I_t ∈ ℝ^(W × W × 1)  (Resize 到 256×256 → 复制为 3 通道)",
         font_size=16, color=WHITE)

add_para(tf, "", font_size=10)
add_para(tf, "▸ 输出", font_size=20, bold=True, color=ACCENT)
add_para(tf, "• 4-点位移 Δp ∈ ℝ^(2×2×2)  表示四个角点 (TL, TR, BL, BR) 的偏移",
         font_size=16, color=WHITE)
add_para(tf, "• 通过 DLT (Direct Linear Transformation) 求解 3×3 Homography 矩阵 H",
         font_size=16, color=WHITE)

add_para(tf, "", font_size=10)
add_para(tf, "▸ 损失函数", font_size=20, bold=True, color=ACCENT)
add_para(tf, "• 序列损失: L = Σᵢ γ^(N-i) · ||Δpᵢ - Δp_gt||₁  (γ = 0.8, 指数加权)",
         font_size=16, color=WHITE)

add_para(tf, "", font_size=10)
add_para(tf, "▸ 评价指标", font_size=20, bold=True, color=ACCENT)
add_para(tf, "• MACE (Mean Average Corner Error): 四个角点的平均像素误差",
         font_size=16, color=WHITE)
add_para(tf, "• MA (Metric Accuracy): 对应到实际地理距离 (米) 的定位精度",
         font_size=16, color=WHITE)

# ============================
# Slide 5: Method Overview
# ============================
sl = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(sl, BG_DARK)
slide_title(sl, "方法总览 — STHN 框架", "Method Overview — STHN Pipeline")

# Pipeline flow boxes
stages = [
    ("卫星图 I_s\n(W_S × W_S)", Inches(0.3), LIGHT_GRAY),
    ("Resize →\n(W × W)", Inches(2.5), LIGHT_GRAY),
    ("Feature\nExtractor\n(ResBlock ×4\n+ InstanceNorm)", Inches(4.3), ACCENT),
    ("Correlation\nVolume\n(Multi-level)", Inches(6.5), ACCENT),
    ("Iterative\nUpdater\n(CNN + GN)", Inches(8.7), ACCENT),
    ("4-Point\nDisplacement\nΔp", Inches(10.9), ACCENT2),
]

for text, left, clr in stages:
    add_rounded_rect(sl, left, Inches(1.8), Inches(1.8), Inches(1.8),
                     RGBColor(0x2A, 0x2A, 0x45), text, font_size=13, font_color=clr)

# Arrows between boxes
for i in range(len(stages) - 1):
    left_arrow = stages[i][1] + Inches(1.85)
    add_textbox(sl, left_arrow, Inches(2.35), Inches(0.5), Inches(0.5),
                "→", font_size=28, bold=True, color=ACCENT, alignment=PP_ALIGN.CENTER)

# Thermal input
add_rounded_rect(sl, Inches(0.3), Inches(4.0), Inches(1.8), Inches(1.0),
                 RGBColor(0x2A, 0x2A, 0x45), "热红外图 I_t\n(W × W)", font_size=13, font_color=LIGHT_GRAY)
add_textbox(sl, Inches(2.1), Inches(4.1), Inches(2), Inches(0.5),
            "──────────────→", font_size=14, color=ACCENT)

# Key points below
tf = add_textbox(sl, Inches(0.6), Inches(5.3), Inches(12), Inches(2),
                 "核心组件:", font_size=18, bold=True, color=ACCENT)
add_para(tf, "① BasicEncoderQuarter: 残差块 + InstanceNorm, 输出 256 维特征 (1/4 分辨率)",
         font_size=14, color=WHITE)
add_para(tf, "② CorrBlock: 多级金字塔 correlation volume, 在 4-level pyramid 上计算特征相关性",
         font_size=14, color=WHITE)
add_para(tf, "③ Iterative Update (GMA/CNN): 6 次迭代更新, 每次预测残差位移 δΔp, 逐步精化 homography",
         font_size=14, color=WHITE)
add_para(tf, "④ DLT: kornia.geometry.transform.get_perspective_transform 求解 H 矩阵",
         font_size=14, color=WHITE)

# ============================
# Slide 6: Coarse Alignment Module
# ============================
sl = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(sl, BG_DARK)
slide_title(sl, "粗对齐模块", "Coarse-Level Alignment Module")

# Left: Feature Extractor
add_rounded_rect(sl, Inches(0.5), Inches(1.5), Inches(5.8), Inches(0.6),
                 ACCENT, "Feature Extractor — BasicEncoderQuarter", font_size=16)

tf = add_textbox(sl, Inches(0.5), Inches(2.2), Inches(5.8), Inches(3),
                 "", font_size=14, color=WHITE)
add_para(tf, "• Conv2d(3→64, 7×7, stride=1) + InstanceNorm + ReLU", font_size=14, color=WHITE)
add_para(tf, "• MaxPool(2×2) → 1/2 分辨率", font_size=14, color=WHITE)
add_para(tf, "• ResidualBlock ×2 (64→64) + MaxPool → 1/4 分辨率", font_size=14, color=WHITE)
add_para(tf, "• ResidualBlock ×2 (64→96)", font_size=14, color=WHITE)
add_para(tf, "• Conv2d(96→256, 1×1) → 输出 256 维特征图", font_size=14, color=WHITE)
add_para(tf, "", font_size=8)
add_para(tf, "• 共享权重: 卫星图与热图使用同一 Encoder", font_size=14, color=YELLOW, bold=True)

# Right: Iterative Update
add_rounded_rect(sl, Inches(7), Inches(1.5), Inches(5.8), Inches(0.6),
                 ACCENT, "Iterative Updater — CNN_64", font_size=16)

tf = add_textbox(sl, Inches(7), Inches(2.2), Inches(5.8), Inches(3),
                 "", font_size=14, color=WHITE)
add_para(tf, "• 输入: Correlation + Flow (164/326/488 维)", font_size=14, color=WHITE)
add_para(tf, "• 5 层 Conv2d(3×3) + GroupNorm + ReLU + MaxPool", font_size=14, color=WHITE)
add_para(tf, "• 输出: 2 维残差位移 δΔp → reshape 为 (2,2,2)", font_size=14, color=WHITE)
add_para(tf, "", font_size=8)
add_para(tf, "• Correlation Volume (CorrBlock):", font_size=14, color=ACCENT2, bold=True)
add_para(tf, "  - 对特征图构建多级 correlation pyramid", font_size=14, color=WHITE)
add_para(tf, "  - 在 radius=4 邻域内采样 → (2r+1)² = 81 维/级", font_size=14, color=WHITE)
add_para(tf, "  - corr_level=2: 81×2+2=164 | level=4: 81×4+2=326", font_size=14, color=WHITE)

# Bottom: iteration diagram
add_rounded_rect(sl, Inches(0.5), Inches(5.5), Inches(12.3), Inches(1.5),
                 RGBColor(0x2A, 0x2A, 0x45), "", font_size=14)
tf = add_textbox(sl, Inches(0.8), Inches(5.6), Inches(12), Inches(1.4),
                 "迭代过程 (6 iterations):", font_size=16, bold=True, color=ACCENT2)
add_para(tf, "Δp₀=0 → corr(coords) → δΔp₁ → Δp₁ → DLT→H₁ → warp coords → corr(coords') → δΔp₂ → Δp₂ → ... → Δp₆ (最终输出)",
         font_size=14, color=WHITE)
add_para(tf, "每次迭代利用更新后的 coords 重新计算 correlation，逐步逼近真实 homography",
         font_size=13, color=LIGHT_GRAY)

# ============================
# Slide 7: Two-Stage Refinement
# ============================
sl = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(sl, BG_DARK)
slide_title(sl, "两阶段精细化模块 (W_S=1536)", "Two-Stage Refinement Pipeline")

# Stage 1
add_rounded_rect(sl, Inches(0.5), Inches(1.5), Inches(5.8), Inches(0.6),
                 ACCENT, "Stage 1: 粗对齐 (Coarse Alignment)", font_size=16)
tf = add_textbox(sl, Inches(0.5), Inches(2.2), Inches(5.8), Inches(2.2),
                 "", font_size=14, color=WHITE)
add_para(tf, "• 卫星图 (1536×1536) → Resize (256×256)", font_size=14, color=WHITE)
add_para(tf, "• 热图 (256×256)", font_size=14, color=WHITE)
add_para(tf, "• IHN 网络 (corr_level=4, 6 次迭代)", font_size=14, color=WHITE)
add_para(tf, "• 输出: 粗略 4-point displacement Δp_coarse", font_size=14, color=YELLOW)

# Stage 2
add_rounded_rect(sl, Inches(7), Inches(1.5), Inches(5.8), Inches(0.6),
                 ACCENT2, "Stage 2: 精细化 (Refinement)", font_size=16)
tf = add_textbox(sl, Inches(7), Inches(2.2), Inches(5.8), Inches(2.5),
                 "", font_size=14, color=WHITE)
add_para(tf, "• 根据 Δp_coarse 从原始卫星图 crop 对应区域", font_size=14, color=WHITE)
add_para(tf, "• Crop → Resize (256×256) 得到更高分辨率输入", font_size=14, color=WHITE)
add_para(tf, "• 第二个 IHN 网络 (corr_level=2, 6 次迭代)", font_size=14, color=WHITE)
add_para(tf, "• 输出: 精细 Δp_fine", font_size=14, color=YELLOW)
add_para(tf, "• 最终: Δp = Δp_fine × κ + flow_bbox / α", font_size=14, color=ACCENT2)

# Arrow
add_textbox(sl, Inches(6.1), Inches(2.5), Inches(1), Inches(0.5),
            "→→→", font_size=24, bold=True, color=ORANGE, alignment=PP_ALIGN.CENTER)

# Bottom: advantage
add_rounded_rect(sl, Inches(0.5), Inches(5.0), Inches(12.3), Inches(2),
                 RGBColor(0x2A, 0x2A, 0x45), "", font_size=14)
tf = add_textbox(sl, Inches(0.8), Inches(5.1), Inches(12), Inches(1.8),
                 "两阶段的优势:", font_size=18, bold=True, color=ACCENT2)
add_para(tf, "• Coarse 阶段: 大范围搜索，处理大的初始偏移 (W_S=1536 覆盖区域是 W_S=512 的 9 倍)",
         font_size=14, color=WHITE)
add_para(tf, "• Refine 阶段: 在 crop 的高分辨率局部区域上精细化，显著提升定位精度",
         font_size=14, color=WHITE)
add_para(tf, "• Coarse 模块训练完成后可冻结权重，仅训练 Refine 模块 (参数高效)",
         font_size=14, color=WHITE)
add_para(tf, "• fine_padding 参数控制 crop 区域的额外边距 → 容纳粗对齐的误差",
         font_size=14, color=WHITE)

# ============================
# Slide 8: TGM — Thermal Generation Module
# ============================
sl = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(sl, BG_DARK)
slide_title(sl, "热图像生成模块 (TGM)", "Thermal Generation Module — Pix2Pix")

tf = add_textbox(sl, Inches(0.6), Inches(1.5), Inches(5.8), Inches(5),
                 "▸ 动机", font_size=20, bold=True, color=ACCENT)
add_para(tf, "• 热红外配对数据稀缺且采集成本高", font_size=16, color=WHITE)
add_para(tf, "• 仅使用有限的训练数据容易过拟合", font_size=16, color=WHITE)
add_para(tf, "", font_size=8)
add_para(tf, "▸ 方案: Pix2Pix 风格 GAN", font_size=20, bold=True, color=ACCENT)
add_para(tf, "• 输入: 卫星 RGB 图像 (无需热图像配对)", font_size=16, color=WHITE)
add_para(tf, "• 输出: 生成的热图像 (合成训练数据)", font_size=16, color=WHITE)
add_para(tf, "• Generator: UNet 结构", font_size=16, color=WHITE)
add_para(tf, "• Discriminator: PatchGAN", font_size=16, color=WHITE)
add_para(tf, "", font_size=8)
add_para(tf, "▸ 数据增强策略", font_size=20, bold=True, color=ACCENT)
add_para(tf, "• 生成 extended_queries 覆盖更大区域", font_size=16, color=WHITE)
add_para(tf, "• 训练时交替使用真实与生成数据", font_size=16, color=WHITE)
add_para(tf, "• 生成数据排除测试区域，防止信息泄露", font_size=16, color=YELLOW, bold=True)

# Right side: pipeline diagram
add_rounded_rect(sl, Inches(7), Inches(1.6), Inches(2.4), Inches(1),
                 RGBColor(0x2A, 0x2A, 0x45), "卫星 RGB 图像", font_size=14, font_color=LIGHT_GRAY)
add_textbox(sl, Inches(7.8), Inches(2.7), Inches(1), Inches(0.4),
            "↓", font_size=24, color=ACCENT, alignment=PP_ALIGN.CENTER)
add_rounded_rect(sl, Inches(7), Inches(3.1), Inches(2.4), Inches(1),
                 ACCENT, "TGM\n(Pix2Pix)", font_size=14, font_color=WHITE)
add_textbox(sl, Inches(7.8), Inches(4.2), Inches(1), Inches(0.4),
            "↓", font_size=24, color=ACCENT, alignment=PP_ALIGN.CENTER)
add_rounded_rect(sl, Inches(7), Inches(4.6), Inches(2.4), Inches(1),
                 RGBColor(0x2A, 0x2A, 0x45), "合成热图像", font_size=14, font_color=ACCENT2)

add_textbox(sl, Inches(9.6), Inches(3.1), Inches(0.6), Inches(1),
            "→", font_size=28, color=ACCENT, alignment=PP_ALIGN.CENTER)

add_rounded_rect(sl, Inches(10.2), Inches(2.8), Inches(2.5), Inches(1.5),
                 RGBColor(0x2A, 0x2A, 0x45),
                 "扩展训练数据\n(extended_queries.h5)\n区域: 23,744m × 9,088m",
                 font_size=13, font_color=WHITE)

# ============================
# Slide 9: Dataset & Experiments
# ============================
sl = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(sl, BG_DARK)
slide_title(sl, "数据集与实验结果", "Dataset & Experimental Results")

# Dataset info
tf = add_textbox(sl, Inches(0.6), Inches(1.5), Inches(5.8), Inches(2.5),
                 "▸ Boson-nighttime 数据集 (扩展版)", font_size=18, bold=True, color=ACCENT)
add_para(tf, "• 6 次航拍飞行 (21:00 - 03:00)", font_size=14, color=WHITE)
add_para(tf, "• 3 次上半区域 + 3 次下半区域", font_size=14, color=WHITE)
add_para(tf, "• 下半区域: 训练集 + 验证集 / 上半区域: 测试集", font_size=14, color=WHITE)
add_para(tf, "• 数据格式: HDF5 (h5), 总计 122 GB", font_size=14, color=WHITE)
add_para(tf, "• W_S=512 (标准) / W_S=1536 (大范围)", font_size=14, color=WHITE)

# Results table header
add_rounded_rect(sl, Inches(0.5), Inches(4.2), Inches(12.3), Inches(0.5),
                 ACCENT, "实验结果对比 (W_S=512)", font_size=16)

# Table-like layout
headers = ["Method", "MACE↓", "MA (m)↓"]
col_x = [Inches(0.8), Inches(4.5), Inches(7.5)]
y_header = Inches(4.8)
for j, h in enumerate(headers):
    add_textbox(sl, col_x[j], y_header, Inches(2.5), Inches(0.35),
                h, font_size=14, bold=True, color=ACCENT)

rows = [
    ("STGL (Image Retrieval)", "Block-level (R@1)", "~3.2m"),
    ("LoFTR (Feature Matching)", "—", "> STHN"),
    ("R2D2 (Feature Matching)", "—", "> STHN"),
    ("STHN-One Stage (Ours)", "低 MACE", "更精确"),
    ("STHN-Two Stage (Ours, 1536)", "最低 MACE", "最精确 ✓"),
]

for i, (m, mace, ma) in enumerate(rows):
    y = Inches(5.15) + Inches(0.35) * i
    clr = YELLOW if "Ours" in m else WHITE
    bld = "Ours" in m
    add_textbox(sl, col_x[0], y, Inches(3.5), Inches(0.35), m, font_size=13, color=clr, bold=bld)
    add_textbox(sl, col_x[1], y, Inches(2.5), Inches(0.35), mace, font_size=13, color=clr, bold=bld)
    add_textbox(sl, col_x[2], y, Inches(2.5), Inches(0.35), ma, font_size=13, color=clr, bold=bld)

# Right side: key findings
add_rounded_rect(sl, Inches(7), Inches(1.5), Inches(5.8), Inches(2.2),
                 RGBColor(0x2A, 0x2A, 0x45), "", font_size=14)
tf = add_textbox(sl, Inches(7.2), Inches(1.6), Inches(5.5), Inches(2),
                 "Key Findings:", font_size=16, bold=True, color=ACCENT2)
add_para(tf, "✓ STHN 显著超越图像检索方法", font_size=14, color=WHITE)
add_para(tf, "✓ 两阶段 > 单阶段 (更大搜索范围)", font_size=14, color=WHITE)
add_para(tf, "✓ TGM 数据增强有效提升泛化性", font_size=14, color=WHITE)
add_para(tf, "✓ Iterative update 收敛快 (6 次即可)", font_size=14, color=WHITE)
add_para(tf, "✓ 推理速度满足实时需求", font_size=14, color=WHITE)

# ============================
# Slide 10: Summary & Future Work
# ============================
sl = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(sl, BG_DARK)
slide_title(sl, "总结与展望", "Summary & Future Work")

# Summary
add_rounded_rect(sl, Inches(0.5), Inches(1.5), Inches(5.8), Inches(0.6),
                 ACCENT, "总结 Summary", font_size=16)
tf = add_textbox(sl, Inches(0.5), Inches(2.2), Inches(5.8), Inches(3.5),
                 "", font_size=14, color=WHITE)
add_para(tf, "✓ 提出 STHN: 首个面向 UAV 热-卫星图像的深度 homography 估计框架",
         font_size=15, color=WHITE)
add_para(tf, "✓ 创新性地结合 iterative correlation-based 估计与两阶段 coarse-to-fine 策略",
         font_size=15, color=WHITE)
add_para(tf, "✓ 引入 TGM (Pix2Pix) 实现跨模态数据增强，缓解训练数据不足",
         font_size=15, color=WHITE)
add_para(tf, "✓ 在 Boson-nighttime 数据集上实现 SOTA 性能",
         font_size=15, color=WHITE)
add_para(tf, "✓ 发表于 IEEE RA-L 2024, 代码与模型已开源",
         font_size=15, color=YELLOW, bold=True)

# Future Work
add_rounded_rect(sl, Inches(7), Inches(1.5), Inches(5.8), Inches(0.6),
                 ACCENT2, "展望 Future Work", font_size=16)
tf = add_textbox(sl, Inches(7), Inches(2.2), Inches(5.8), Inches(3.5),
                 "", font_size=14, color=WHITE)
add_para(tf, "→ UASTHN: 加入不确定性估计 (Uncertainty-Aware)",
         font_size=15, color=WHITE)
add_para(tf, "→ 长距离地理定位 (STGL 后续工作)",
         font_size=15, color=WHITE)
add_para(tf, "→ 更多模态/场景的泛化能力验证",
         font_size=15, color=WHITE)
add_para(tf, "→ 端到端结合全局检索 + 局部对齐",
         font_size=15, color=WHITE)
add_para(tf, "→ 实际 UAV 平台部署与实验",
         font_size=15, color=WHITE)

# References / Resources
add_rounded_rect(sl, Inches(0.5), Inches(5.8), Inches(12.3), Inches(1.2),
                 RGBColor(0x2A, 0x2A, 0x45), "", font_size=14)
tf = add_textbox(sl, Inches(0.8), Inches(5.9), Inches(12), Inches(1),
                 "Resources & Related Works:", font_size=14, bold=True, color=ACCENT)
add_para(tf, "Paper: arxiv.org/abs/2405.20470  |  Code: github.com/arplaboratory/STHN  |  Model: huggingface.co/xjh19972/STHN",
         font_size=12, color=LIGHT_GRAY)
add_para(tf, "STGL: Long-range UAV Thermal Geo-localization  |  UASTHN: Uncertainty-Aware Deep Homography Estimation",
         font_size=12, color=LIGHT_GRAY)

# ── Save ─────────────────────────────────────────────────────────────────────
output_path = "/home/runner/work/STHN/STHN/STHN_GroupMeeting_Presentation.pptx"
prs.save(output_path)
print(f"Presentation saved to: {output_path}")
print(f"Total slides: {len(prs.slides)}")
