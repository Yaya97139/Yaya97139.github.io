import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

# =============================================================================
# 1. PARAMÈTRES DU SYSTÈME ET MODÈLES
# =============================================================================

# Vitesse de la lumière (en m/s)
C = 3e8

def rssi_to_distance(rssi, P0=-40, n=2.5, d0=1.0):
    """
    Convertit la puissance RSSI en distance estimée selon le modèle de path-loss Log-Distance.
    
    :param rssi: Puissance reçue (dBm)
    :param P0: Puissance de référence à la distance d0 (dBm)
    :param n: Exposant de perte de trajet (path loss exponent) - dépend de l'environnement
    :param d0: Distance de référence (m)
    :return: Distance estimée (m)
    """
    return d0 * 10 ** ((P0 - rssi) / (10 * n))

def time_to_distance_diff(delta_t):
    """
    Convertit une différence de temps d'arrivée (TDOA) en différence de distance.
    """
    return C * delta_t

# =============================================================================
# 2. FONCTIONS DE CONST EN VUE DE L'OPTIMISATION (FUSION)
# =============================================================================

def fusion_cost_function(p_est, receivers, d_rssi, delta_d_tdoa, weights):
    """
    Fonction de coût globale combinant RSSI et TDOA pour l'algorithme des moindres carrés.
    
    :param p_est: Position estimée actuelle [x, y]
    :param receivers: Positions des récepteurs [[x1, y1], [x2, y2]]
    :param d_rssi: Distances estimées par le RSSI [d1, d2]
    :param delta_d_tdoa: Différence de distance estimée par le TDOA (d1 - d2)
    :param weights: Poids pour chaque mesure [w_rssi1, w_rssi2, w_tdoa]
    :return: Tableau des résidus de chaque contrainte
    """
    x, y = p_est
    R1, R2 = receivers

    # Distances depuis le point estimé p_est aux récepteurs
    d1_est = np.sqrt((x - R1[0])**2 + (y - R1[1])**2)
    d2_est = np.sqrt((x - R2[0])**2 + (y - R2[1])**2)

    residuals = []
    
    # Résidus RSSI : la distance géométrique doit correspondre à la distance RSSI
    residuals.append(weights[0] * (d1_est - d_rssi[0]))
    residuals.append(weights[1] * (d2_est - d_rssi[1]))
    
    # Résidu TDOA : la différence de distance géométrique doit correspondre à delta_d mesuré
    residuals.append(weights[2] * ((d1_est - d2_est) - delta_d_tdoa))
    
    return np.array(residuals)

# =============================================================================
# 3. PLATEFORME INTERACTIVE / VISUALISATION
# =============================================================================

def resolve_position_fusion(receivers, rssi_measurements, tdoa_measurement, P0, n, w_rssi=1.0, w_tdoa=2.0, true_pos=None):
    """
    Résout et trace la position en fusionnant les données TDOA et RSSI pour 2 récepteurs.
    """
    R1, R2 = np.array(receivers[0]), np.array(receivers[1])
    
    # 1. Traitement des mesures
    # RSSI vers Distances (Cercles)
    d1_rssi = rssi_to_distance(rssi_measurements[0], P0=P0, n=n)
    d2_rssi = rssi_to_distance(rssi_measurements[1], P0=P0, n=n)
    
    # TDOA vers dP (Hyperbole)
    delta_d_tdoa = time_to_distance_diff(tdoa_measurement)
    
    print("--- RÉSULTATS DES MESURES ---")
    print(f"Distance estimée à partir du RSSI 1 : {d1_rssi:.2f} m")
    print(f"Distance estimée à partir du RSSI 2 : {d2_rssi:.2f} m")
    print(f"Différence de distance estimée (TDOA) : {delta_d_tdoa:.2f} m")
    
    # 2. Algorithme de Fusion (Moindres Carrés Non-Linéaires)
    # Initialisation géométrique : on estime x depuis les cercles RSSI (trilatération linéarisée)
    # En soustrayant les équations de cercle de R1 et R2 (sur l'axe X) :
    BL = np.linalg.norm(R2 - R1)  # longueur de la baseline
    if BL > 1e-6:
        x0 = (d1_rssi**2 - d2_rssi**2 + BL**2) / (2 * BL)
        y2_sq = d1_rssi**2 - x0**2
        y0 = np.sqrt(max(y2_sq, 1.0))  # on choisit le demi-plan Y > 0
        # On recentre dans le repère de R1
        direction = (R2 - R1) / BL
        perp = np.array([-direction[1], direction[0]])  # perpendiculaire
        p0 = R1 + x0 * direction + y0 * perp
    else:
        p0 = (R1 + R2) / 2.0
    
    # Définition des poids (on peut accorder plus de confiance au TDOA s'il est de type UWB)
    weights = [w_rssi, w_rssi, w_tdoa]
    
    res = least_squares(
        fusion_cost_function, 
        p0, 
        args=(np.array([R1, R2]), [d1_rssi, d2_rssi], delta_d_tdoa, weights),
        method='lm' # Levenberg-Marquardt
    )
    
    estimated_pos = res.x
    print("\n--- POSITION ESTIMÉE PAR FUSION ---")
    print(f"Coordonnées (X, Y) : ({estimated_pos[0]:.2f} m, {estimated_pos[1]:.2f} m)")
    
    if true_pos is not None:
        erreur = np.linalg.norm(estimated_pos - true_pos)
        print(f"Erreur par rapport à la vraie position : {erreur:.2f} m")

    # 3. Visualisation (Graphique)
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot des récepteurs
    ax.plot(R1[0], R1[1], 's', markersize=10, color='blue', label='Récepteur 1')
    ax.plot(R2[0], R2[1], 's', markersize=10, color='blue', label='Récepteur 2')
    ax.text(R1[0]+0.3, R1[1]+0.3, 'R1', color='blue', fontsize=12, fontweight='bold')
    ax.text(R2[0]+0.3, R2[1]+0.3, 'R2', color='blue', fontsize=12, fontweight='bold')
    
    # Tracer la "Base line" (Ligne entre les récepteurs)
    ax.plot([R1[0], R2[0]], [R1[1], R2[1]], 'k--', alpha=0.5, label='Base Line')
    
    # Tracer les cercles RSSI
    circle1 = plt.Circle(R1, d1_rssi, color='green', fill=False, linestyle='-', linewidth=1.5, alpha=0.7, label=f'Cercle RSSI 1 (r={d1_rssi:.1f}m)')
    circle2 = plt.Circle(R2, d2_rssi, color='green', fill=False, linestyle='--', linewidth=1.5, alpha=0.7, label=f'Cercle RSSI 2 (r={d2_rssi:.1f}m)')
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    
    # Tracer l'hyperbole TDOA (d1 - d2 = delta_d)
    x_range = np.linspace(-15, 15, 400)
    y_range = np.linspace(-15, 15, 400)
    X, Y = np.meshgrid(x_range, y_range)
    D1 = np.sqrt((X - R1[0])**2 + (Y - R1[1])**2)
    D2 = np.sqrt((X - R2[0])**2 + (Y - R2[1])**2)
    
    # L'hyperbole est la courbe de niveau où D1 - D2 = delta_d_tdoa
    ax.contour(X, Y, D1 - D2, levels=[delta_d_tdoa], colors='red', linewidths=2, alpha=0.8)
    # Ajout d'un handle manuel pour la légende (contour.collections dépréciée en mpl 3.8+)
    from matplotlib.lines import Line2D
    hyperbole_handle = Line2D([0], [0], color='red', linewidth=2, label=f'Hyperbole TDOA (Δd={delta_d_tdoa:.2f}m)')
    ax.add_artist(ax.legend(handles=[hyperbole_handle], loc='lower right'))
    
    # Plot de la Vraie position (si connue, ex: environnement de test)
    if true_pos is not None:
        ax.plot(true_pos[0], true_pos[1], '*', markersize=12, color='black', label='Vraie Position Émetteur')
        
    # Plot de la position Estimée par la fusion
    ax.plot(estimated_pos[0], estimated_pos[1], 'o', markersize=12, color='darkorange', label='Position Estimée (Fusion)')
    
    # Finalisation des options graphiques
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(-5, 15)
    ax.set_ylim(-10, 15)
    ax.set_xlabel('Position X (m)')
    ax.set_ylabel('Position Y (m)')
    ax.set_title('Fusion TDOA et RSSI - 2 Récepteurs\nOptimisation Moindres Carrés', fontsize=14, fontweight='bold', color='#003E7E')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # Légende en dehors
    plt.legend(loc='upper right', bbox_to_anchor=(1.45, 1.0))
    plt.tight_layout()
    
    # Sauvegarde et affichage
    plt.savefig('resultat_fusion_tdoa_rssi.png', dpi=300)
    print("\nGraphique généré et sauvegardé sous le nom 'resultat_fusion_tdoa_rssi.png'.")
    plt.show()


# =============================================================================
# 4. EXÉCUTION / SCÉNARIO DE TEST
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print(" PLATEFORME DE LOCALISATION FUSION TDOA + RSSI ")
    print("="*60)
    
    # --- DÉFINITION DE L'ENVIRONNEMENT ---
    # Coordonnées (x, y) de la Baseline (Les 2 récepteurs)
    R1 = [0.0, 0.0]  # Récepteur 1 à l'origine
    R2 = [8.0, 0.0]  # Récepteur 2 sur l'axe X (Base line de 8 mètres)
    recepteurs = [R1, R2]
    
    # Paramètres de l'environnement pour RSSI
    P0_env = -40  # Puissance à 1m en dBm
    n_env = 2.5   # Exposant d'atténuation indoor (typique)
    
    # --- SCÉNARIO SIMULÉ (Pour générer les données si on veut tester) ---
    # Imaginons que la vraie cible est en (4, 6)
    vraie_position = [4.0, 6.0]
    
    # Simulation des "Mesures" (idéales, puis on ajoute un peu d'erreur)
    dist_reelle_1 = np.sqrt((vraie_position[0]-R1[0])**2 + (vraie_position[1]-R1[1])**2) # ~7.21m
    dist_reelle_2 = np.sqrt((vraie_position[0]-R2[0])**2 + (vraie_position[1]-R2[1])**2) # ~7.21m
    
    # 1. On crée des valeurs TDOA bruitées (en nanosecondes -> secondes)
    delta_dist_vrai = dist_reelle_1 - dist_reelle_2 # 0m car équidistant
    # Ajoutons un léger retard mesuré (ex: multi-trajet modéré ou biais synchro)
    delta_dist_mesure = delta_dist_vrai + 0.3 # Biais de +30cm
    temps_tdoa_mesure = delta_dist_mesure / C
    <
    # 2. On crée des valeurs RSSI bruitées
    # Puissance théorique P(d) = P0 - 10*n*log10(d)
    rssi_ideal_1 = P0_env - 10 * n_env * np.log10(dist_reelle_1)
    rssi_ideal_2 = P0_env - 10 * n_env * np.log10(dist_reelle_2)
    # Ajout du bruit ("shadowing" : on perd ou gagne quelques dB)
    rssi_mesure_1 = rssi_ideal_1 - 1.5 # Obstacle -> perte de -1.5 dBm
    rssi_mesure_2 = rssi_ideal_2 + 2.0 # Fading constructif -> +2.0 dBm
    
    print(f"\nConfiguration de l'espace :")
    print(f"R1 : {R1} | R2 : {R2}")
    print(f"\nMesures simulées et introduites dans l'algorithme :")
    print(f"RSSI 1 : {rssi_mesure_1:.1f} dBm")
    print(f"RSSI 2 : {rssi_mesure_2:.1f} dBm")
    print(f"TDOA   : {temps_tdoa_mesure*1e9:.2f} ns")
    
    print("\nLancement de l'algorithme de fusion...")
    
    # Appel de la fonction de la plateforme
    # On donne plus de poids au TDOA (w_tdoa=2.0) par rapport au RSSI (w_rssi=0.5) 
    # car le TDOA UWB est physiquement plus fiable sur cette mesure.
    resolve_position_fusion(
        receivers=recepteurs,
        rssi_measurements=[rssi_mesure_1, rssi_mesure_2],
        tdoa_measurement=temps_tdoa_mesure,
        P0=P0_env,
        n=n_env,
        w_rssi=0.5,
        w_tdoa=2.0,
        true_pos=vraie_position
    )
