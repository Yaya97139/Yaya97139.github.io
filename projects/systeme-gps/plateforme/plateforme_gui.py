#!/usr/bin/env python3
"""
Plateforme interactive de localisation — Fusion TDOA + RSSI
IEMN — Stage 2026
Interface graphique Tkinter + Matplotlib embarqué
"""

import tkinter as tk
import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.lines import Line2D

C = 3e8  # vitesse de la lumière (m/s)

# =============================================================================
# PHYSIQUE
# =============================================================================

def rssi_to_distance(rssi, P0, n, d0=1.0):
    """Modèle Log-Distance : RSSI (dBm) → distance (m)."""
    return d0 * 10 ** ((P0 - rssi) / (10.0 * n))

def fusion_residuals(p, R1, R2, d1, d2, delta_d, w_rssi, w_tdoa):
    """Résidus pondérés pour le solveur de moindres carrés (RSSI + TDOA)."""
    x, y = p
    d1e = np.sqrt((x - R1[0])**2 + (y - R1[1])**2)
    d2e = np.sqrt((x - R2[0])**2 + (y - R2[1])**2)
    return [
        w_rssi * (d1e - d1),
        w_rssi * (d2e - d2),
        w_tdoa * ((d1e - d2e) - delta_d),
    ]

def smart_init(R1, R2, d1, d2):
    """
    Initialisation géométrique (trilatération linéarisée RSSI) pour éviter
    le minimum local sur Y=0 avec Levenberg-Marquardt.
    """
    BL = np.linalg.norm(R2 - R1)
    if BL < 1e-9:
        return (R1 + R2) / 2.0
    x0 = (d1**2 - d2**2 + BL**2) / (2.0 * BL)
    y2 = d1**2 - x0**2
    y0 = np.sqrt(max(y2, 1.0))
    direction = (R2 - R1) / BL
    perp = np.array([-direction[1], direction[0]])
    return R1 + x0 * direction + y0 * perp


def circle_intersections(R1, R2, d1, d2):
    """
    Calcule analytiquement les 0, 1 ou 2 intersections de deux cercles RSSI.
    Cercle1 : centre R1, rayon d1 | Cercle2 : centre R2, rayon d2.
    Retourne une liste de points (array 2D).
    """
    d = np.linalg.norm(R2 - R1)
    if d < 1e-9:
        return []
    # Pas d'intersection si cercles disjoints ou l'un contient l'autre
    if d > d1 + d2 + 1e-9 or d < abs(d1 - d2) - 1e-9:
        return []
    # Coordonnée 'a' : projection du centre d'intersection sur l'axe R1→R2
    a = (d1**2 - d2**2 + d**2) / (2.0 * d)
    h2 = max(d1**2 - a**2, 0.0)
    h = np.sqrt(h2)
    direction = (R2 - R1) / d
    perp = np.array([-direction[1], direction[0]])
    mid = R1 + a * direction
    p1 = mid + h * perp   # demi-plan Y > 0 (convention)
    p2 = mid - h * perp
    if h < 1e-6:           # cercles tangents : un seul point
        return [p1]
    return [p1, p2]


def tdoa_residual(p, R1, R2, delta_d):
    """Ecart entre la différence de distances géométrique et delta_d mesuré."""
    return np.linalg.norm(p - R1) - np.linalg.norm(p - R2) - delta_d

# =============================================================================
# COULEURS
# =============================================================================
BG_DARK   = '#0d1520'
BG_PANEL  = '#111e2e'
BG_SECT   = '#152641'
BG_ENTRY  = '#0a1628'
FG_WHITE  = '#e8edf2'
FG_GREY   = '#7a8fa6'
FG_BLUE   = '#aad4f5'
IEMN_BLUE = '#003E7E'
COL_R1    = '#00e676'
COL_R2    = '#40c4ff'
COL_HYP   = '#ff5252'
COL_EST   = '#FFB300'
COL_TRUE  = '#ffffff'

# =============================================================================
# APPLICATION
# =============================================================================

class LocalisationApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Plateforme Localisation  ·  Fusion TDOA + RSSI  ·  IEMN 2026")
        self.configure(bg=BG_DARK)
        self.geometry("1280x760")
        self.minsize(1000, 640)
        self._build_ui()
        self._run_calculation()   # trace initial automatique

    # ── Construction de l'interface ──────────────────────────────────────────

    def _build_ui(self):
        # En-tête
        hdr = tk.Frame(self, bg=IEMN_BLUE, height=44)
        hdr.pack(fill='x')
        tk.Label(hdr, text="IEMN  ·  Fusion TDOA + RSSI  ·  Localisation 2D",
                 bg=IEMN_BLUE, fg='white',
                 font=('Helvetica', 13, 'bold'), pady=10).pack(side='left', padx=16)
        tk.Label(hdr, text="Université de Valenciennes — Stage 2026",
                 bg=IEMN_BLUE, fg='#9ec8f5',
                 font=('Helvetica', 9, 'italic')).pack(side='right', padx=16)

        # Conteneur principal
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill='both', expand=True, padx=8, pady=8)

        # ── Panneau gauche (paramètres) ──────────────────────────────────────
        left = tk.Frame(body, bg=BG_PANEL, width=320, relief='flat')
        left.pack(side='left', fill='y', padx=(0, 8))
        left.pack_propagate(False)

        scroll_canvas = tk.Canvas(left, bg=BG_PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(left, orient='vertical', command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        scroll_canvas.pack(side='left', fill='both', expand=True)
        inner = tk.Frame(scroll_canvas, bg=BG_PANEL)
        inner_id = scroll_canvas.create_window((0, 0), window=inner, anchor='nw')

        def on_configure(e):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox('all'))
            scroll_canvas.itemconfig(inner_id, width=scroll_canvas.winfo_width())
        inner.bind('<Configure>', on_configure)
        scroll_canvas.bind('<Configure>', lambda e: scroll_canvas.itemconfig(inner_id, width=e.width))
        scroll_canvas.bind_all("<MouseWheel>", lambda e: scroll_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        P = inner  # raccourci

        # Section Récepteurs
        self._section(P, "📡  Configuration des Récepteurs")
        row = self._row(P)
        self.r1x = self._field(row, "R1   x", "0.0")
        self.r1y = self._field(row, "y", "0.0")
        row2 = self._row(P)
        self.r2x = self._field(row2, "R2   x", "8.0")
        self.r2y = self._field(row2, "y", "0.0")
        self.lbl_bl = tk.Label(P, text="Baseline : 8.00 m",
                                bg=BG_PANEL, fg=COL_R2,
                                font=('Courier', 9, 'bold'))
        self.lbl_bl.pack(anchor='w', padx=12, pady=(0, 4))
        for e in (self.r1x, self.r1y, self.r2x, self.r2y):
            e.bind('<FocusOut>', self._update_bl)
            e.bind('<Return>',   self._run_calculation)

        # Section RSSI
        self._section(P, "📶  Mesures RSSI (dBm)")
        row3 = self._row(P)
        self.rssi1 = self._field(row3, "RSSI 1", "-58.3")
        self.rssi2 = self._field(row3, "RSSI 2", "-62.3")
        self._hint(P, "Valeurs typiques indoor : -40 à -90 dBm")

        # Section TDOA
        self._section(P, "⏱  Mesure TDOA (différence de temps)")
        row4 = self._row(P)
        self.tdoa_ns = self._field(row4, "TDOA (ns)", "-8.08")
        self._hint(P, "Valeur absolue |t_long − t_court| · 1 ns → Δd ≈ 30 cm")

        # Section Modèle path-loss
        self._section(P, "🌐  Modèle de Propagation (Path-Loss)")
        row5 = self._row(P)
        self.P0_val = self._field(row5, "P₀ réf. (dBm)", "-40.0", w=9)
        self.n_val  = self._field(row5, "n", "2.5", w=5)
        self._hint(P, "n : 2 (espace libre) · 2.5–4 (indoor)")

        # Section Pondération  
        self._section(P, "⚖  Pondération de la Fusion")
        row6 = self._row(P)
        self.w_rssi = self._field(row6, "w RSSI", "1.0", w=7)
        self.w_tdoa = self._field(row6, "w TDOA", "2.0", w=7)
        self._hint(P, "Augmenter w TDOA si UWB · Diminuer si NLOS")

        # Section position réelle
        self._section(P, "🎯  Vraie Position de l'Émetteur (optionnel)")
        self.chk_var = tk.BooleanVar(value=True)
        chk_row = self._row(P)
        tk.Checkbutton(chk_row, text="Afficher", variable=self.chk_var,
                       bg=BG_PANEL, fg=FG_WHITE, selectcolor=BG_DARK,
                       activebackground=BG_PANEL, font=('Helvetica', 9),
                       command=self._run_calculation).pack(side='left', padx=4)
        self.true_x = self._field(chk_row, "x", "2.0", w=7)
        self.true_y = self._field(chk_row, "y", "5.0", w=7)

        # Bouton Calculer
        btn = tk.Button(P, text="▶   CALCULER & VISUALISER",
                        bg=IEMN_BLUE, fg='white',
                        font=('Helvetica', 11, 'bold'),
                        relief='flat', cursor='hand2', pady=10,
                        activebackground='#005cb8', activeforeground='white',
                        command=self._run_calculation)
        btn.pack(fill='x', padx=8, pady=(14, 6))
        for e in (self.rssi1, self.rssi2, self.tdoa_ns, self.P0_val,
                  self.n_val, self.w_rssi, self.w_tdoa, self.true_x, self.true_y):
            e.bind('<Return>', self._run_calculation)

        # Zone résultats
        self._section(P, "📊  Résultats")
        self.txt_res = tk.Text(P, height=10, bg=BG_ENTRY, fg=COL_R2,
                               font=('Courier', 9), relief='flat',
                               state='disabled', padx=8, pady=6,
                               insertbackground='white')
        self.txt_res.pack(fill='x', padx=8, pady=(0, 10))

        # ── Panneau droite (figure Matplotlib) ──────────────────────────────
        right = tk.Frame(body, bg=BG_DARK)
        right.pack(side='left', fill='both', expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7.5, 6.5))
        self.fig.patch.set_facecolor(BG_DARK)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        toolbar_frame = tk.Frame(right, bg=BG_DARK)
        toolbar_frame.pack(fill='x')
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.config(bg=BG_DARK)
        toolbar.update()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    # ── Widgets utilitaires ─────────────────────────────────────────────────

    def _section(self, p, title):
        tk.Label(p, text=title, bg=BG_SECT, fg=FG_BLUE,
                 font=('Helvetica', 9, 'bold'), anchor='w', pady=5
                 ).pack(fill='x', padx=0, pady=(8, 2))

    def _row(self, p):
        f = tk.Frame(p, bg=BG_PANEL)
        f.pack(fill='x', padx=8, pady=2)
        return f

    def _field(self, parent, label, default, w=8):
        tk.Label(parent, text=label, bg=BG_PANEL, fg=FG_GREY,
                 font=('Helvetica', 9)).pack(side='left', padx=(4, 2))
        e = tk.Entry(parent, width=w, bg=BG_ENTRY, fg=FG_WHITE,
                     insertbackground=FG_WHITE, relief='flat',
                     font=('Courier', 10), justify='center',
                     highlightthickness=1, highlightcolor=IEMN_BLUE,
                     highlightbackground='#223344')
        e.insert(0, default)
        e.pack(side='left', padx=(0, 6), ipady=3)
        return e

    def _hint(self, p, text):
        tk.Label(p, text=text, bg=BG_PANEL, fg='#556677',
                 font=('Helvetica', 8, 'italic'),
                 anchor='w').pack(fill='x', padx=12, pady=(0, 2))

    def _get(self, e, fallback=0.0):
        try:
            return float(e.get())
        except (ValueError, tk.TclError):
            return fallback

    def _update_bl(self, event=None):
        R1 = np.array([self._get(self.r1x), self._get(self.r1y)])
        R2 = np.array([self._get(self.r2x), self._get(self.r2y)])
        bl = np.linalg.norm(R2 - R1)
        self.lbl_bl.config(text=f"Baseline : {bl:.2f} m")

    def _set_results(self, lines):
        self.txt_res.config(state='normal')
        self.txt_res.delete('1.0', 'end')
        self.txt_res.insert('end', "\n".join(lines))
        self.txt_res.config(state='disabled')

    # ── Calcul principal ─────────────────────────────────────────────────────

    def _run_calculation(self, event=None):
        R1 = np.array([self._get(self.r1x), self._get(self.r1y)])
        R2 = np.array([self._get(self.r2x), self._get(self.r2y)])
        rssi1  = self._get(self.rssi1, -63.0)
        rssi2  = self._get(self.rssi2, -59.5)
        tdoa_s = self._get(self.tdoa_ns, 1.0) * 1e-9
        P0     = self._get(self.P0_val, -40.0)
        n      = self._get(self.n_val,  2.5)
        w_r    = self._get(self.w_rssi, 0.5)
        w_t    = self._get(self.w_tdoa, 2.0)
        self._update_bl()

        d1      = rssi_to_distance(rssi1, P0, n)
        d2      = rssi_to_distance(rssi2, P0, n)
        delta_d = C * abs(tdoa_s)   # temps toujours ≥ 0 : |t_long − t_court|

        # ── Phase 1 : Intersections analytiques des cercles RSSI ─────────────
        candidates = circle_intersections(R1, R2, d1, d2)

        # Résidus TDOA pour chaque candidat (|D1-D2 - Δd| en m)
        def score(p):
            return abs(tdoa_residual(p, R1, R2, delta_d))

        status_msg = ""
        ep = None

        if candidates:
            # ── Phase 2 : Classer les candidats par résidu TDOA ─────────────
            candidates_sorted = sorted(candidates, key=score)
            best_cand = candidates_sorted[0]

            if score(best_cand) < 0.05:          # < 5 cm : déjà sur l'intersection
                ep = best_cand
                status_msg = (f"✓ Intersection exacte  "
                              f"|Δd_résidu| = {score(ep)*100:.1f} cm")
            else:
                # ── Phase 3 : Multi-start LM depuis chaque candidat ──────────
                # + le point géométrique de smart_init comme filet de sécurité
                starts = candidates_sorted + [smart_init(R1, R2, d1, d2)]
                best_cost, best_ep = np.inf, None
                for p_start in starts:
                    try:
                        res = least_squares(
                            fusion_residuals, p_start,
                            args=(R1, R2, d1, d2, delta_d, w_r, w_t),
                            method='lm'
                        )
                        cost = float(np.sum(res.fun ** 2))
                        if cost < best_cost:
                            best_cost, best_ep = cost, res.x
                    except Exception:
                        continue
                ep = best_ep if best_ep is not None else best_cand
                status_msg = (f"↪ LM multi-start  "
                              f"|Δd_résidu| = {score(ep)*100:.1f} cm")
        else:
            # Aucune intersection cercle-cercle : mesures trop bruitées/incompatibles
            p0 = smart_init(R1, R2, d1, d2)
            res = least_squares(fusion_residuals, p0,
                                args=(R1, R2, d1, d2, delta_d, w_r, w_t),
                                method='lm')
            ep = res.x
            status_msg = (f"⚠ Cercles non-sécants  "
                          f"|Δd_résidu| = {score(ep)*100:.1f} cm")

        # ── Résultats texte ───────────────────────────────────────────────────
        bl = np.linalg.norm(R2 - R1)
        residual_tdoa_cm = score(ep) * 100
        # Qualité : ratio erreur/delta_d (ou /1 si delta_d ≈ 0)
        lines = [
            f"━━━  MESURES TRAITÉES  ━━━",
            f"d₁  (RSSI 1)  = {d1:.3f} m",
            f"d₂  (RSSI 2)  = {d2:.3f} m",
            f"Δd  (TDOA)    = {delta_d:.4f} m",
            f"Baseline R1→R2 = {bl:.2f} m",
            f"Candidats cercles : {len(candidates)}",
            f"",
            f"━━━  POSITION ESTIMÉE  ━━━",
            f"X = {ep[0]:.4f} m",
            f"Y = {ep[1]:.4f} m",
            f"",
            f"[Δd résidu TDOA] = {residual_tdoa_cm:.2f} cm",
            f"{status_msg}",
        ]
        if self.chk_var.get():
            tp  = np.array([self._get(self.true_x), self._get(self.true_y)])
            err = np.linalg.norm(ep - tp)
            lines += [f"", f"► Erreur vs vraie pos. = {err:.4f} m"]
        self._set_results(lines)

        # Mise à jour du graphique
        self._draw(R1, R2, d1, d2, delta_d, ep, candidates)

    # ── Tracé Matplotlib ─────────────────────────────────────────────────────

    def _draw(self, R1, R2, d1, d2, delta_d, ep, candidates=None):
        ax = self.ax
        ax.clear()
        ax.set_facecolor('#060e1a')

        # Zone de calcul (auto-adaptative)
        margin = max(d1, d2, np.linalg.norm(R2 - R1)) * 1.6 + 2
        cx, cy = (R1 + R2) / 2
        xs = np.linspace(cx - margin, cx + margin, 700)
        ys = np.linspace(cy - margin, cy + margin, 700)
        X, Y = np.meshgrid(xs, ys)
        D1g  = np.sqrt((X - R1[0])**2 + (Y - R1[1])**2)
        D2g  = np.sqrt((X - R2[0])**2 + (Y - R2[1])**2)

        # ── Cercles RSSI (+ zone d'incertitude ±15%) ────────────────────────
        tol = 0.15
        for radius, center, color in [(d1, R1, COL_R1), (d2, R2, COL_R2)]:
            ax.add_patch(plt.Circle(center, radius*(1+tol), color=color,
                                    fill=True, alpha=0.07, linewidth=0))
            ax.add_patch(plt.Circle(center, radius*(1-tol), color='#060e1a',
                                    fill=True, linewidth=0))
            ax.add_patch(plt.Circle(center, radius, color=color,
                                    fill=False, linewidth=2.2, alpha=0.9))

        # ── Hyperbole TDOA ───────────────────────────────────────────────────
        tol_tdoa = abs(delta_d) * 0.12 + 0.15
        ax.contourf(X, Y, D1g - D2g,
                    levels=[delta_d - tol_tdoa, delta_d + tol_tdoa],
                    colors=[COL_HYP], alpha=0.15)
        ax.contour(X, Y, D1g - D2g, levels=[delta_d],
                   colors=[COL_HYP], linewidths=2.5, alpha=0.95)

        # ── Base Line ────────────────────────────────────────────────────────
        ax.plot([R1[0], R2[0]], [R1[1], R2[1]],
                color='#445566', linestyle=':', linewidth=1.5)
        bl = np.linalg.norm(R2 - R1)
        mid = (R1 + R2) / 2
        ax.text(mid[0], mid[1] - 0.5, f'BL = {bl:.2f} m',
                color='#445566', fontsize=8, ha='center', va='top')

        # ── Récepteurs ───────────────────────────────────────────────────────
        ax.scatter(*R1, s=140, color=COL_R1, zorder=6, marker='s', edgecolors='white', linewidths=1)
        ax.scatter(*R2, s=140, color=COL_R2, zorder=6, marker='s', edgecolors='white', linewidths=1)
        ax.text(R1[0]+0.18, R1[1]+0.35, 'R1', color=COL_R1,
                fontsize=11, fontweight='bold', zorder=7)
        ax.text(R2[0]+0.18, R2[1]+0.35, 'R2', color=COL_R2,
                fontsize=11, fontweight='bold', zorder=7)

        # ── Vraie position ───────────────────────────────────────────────────
        if self.chk_var.get():
            tp = np.array([self._get(self.true_x), self._get(self.true_y)])
            ax.scatter(*tp, s=200, color=COL_TRUE, zorder=8, marker='*',
                       edgecolors='#cccccc', linewidths=0.8, label='Vraie position')
            ax.text(tp[0]+0.2, tp[1]+0.35, 'Cible réelle',
                    color=COL_TRUE, fontsize=8.5, fontstyle='italic')
            # Ligne d'erreur
            ax.plot([tp[0], ep[0]], [tp[1], ep[1]],
                    color='#ff8800', linestyle='--', linewidth=1.2, alpha=0.6)
        # ── Candidats cercle-cercle (non sélectionnés) ───────────────────────
        if candidates:
            for i, cand in enumerate(candidates):
                # Affiche le rejeté en gris, le sélectionné est déjà montré
                dist_to_ep = np.linalg.norm(np.array(cand) - np.array(ep))
                if dist_to_ep > 0.1:   # candidat non choisi
                    ax.scatter(*cand, s=80, color='#888888', zorder=7,
                               marker='o', edgecolors='white', linewidths=0.8,
                               alpha=0.65)
                    ax.text(cand[0]+0.18, cand[1]+0.35,
                            f'Candidat {i+1}\n(rejeté)',
                            color='#666666', fontsize=7, fontstyle='italic')
                else:                  # candidat choisi = marquer l'intersection exacte
                    ax.scatter(*cand, s=130, color='#ffffff', zorder=8,
                               marker='+', linewidths=2.5, alpha=0.9)
        # ── Position estimée fusion ──────────────────────────────────────────
        ax.scatter(*ep, s=200, color=COL_EST, zorder=9, marker='o',
                   edgecolors='white', linewidths=1.8)
        ax.text(ep[0] + 0.2, ep[1] - 0.6,
                f'Estimé\n({ep[0]:.2f}, {ep[1]:.2f}) m',
                color=COL_EST, fontsize=8.5, fontweight='bold', va='top')

        # ── Mise en forme des axes ───────────────────────────────────────────
        ax.set_xlabel('X (m)', color=FG_GREY, fontsize=10)
        ax.set_ylabel('Y (m)', color=FG_GREY, fontsize=10)
        ax.tick_params(colors=FG_GREY, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor('#1e3050')
        ax.set_title('Localisation par Fusion  TDOA + RSSI',
                     color='white', fontsize=13, fontweight='bold', pad=12)
        ax.set_aspect('equal', 'box')
        ax.grid(True, color='#1a2d40', linewidth=0.8, linestyle=':')

        # ── Légende ──────────────────────────────────────────────────────────
        handles = [
            Line2D([0],[0], color=COL_R1, lw=2.2,
                   label=f'Cercle RSSI 1   r = {d1:.2f} m'),
            Line2D([0],[0], color=COL_R2, lw=2.2, linestyle='--',
                   label=f'Cercle RSSI 2   r = {d2:.2f} m'),
            Line2D([0],[0], color=COL_HYP, lw=2.5,
                   label=f'Hyperbole TDOA  Δd = {delta_d:.3f} m'),
            Line2D([0],[0], marker='o', color=COL_EST, lw=0, ms=9,
                   label=f'Position estimée  ({ep[0]:.2f}, {ep[1]:.2f}) m'),
        ]
        if self.chk_var.get():
            tp = np.array([self._get(self.true_x), self._get(self.true_y)])
            err = np.linalg.norm(ep - tp)
            handles.append(
                Line2D([0],[0], marker='*', color=COL_TRUE, lw=0, ms=11,
                       label=f'Vraie position    erreur = {err:.3f} m')
            )
        ax.legend(handles=handles, facecolor='#0d1e30', edgecolor='#1e3050',
                  labelcolor='white', fontsize=8, loc='upper right',
                  framealpha=0.9)

        self.fig.tight_layout()
        self.canvas.draw()


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================
if __name__ == "__main__":
    app = LocalisationApp()
    app.mainloop()
