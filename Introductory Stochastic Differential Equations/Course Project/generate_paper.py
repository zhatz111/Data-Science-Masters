"""
Generate the final course project PDF using ReportLab.
Uses registered Times New Roman TTF for Unicode Greek support.
All subscripts/superscripts use <sub>/<super> markup instead of Unicode
modifier letters.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    HRFlowable,
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

# ── Register Times New Roman TTF (supports Greek + extended Latin) ───────────
_FONT_DIR = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("TNR",    _FONT_DIR + "times.ttf"))
pdfmetrics.registerFont(TTFont("TNR-B",  _FONT_DIR + "timesbd.ttf"))
pdfmetrics.registerFont(TTFont("TNR-I",  _FONT_DIR + "timesi.ttf"))
pdfmetrics.registerFont(TTFont("TNR-BI", _FONT_DIR + "timesbi.ttf"))
pdfmetrics.registerFontFamily(
    "TNR", normal="TNR", bold="TNR-B", italic="TNR-I", boldItalic="TNR-BI"
)

# ── Paths ────────────────────────────────────────────────────────────────────
BASE    = Path(__file__).parent
FIG_DIR = BASE / "figures"
OUT     = BASE / "Final_Project_Draft.pdf"

# ── Styles ───────────────────────────────────────────────────────────────────
title_style = ParagraphStyle(
    "Title", fontName="TNR-B", fontSize=16, leading=21,
    alignment=TA_CENTER, spaceAfter=4,
)
subtitle_style = ParagraphStyle(
    "Subtitle", fontName="TNR", fontSize=11, leading=14,
    alignment=TA_CENTER, spaceAfter=2,
)
abstract_heading = ParagraphStyle(
    "AbstractHeading", fontName="TNR-B", fontSize=11, leading=14,
    alignment=TA_CENTER, spaceAfter=4,
)
abstract_style = ParagraphStyle(
    "Abstract", fontName="TNR", fontSize=10, leading=13,
    alignment=TA_JUSTIFY, leftIndent=36, rightIndent=36, spaceAfter=6,
)
section_style = ParagraphStyle(
    "Section", fontName="TNR-B", fontSize=12, leading=15,
    alignment=TA_LEFT, spaceBefore=10, spaceAfter=4,
)
subsection_style = ParagraphStyle(
    "Subsection", fontName="TNR-BI", fontSize=11, leading=13,
    alignment=TA_LEFT, spaceBefore=6, spaceAfter=3,
)
body_style = ParagraphStyle(
    "Body", fontName="TNR", fontSize=10, leading=14,
    alignment=TA_JUSTIFY, spaceAfter=6,
)
caption_style = ParagraphStyle(
    "Caption", fontName="TNR-I", fontSize=9, leading=11,
    alignment=TA_CENTER, spaceAfter=8,
)
eq_style = ParagraphStyle(
    "Eq", fontName="TNR", fontSize=10, leading=13,
    alignment=TA_CENTER, spaceAfter=4,
)
bullet_style = ParagraphStyle(
    "Bullet", fontName="TNR", fontSize=10, leading=14,
    alignment=TA_JUSTIFY, leftIndent=18, spaceAfter=4,
)
ref_style = ParagraphStyle(
    "Ref", fontName="TNR", fontSize=9, leading=12,
    alignment=TA_JUSTIFY, leftIndent=18, firstLineIndent=-18, spaceAfter=4,
)

# ── Helpers ──────────────────────────────────────────────────────────────────
def H(text):   return Paragraph(text, section_style)
def H2(text):  return Paragraph(text, subsection_style)
def B(text):   return Paragraph(text, body_style)
def EQ(text):  return Paragraph(text, eq_style)
def SP(n=6):   return Spacer(1, n)
def HR():      return HRFlowable(width="100%", thickness=0.5, color=colors.grey)

def fig(fname, width, caption_text):
    path = str(FIG_DIR / fname)
    img = Image(path, width=width, height=width * 0.65, kind="proportional")
    cap = Paragraph(caption_text, caption_style)
    return [img, cap]

# ── Content ──────────────────────────────────────────────────────────────────
story = []

# Title block
story.append(Paragraph(
    "Extended Kalman Filtering for State Estimation in Fed-Batch<br/>"
    "Bioreactor Systems Under Varying Noise Regimes",
    title_style,
))
story.append(SP(4))
story.append(Paragraph("Zachary Hatzenbeller", subtitle_style))
story.append(Paragraph("EN.625.714 \u2013 Stochastic Differential Equations", subtitle_style))
story.append(SP(8))
story.append(HR())
story.append(SP(4))

# ── Abstract ─────────────────────────────────────────────────────────────────
story.append(Paragraph("<b>Abstract</b>", abstract_heading))
story.append(Paragraph(
    "This project applies Extended Kalman Filter (EKF) methods to state estimation in a "
    "simulated 14-day fed-batch bioreactor running under Monod growth kinetics. The system "
    "has three states (viable cell concentration X<sub>v</sub>, substrate glucose S, and "
    "monoclonal antibody titer P) and is observed through a mix of online sensors and sparse "
    "offline assays. I implemented the EKF from the discrete-time stochastic state-space "
    "formulation, which ties back to the Kalman\u2013Bucy filter and It\u014d calculus "
    "covered in the course. A sweep over different process noise levels shows a "
    "bias\u2013variance tradeoff, where the best performance on X<sub>v</sub> and S is near "
    "the baseline Q setting. Whiteness tests on the innovations sequence (Ljung\u2013Box and "
    "ACF) confirm the martingale property holds under correct model specification. Baseline "
    "RMSE values came out to 0.172, 0.171, and 0.055 for X<sub>v</sub>, S, and P, respectively.",
    abstract_style,
))
story.append(SP(4))
story.append(HR())
story.append(SP(6))

# ── 1. Introduction ───────────────────────────────────────────────────────────
story.append(H("1. Introduction"))
story.append(B(
    "One of the core problems in stochastic systems is figuring out the true state of a system "
    "when your observations are noisy and incomplete. The Kalman filter gives the "
    "minimum-variance unbiased estimate for linear Gaussian systems, and the Extended Kalman "
    "Filter (EKF) extends that idea to nonlinear systems by linearizing around the current "
    "state estimate at each step."
))
story.append(B(
    "Fed-batch bioreactors are a good application for this because several things make them "
    "challenging to monitor directly. The growth dynamics are nonlinear (Monod kinetics), not "
    "all states can be measured continuously, sensors have different noise levels and sampling "
    "rates, and some measurements (like titer) only come from lab assays done once a day. "
    "Getting a good real-time estimate of cell concentration and titer matters a lot in "
    "pharmaceutical manufacturing for process control and meeting regulatory requirements."
))
story.append(B(
    "The main question I wanted to explore is: how does the level and structure of process "
    "and measurement noise affect how well the EKF can track the true state? And can we use "
    "the innovations sequence as a tool to check whether the filter is working correctly? "
    "Section 2 covers the bioreactor model and the stochastic formulation. Section 3 walks "
    "through the EKF implementation. Section 4 describes the simulation setup. Section 5 "
    "presents the results, and Sections 6 and 7 discuss findings and wrap up."
))

# ── 2. Mathematical Formulation ───────────────────────────────────────────────
story.append(H("2. Mathematical Formulation"))

story.append(H2("2.1 Continuous-Time Process Model"))
story.append(B(
    "The bioreactor state is <b>x</b>(t) = [X<sub>v</sub>(t), S(t), P(t)]<super>T</super>, "
    "where X<sub>v</sub> is viable cell concentration (10<super>6</super> cells/mL), S is "
    "glucose (g/L), and P is product titer (g/L). The dynamics follow a standard fed-batch "
    "ODE model:"
))
story.append(EQ("dX<sub>v</sub>/dt = \u03bc(S) X<sub>v</sub> \u2212 k<sub>d</sub> X<sub>v</sub>"))
story.append(EQ(
    "dS/dt = \u2212\u03bc(S) X<sub>v</sub> / Y<sub>x/s</sub> "
    "\u2212 m<sub>s</sub> X<sub>v</sub> + F<sub>s</sub>(t) / V(t)"
))
story.append(EQ("dP/dt = q<sub>p</sub> X<sub>v</sub>"))
story.append(B(
    "where the specific growth rate follows Monod kinetics: "
    "\u03bc(S) = \u03bc<sub>max</sub> S / (K<sub>s</sub> + S). "
    "The parameter values used are: \u03bc<sub>max</sub> = 0.035 h<super>\u22121</super>, "
    "K<sub>s</sub> = 0.5 g/L, k<sub>d</sub> = 0.003 h<super>\u22121</super>, "
    "Y<sub>x/s</sub> = 2.5, "
    "m<sub>s</sub> = 0.005 g\u00b7g<super>\u22121</super>\u00b7h<super>\u22121</super>, and "
    "q<sub>p</sub> = 0.01 g\u00b7cell<super>\u22121</super>\u00b7h<super>\u22121</super>. "
    "The feed F<sub>s</sub>(t) is a Gaussian-smoothed bolus every 24 hours starting at "
    "t = 48 h, adding 5% volume at 400 g/L each time."
))

story.append(H2("2.2 Stochastic Discrete-Time Representation"))
story.append(B(
    "To apply the Kalman filter, I discretized the system and added noise terms to get the "
    "standard stochastic state-space form:"
))
story.append(EQ(
    "<b>x</b><sub>k+1</sub> = f(<b>x</b><sub>k</sub>, u<sub>k</sub>) + <b>w</b><sub>k</sub>,"
    "   <b>w</b><sub>k</sub> ~ N(<b>0</b>, Q)"
))
story.append(EQ(
    "<b>z</b><sub>k</sub> = h(<b>x</b><sub>k</sub>) + <b>v</b><sub>k</sub>,"
    "   <b>v</b><sub>k</sub> ~ N(<b>0</b>, R)"
))
story.append(B(
    "The function f(\u00b7) is the nonlinear state transition computed using RK4 over "
    "\u0394t = 0.5 h, and h(\u00b7) maps states to measurements. The process noise Q is "
    "meant to capture model uncertainty. This setup is the discrete-time analog of the "
    "Kalman\u2013Bucy filter: in the continuous limit, Q approaches "
    "G\u03a3G<super>T</super>\u0394t where \u03a3 is the diffusion coefficient of the "
    "underlying Wiener process."
))

story.append(H2("2.3 Measurement Model and Sensor Fusion"))
story.append(B(
    "The filter fuses two types of measurements. Online sensors run every 0.5 h: capacitance "
    "(z<sub>cap</sub> = \u03b1 X<sub>v</sub> + noise, \u03b1 = 1.5, "
    "\u03c3<sub>cap</sub> = 0.6) and Raman spectroscopy "
    "(z<sub>ram</sub> = \u03b2 S + noise, \u03b2 = 0.8, \u03c3<sub>ram</sub> = 0.5). "
    "Offline assays of X<sub>v</sub>, S, and P are available every 24 h with lower noise "
    "(\u03c3<sub>VCC</sub> = 0.15, \u03c3<sub>gluc</sub> = 0.20, "
    "\u03c3<sub>titer</sub> = 0.10). When both types are available at the same time step, "
    "I stack them into a 5x1 vector with a block-diagonal R so the filter processes them together."
))

story.append(H2("2.4 Martingale Structure of the Innovations"))
story.append(B(
    "The innovations at each step are \u03bd<sub>k</sub> = z<sub>k</sub> \u2212 "
    "h(x&#x302;<sub>k|k-1</sub>). When the filter model is correct, "
    "\u03bd<sub>k</sub> should form a martingale difference sequence: "
    "E[\u03bd<sub>k</sub> | F<sub>k-1</sub>] = 0. This means the innovations carry no "
    "predictable information, only unpredictable noise. If they are autocorrelated or have "
    "a nonzero mean, something is wrong with the model or noise settings. The normalized "
    "innovations \u03bd&#x0305;<sub>k</sub> = S<sub>k</sub><super>-1/2</super> "
    "\u03bd<sub>k</sub> should look like i.i.d. N(0, I) if things are working correctly, "
    "which we can check with whiteness tests."
))

# ── 3. EKF Implementation ─────────────────────────────────────────────────────
story.append(H("3. Extended Kalman Filter Implementation"))

story.append(H2("3.1 Predict-Update Recursion"))
story.append(B(
    "Since the bioreactor model is nonlinear, I used the EKF which linearizes f(\u00b7) and "
    "h(\u00b7) at each time step. The predict step uses RK4 for the state and the "
    "Euler-discretized Jacobian for the covariance:"
))
story.append(EQ(
    "x&#x302;<sub>k|k-1</sub> = f(x&#x302;<sub>k-1|k-1</sub>, u<sub>k-1</sub>)   [RK4]"
))
story.append(EQ(
    "P<sub>k|k-1</sub> = F<sub>k-1</sub> P<sub>k-1|k-1</sub> "
    "F<sub>k-1</sub><super>T</super> + Q"
))
story.append(B(
    "For the update, I compute the Kalman gain "
    "K<sub>k</sub> = P<sub>k|k-1</sub> H<sub>k</sub><super>T</super> "
    "S<sub>k</sub><super>-1</super> and then update both state and covariance. "
    "I used the Joseph form for the covariance update to keep it numerically stable: "
    "P<sub>k|k</sub> = (I \u2212 K<sub>k</sub> H<sub>k</sub>) P<sub>k|k-1</sub> "
    "(I \u2212 K<sub>k</sub> H<sub>k</sub>)<super>T</super> + "
    "K<sub>k</sub> R K<sub>k</sub><super>T</super>. "
    "This guarantees the covariance stays positive semi-definite even after many iterations."
))

story.append(H2("3.2 Analytical Jacobian for Monod Kinetics"))
story.append(B(
    "Rather than using numerical differentiation, I worked out the analytical Jacobian of the "
    "continuous-time system. The tricky part is the Monod term, which gives "
    "\u2202\u03bc/\u2202S = \u03bc<sub>max</sub> K<sub>s</sub> / "
    "(K<sub>s</sub> + S)<super>2</super>. The Jacobian rows are:"
))
story.append(EQ(
    "J[1,1] = \u03bc \u2212 k<sub>d</sub>,   "
    "J[1,2] = (\u2202\u03bc/\u2202S) X<sub>v</sub>,   J[1,3] = 0"
))
story.append(EQ(
    "J[2,1] = \u2212\u03bc/Y<sub>x/s</sub> \u2212 m<sub>s</sub>,   "
    "J[2,2] = \u2212(\u2202\u03bc/\u2202S) X<sub>v</sub> / Y<sub>x/s</sub>,   J[2,3] = 0"
))
story.append(EQ("J[3,1] = q<sub>p</sub>,   J[3,2] = 0,   J[3,3] = 0"))
story.append(B(
    "The state-transition Jacobian is then F = I + \u0394t J (first-order Euler). One thing "
    "worth noting is that the off-diagonal coupling between X<sub>v</sub> and S means "
    "estimation errors in one state bleed into the other through the Monod term."
))

story.append(H2("3.3 Mixed-Frequency Measurement Fusion"))
story.append(B(
    "At each time step, the filter checks which measurements are available. If only online "
    "measurements are there, it uses a 2x1 measurement vector. If only offline assays are "
    "available, it uses a 3x1 vector. If both coincide (every 24 hours), it fuses all five "
    "measurements in one update step. This naturally handles the different sampling rates "
    "without any interpolation."
))

# ── 4. Simulation Setup ───────────────────────────────────────────────────────
story.append(H("4. Simulation Setup"))
story.append(B(
    "I generated the ground truth by integrating the ODE system using SciPy's RK45 solver "
    "with tight tolerances (rtol = 10<super>\u22128</super>, atol = 10<super>\u221210</super>) "
    "over 336 hours (14 days), giving 673 time points at \u0394t = 0.5 h. Initial conditions "
    "were X<sub>v</sub>(0) = 0.5, S(0) = 6.0 g/L, and P(0) = 0 g/L."
))
story.append(B(
    "To test convergence, I started the filter with a 20% low initial guess on X<sub>v</sub> "
    "and a 20% high guess on S, with initial covariance P<sub>0</sub> = diag(0.1, 1.0, 0.01). "
    "Measurements were generated by adding Gaussian noise to the true trajectory at the "
    "appropriate sampling rates (fixed random seed throughout). The baseline process noise was "
    "Q = diag(0.001, 0.01, 0.0001)."
))

# ── 5. Results ────────────────────────────────────────────────────────────────
story.append(H("5. Results"))

story.append(H2("5.1 Baseline EKF Performance"))
story.append(B(
    "Figure 1 shows the EKF estimates alongside the true trajectory and measurements for "
    "all three states. The filter recovers from its initial offset fairly quickly and stays "
    "close to the true values for the full 14 days."
))
story += fig(
    "ekf_baseline.png", 6.2 * inch,
    "Figure 1. EKF state estimation over the 14-day fed-batch run. Top: viable cell "
    "concentration with capacitance online measurements (divided by \u03b1) and offline VCC "
    "assays. Middle: glucose with Raman measurements (divided by \u03b2) and offline assays; "
    "the feed boluses show up as step increases. Bottom: titer with offline assays. Blue "
    "shading is the \u00b12\u03c3 confidence region. "
    "RMSE: X<sub>v</sub> = 0.172, S = 0.171, P = 0.055."
)
story.append(SP(4))
story.append(B(
    "The glucose panel is the most interesting to look at because you can clearly see the "
    "filter responding to each feed bolus. The state jumps up, the filter initially has "
    "wider uncertainty, and then tightens back up as it assimilates more online data. The "
    "titer estimate is the cleanest of the three because it only increases over time and "
    "gets anchored every 24 hours by the offline assay. The RMSE on titer (0.055) is much "
    "lower than X<sub>v</sub> and S for that reason."
))

story.append(H2("5.2 Innovations Whiteness Test"))
story.append(B(
    "Figure 2 shows the normalized innovations and their autocorrelation functions for both "
    "online channels. This is the main diagnostic for whether the filter is working correctly."
))
story += fig(
    "innovations_diagnostics.png", 6.2 * inch,
    "Figure 2. Innovations diagnostics. Left: normalized innovations time series for the "
    "capacitance (top) and Raman (bottom) channels. Right: sample ACF with 95% white-noise "
    "confidence bounds (dashed red). Ljung\u2013Box statistics: capacitance LB = 28.8 "
    "(p = 0.093), Raman LB = 28.9 (p = 0.090)."
)
story.append(SP(4))
story.append(B(
    "The normalized innovations look roughly zero-mean and stay within the \u00b12 range most "
    "of the time, which is what you would expect from a standard normal. The ACF plots show "
    "almost all lags are within the 95% confidence bands (\u00b11.96/\u221an), meaning there "
    "is no significant autocorrelation. The Ljung\u2013Box test at lag 20 gives p = 0.093 "
    "for capacitance and p = 0.090 for Raman. Both are above 0.05, so we do not reject the "
    "null hypothesis that the innovations are white. This confirms the martingale property "
    "holds for the baseline filter setup."
))

story.append(H2("5.3 Noise Regime Analysis"))
story.append(B(
    "Figure 3 shows how RMSE changes as I scale the process noise Q from 0.1 to 10 times "
    "the baseline, keeping R fixed."
))
story += fig(
    "noise_sweep.png", 5.5 * inch,
    "Figure 3. EKF RMSE versus process noise scale factor (log scale) for viable cell "
    "concentration (X<sub>v</sub>), glucose (S), and titer (P). Each point is a full "
    "14-day simulation using the same synthetic measurements."
)
story.append(SP(4))
story.append(B(
    "There is a pretty clear tradeoff visible in the results. For X<sub>v</sub> and S, RMSE "
    "stays fairly flat at low Q values, hits a minimum somewhere around scale factor 0.5 to "
    "1.0, then climbs again at higher values. When Q is too small, the filter trusts the ODE "
    "model too much and reacts slowly to feed disturbances. When Q is too large, it starts "
    "chasing the noisy measurements and the estimates get noisier. Titer is a different "
    "story: RMSE increases monotonically with Q-scale, which makes sense because P only "
    "shows up through dP/dt = q<sub>p</sub> X<sub>v</sub>, so any extra noise in the "
    "X<sub>v</sub> estimate gets integrated directly into the titer error."
))
story.append(B(
    "The fact that the baseline Q (scale factor 1.0) sits near the minimum for X<sub>v</sub> "
    "and S suggests it was set reasonably well to begin with."
))

# ── 6. Discussion ─────────────────────────────────────────────────────────────
story.append(H("6. Discussion"))

story.append(H2("6.1 Connection to SDE Theory"))
story.append(B(
    "The EKF implemented here is the discrete-time approximation of the Kalman\u2013Bucy "
    "filter, which is the continuous-time solution to optimal filtering for SDE systems. "
    "In continuous time the system looks like d<b>x</b> = f(<b>x</b>, t)dt + G dW<sub>t</sub> "
    "with observations d<b>z</b> = h(<b>x</b>)dt + dV<sub>t</sub>, and the optimal filter "
    "has to solve the Zakai equation for the conditional density. For Gaussian systems this "
    "simplifies down to ODEs for the mean and covariance, which is the Kalman\u2013Bucy "
    "filter. The EKF gives you the same thing in discrete time using local linearizations."
))
story.append(B(
    "The innovations \u03bd<sub>k</sub> are the discrete-time version of the It\u014d "
    "integral d\u03b9<sub>t</sub> = dz<sub>t</sub> \u2212 h(x&#x302;<sub>t</sub>)dt, "
    "which appears in the Kalman\u2013Bucy gain term. Checking that E[d\u03b9<sub>t</sub> | "
    "F<sub>t</sub><super>\u2212</super>] = 0 in the discrete case via the Ljung\u2013Box "
    "test is the same idea, just applied to the sample innovations sequence."
))

story.append(H2("6.2 Observability and Sensor Design"))
story.append(B(
    "With both online and offline sensors available, all three states are observable. "
    "Titer P is the one that benefits most from offline assays, since the only way to "
    "directly correct the titer estimate is from the lab measurement every 24 hours. Between "
    "assays, the filter relies on integrating q<sub>p</sub> X<sub>v</sub>, which means errors "
    "in X<sub>v</sub> accumulate into the titer estimate over time. The offline anchors help "
    "reset this drift."
))
story.append(B(
    "The Monod coupling in the Jacobian means X<sub>v</sub> and S estimation errors are "
    "linked. This cross-coupling is probably why the optimal Q-scale is slightly different "
    "for X<sub>v</sub> and S in the noise sweep."
))

story.append(H2("6.3 Limitations"))
story.append(B(
    "A few things could be improved. The Euler Jacobian discretization (F = I + \u0394t J) "
    "is only first-order accurate and could accumulate error over the 14-day run. The filter "
    "also assumes Q and R are known exactly, which would not be the case in a real bioreactor "
    "where you would need some form of adaptive noise estimation. And the feed profile "
    "F<sub>s</sub>(t) is treated as perfectly known here, which is an idealization since pump "
    "errors and feed concentration uncertainty would also need to be accounted for in practice."
))

# ── 7. Conclusion ─────────────────────────────────────────────────────────────
story.append(H("7. Conclusion"))
story.append(B(
    "This project walked through applying the EKF to a simulated fed-batch bioreactor and "
    "connecting it back to the stochastic process theory covered in the course. A few key "
    "takeaways:"
))
for bullet in [
    "The EKF with RK4 propagation and the analytical Monod Jacobian tracked all three "
    "states reasonably well, with baseline RMSE of 0.172 (X<sub>v</sub>), 0.171 (S), and "
    "0.055 (P), even starting from a biased initial condition.",

    "The innovations whiteness test (p \u2248 0.09 for both channels) confirmed the martingale "
    "property holds for the baseline filter, which connects directly to the theory of optimal "
    "filtering and the innovations representation from class.",

    "The noise sweep showed that estimation accuracy is sensitive to how Q is set. Too "
    "small and the filter is too rigid; too large and it gets noisy. Titer is especially "
    "sensitive because errors in X<sub>v</sub> integrate into P over time.",

    "Using the Joseph form and handling online and offline measurements separately at each "
    "time step kept the filter numerically stable throughout the full 14-day run.",
]:
    story.append(Paragraph(f"\u2022 {bullet}", bullet_style))

story.append(SP(6))
story.append(B(
    "Overall, this was a good exercise in seeing how the abstract ideas from the course "
    "(the Kalman\u2013Bucy filter, martingale innovations, It\u014d calculus) translate into "
    "something practical. The bioreactor setting made it concrete and showed that the filter "
    "diagnostics actually give you useful information about whether your noise model is "
    "tuned correctly."
))

# ── References ────────────────────────────────────────────────────────────────
story.append(H("References"))
for ref in [
    "[1] R. E. Kalman, \"A new approach to linear filtering and prediction problems,\" "
    "<i>Journal of Basic Engineering</i>, vol. 82, no. 1, pp. 35\u201345, 1960.",

    "[2] A. H. Jazwinski, <i>Stochastic Processes and Filtering Theory</i>. Academic Press, 1970.",

    "[3] D. Simon, <i>Optimal State Estimation: Kalman, H\u221e, and Nonlinear Approaches</i>. "
    "Wiley-Interscience, 2006.",

    "[4] S. S\u00e4rkk\u00e4, <i>Bayesian Filtering and Smoothing</i>. "
    "Cambridge University Press, 2013.",

    "[5] J. Monod, \"The growth of bacterial cultures,\" "
    "<i>Annual Review of Microbiology</i>, vol. 3, no. 1, pp. 371\u2013394, 1949.",

    "[6] G. Bastin and D. Dochain, <i>On-line Estimation and Adaptive Control of "
    "Bioreactors</i>. Elsevier, 1990.",

    "[7] B. \u00d8ksendal, <i>Stochastic Differential Equations: An Introduction with "
    "Applications</i>, 6th ed. Springer, 2003.",

    "[8] G. M. Ljung and G. E. P. Box, \"On a measure of lack of fit in time series "
    "models,\" <i>Biometrika</i>, vol. 65, no. 2, pp. 297\u2013303, 1978.",

    "[9] A. Gelb (Ed.), <i>Applied Optimal Estimation</i>. MIT Press, 1974.",

    "[10] F. J. Doyle et al., \"Model identification of signal transduction networks from "
    "cell culture assay data,\" <i>Metabolic Engineering</i>, vol. 4, no. 1, "
    "pp. 64\u201376, 2002.",
]:
    story.append(Paragraph(ref, ref_style))

# ── Build ─────────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    str(OUT),
    pagesize=letter,
    leftMargin=1.0 * inch, rightMargin=1.0 * inch,
    topMargin=1.0 * inch,  bottomMargin=1.0 * inch,
    title="EKF for Fed-Batch Bioreactor State Estimation",
    author="Zachary Hatzenbeller",
)
doc.build(story)
print(f"PDF written to: {OUT}")
