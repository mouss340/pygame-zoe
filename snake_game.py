"""
====================================================================
                    JEU SNAKE - APPRENTISSAGE
====================================================================

Ce jeu vous enseigne les bases de la programmation avec Pygame.
Lisez les commentaires pour comprendre chaque étape !

OBJECTIF : Manger des pommes pour grandir sans toucher les murs
           ou vous-même.
====================================================================
"""

# ÉTAPE 1 : IMPORTER LES BIBLIOTHÈQUES
# ===================================
# Pygame est une bibliothèque qui nous aide à créer des jeux vidéo.
# Elle fournit des outils pour :
# - Créer une fenêtre
# - Dessiner des formes
# - Gérer les événements (touches du clavier, etc.)

import pygame
import random
from enum import Enum
import json
import os

# ===================================================================
# ÉTAPE 2 : DÉFINIR LES CONSTANTES (les valeurs qui ne changent pas)
# ===================================================================

# Initialiser Pygame (obligatoire au démarrage)
pygame.init()

# Fichier pour sauvegarder les scores
FICHIER_SCORES = "scores.json"
FICHIER_JOUEURS = "joueurs.json"  # Nouveau fichier pour les métadonnées des joueurs

# Fonctions pour gérer la sauvegarde des scores et des préférences des joueurs
def charger_scores():
    """
    Charge les scores depuis le fichier JSON
    Si le fichier n'existe pas, retourne un dictionnaire vide
    """
    if os.path.exists(FICHIER_SCORES):
        with open(FICHIER_SCORES, 'r') as f:
            return json.load(f)
    return {}

def charger_joueurs():
    """
    Charge les informations des joueurs (couleur préférée, etc.) depuis le fichier JSON
    """
    if os.path.exists(FICHIER_JOUEURS):
        with open(FICHIER_JOUEURS, 'r') as f:
            return json.load(f)
    return {}

def sauvegarder_joueurs(joueurs):
    """
    Sauvegarde les informations des joueurs
    """
    with open(FICHIER_JOUEURS, 'w') as f:
        json.dump(joueurs, f, indent=2)

def sauvegarder_scores(scores):
    """
    Sauvegarde les scores dans le fichier JSON
    """
    with open(FICHIER_SCORES, 'w') as f:
        json.dump(scores, f, indent=2)

def ajouter_score(scores, nom, score):
    """
    Ajoute un score pour un joueur
    """
    if nom not in scores:
        scores[nom] = []
    scores[nom].append(score)
    sauvegarder_scores(scores)

def obtenir_meilleur_score(scores, nom):
    """
    Retourne le meilleur score d'un joueur
    """
    if nom in scores and scores[nom]:
        return max(scores[nom])
    return 0

def obtenir_couleur_joueur(joueurs, nom, couleurs_disponibles):
    """
    Retourne la couleur préférée d'un joueur
    Retourne l'index de la couleur dans la liste des couleurs disponibles
    Par défaut, retourne 0 (première couleur - VERT)
    """
    if nom in joueurs and "couleur" in joueurs[nom]:
        couleur_rgb = joueurs[nom]["couleur"]
        # Trouver l'index de cette couleur dans les couleurs disponibles
        for i, (nom_couleur, rgb) in enumerate(couleurs_disponibles):
            if rgb == couleur_rgb:
                return i
    return 0  # Couleur par défaut (VERT)

def sauvegarder_couleur_joueur(joueurs, nom, couleur_rgb):
    """
    Sauvegarde la couleur préférée d'un joueur
    """
    if nom not in joueurs:
        joueurs[nom] = {}
    joueurs[nom]["couleur"] = couleur_rgb
    sauvegarder_joueurs(joueurs)

def afficher_classement(scores):
    """
    Affiche le classement de tous les joueurs
    """
    if not scores:
        print("\n📊 Aucun score enregistré pour le moment.\n")
        return
    
    # Créer une liste avec le meilleur score de chaque joueur
    classement = []
    for nom, liste_scores in scores.items():
        if liste_scores:
            meilleur = max(liste_scores)
            classement.append((nom, meilleur, len(liste_scores)))
    
    # Trier par score décroissant
    classement.sort(key=lambda x: x[1], reverse=True)
    
    print("\n" + "="*50)
    print("📊 CLASSEMENT DES MEILLEURS SCORES")
    print("="*50)
    for i, (nom, score, nb_parties) in enumerate(classement[:10], 1):
        print(f"{i}. {nom:20} - Score: {score:4} (Parties: {nb_parties})")
    print("="*50 + "\n")

# Dimensions de la fenêtre du jeu
LARGEUR = 1000
HAUTEUR = 700

# Taille des carrés (pixels)
# Tout dans ce jeu est basé sur des carrés de 20x20 pixels
TAILLE_CASE = 20

# Couleurs (format RGB : Rouge, Vert, Bleu - valeurs 0 à 255)
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)      # Pour la pomme
VERT = (0, 255, 0)       # Pour le serpent
BLEU = (100, 150, 255)   # Pour le texte

# Vitesse du jeu (nombre d'images par seconde)
# Plus la valeur est élevée, plus vite le jeu s'exécute
FPS = 10

# Directions possibles du serpent
class Direction(Enum):
    """
    Enum : un type spécial pour représenter un ensemble de valeurs fixées
    Ici on utilise UP, DOWN, LEFT, RIGHT pour les 4 directions
    """
    HAUT = (0, -1)      # Y diminue = vers le haut
    BAS = (0, 1)        # Y augmente = vers le bas
    GAUCHE = (-1, 0)    # X diminue = vers la gauche
    DROITE = (1, 0)     # X augmente = vers la droite

# ===================================================================
# ÉTAPE 3 : CRÉER LA FENÊTRE DU JEU
# ===================================================================

# Créer la surface de jeu (la fenêtre où se dessine tout)
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("🐍 Jeu Snake - Apprendre à Programmer!")

# Créer une horloge pour contrôler la vitesse du jeu
horloge = pygame.time.Clock()

# Police pour écrire du texte
police = pygame.font.Font(None, 36)

# ===================================================================
# ÉTAPE 4 : INITIALISER LES VARIABLES DU JEU
# ===================================================================

# Calculer la position de départ alignée avec la grille
# (important : toutes les positions doivent être des multiples de TAILLE_CASE)
start_x = (LARGEUR // 2) // TAILLE_CASE * TAILLE_CASE
start_y = (HAUTEUR // 2) // TAILLE_CASE * TAILLE_CASE

# Position du serpent (liste de coordonnées x, y)
# On commence avec un serpent de 3 carrés
serpent = [
    (start_x, start_y),                          # La tête
    (start_x - TAILLE_CASE, start_y),            # Le corps
    (start_x - 2 * TAILLE_CASE, start_y)        # La queue
]

# Direction initiale du serpent
direction = Direction.DROITE

# Direction demandée par l'utilisateur (mise à jour avec les touches)
direction_demandee = Direction.DROITE

# Position de la pomme (aléatoire)
def generer_pomme():
    """
    FONCTION : bloc de code réutilisable qui effectue une action
    
    Cette fonction crée une nouvelle pomme à une position aléatoire
    on la met toujours sur une case (multiple de TAILLE_CASE)
    """
    while True:
        x = random.randint(0, (LARGEUR - TAILLE_CASE) // TAILLE_CASE) * TAILLE_CASE
        y = random.randint(0, (HAUTEUR - TAILLE_CASE) // TAILLE_CASE) * TAILLE_CASE
        pomme_pos = (x, y)
        # S'assurer que la pomme n'apparaît pas sur le serpent
        # Note: On ne peut pas toujours éviter le serpent, donc on prend juste une position aléatoire
        return pomme_pos

def calculer_nombre_pommes(score):
    """
    Calcule le nombre de pommes à afficher en fonction du score
    À 200 points: 2 pommes
    À 300 points: 3 pommes
    etc.
    """
    # Le nombre de pommes est 1 + (score // 100)
    # Donc: 0-99 pts = 1 pomme, 100-199 pts = 1 pomme, 200-299 pts = 2 pommes, etc.
    return 1 + (score // 200)

def initialiser_pommes(nombre_pommes, serpent_actuel):
    """
    Crée une liste de pommes à partir du nombre demandé
    """
    pommes = []
    for _ in range(nombre_pommes):
        pomme = generer_pomme()
        pommes.append(pomme)
    return pommes

pomme = generer_pomme()

# FONCTION : Demander le nom du joueur et la couleur du serpent dans une fenêtre
def demander_nom_joueur(ecran, scores_existants=None, joueurs_existants=None):
    """
    Affiche une fenêtre graphique pour demander le nom du joueur et choisir la couleur du serpent
    Retourne un tuple (nom, couleur)
    """
    if scores_existants is None:
        scores_existants = {}
    if joueurs_existants is None:
        joueurs_existants = {}
    
    # Couleurs disponibles pour le serpent
    couleurs_disponibles = [
        ("VERT", (0, 255, 0)),
        ("BLEU", (0, 100, 255)),
        ("ROUGE", (255, 50, 50)),
        ("JAUNE", (255, 255, 0)),
        ("MAGENTA", (255, 0, 255)),
        ("CYAN", (0, 255, 255))
    ]
    
    # Obtenir la liste des noms existants
    noms_existants = list(scores_existants.keys())
    
    nom = ""
    couleur_selectionnee = 0  # Index de la couleur actuellement sélectionnée
    en_saisie = True
    suggestion_active = None  # Suggestion actuelle
    derniere_couleur_suggeree = None  # Pour pré-sélectionner la couleur après autocomplete
    
    while en_saisie:
        ecran.fill(NOIR)
        
        # Titre
        titre = pygame.font.Font(None, 60).render("BIENVENUE!", True, BLEU)
        ecran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, 50))
        
        # Question nom
        question = pygame.font.Font(None, 40).render("Quel est ton nom ?", True, BLANC)
        ecran.blit(question, (LARGEUR // 2 - question.get_width() // 2, 130))
        
        # Trouver une suggestion si le joueur tape quelque chose
        suggestion_active = None
        if nom:
            for n in noms_existants:
                if n.lower().startswith(nom.lower()):
                    suggestion_active = n
                    break
        
        # Champ de saisie avec le texte et la suggestion
        police_saisie = pygame.font.Font(None, 50)
        if suggestion_active:
            # Afficher le texte saisi en vert et la suggestion complète en gris
            champ_texte = police_saisie.render(nom, True, (100, 255, 100))
            suggestion_texte = police_saisie.render(suggestion_active[len(nom):], True, (100, 100, 100))
            ecran.blit(champ_texte, (LARGEUR // 2 - 200, 190))
            ecran.blit(suggestion_texte, (LARGEUR // 2 - 200 + champ_texte.get_width(), 190))
        else:
            champ_texte = police_saisie.render(nom + "_", True, (100, 255, 100))
            ecran.blit(champ_texte, (LARGEUR // 2 - champ_texte.get_width() // 2, 190))
        
        # Message si une suggestion est disponible
        if suggestion_active:
            texte_tab = pygame.font.Font(None, 25).render(f"Appuyez sur TAB pour accepter la suggestion: {suggestion_active}", True, (150, 150, 150))
            ecran.blit(texte_tab, (LARGEUR // 2 - texte_tab.get_width() // 2, 260))
        
        # Question couleur
        texte_couleur = pygame.font.Font(None, 35).render("Choisir la couleur du serpent :", True, BLANC)
        ecran.blit(texte_couleur, (LARGEUR // 2 - texte_couleur.get_width() // 2, 310))
        
        # Afficher les couleurs disponibles comme des carrés cliquables
        taille_carre = 40
        espacement = 15
        largeur_total = (taille_carre + espacement) * len(couleurs_disponibles) - espacement
        x_debut = LARGEUR // 2 - largeur_total // 2
        
        for i, (nom_couleur, rgb) in enumerate(couleurs_disponibles):
            x = x_debut + i * (taille_carre + espacement)
            y = 370
            
            # Dessiner le carré de couleur
            pygame.draw.rect(ecran, rgb, (x, y, taille_carre, taille_carre))
            
            # Si sélectionné, ajouter une bordure blanche plus épaisse
            if i == couleur_selectionnee:
                pygame.draw.rect(ecran, BLANC, (x, y, taille_carre, taille_carre), 4)
            else:
                pygame.draw.rect(ecran, BLANC, (x, y, taille_carre, taille_carre), 2)
            
            # Afficher le nom de la couleur
            texte_nom_couleur = pygame.font.Font(None, 20).render(nom_couleur, True, BLANC)
            ecran.blit(texte_nom_couleur, (x + taille_carre // 2 - texte_nom_couleur.get_width() // 2, y + taille_carre + 5))
        
        # Instructions
        instructions = pygame.font.Font(None, 25).render("← → pour changer la couleur | ENTRÉE pour confirmer", True, BLANC)
        ecran.blit(instructions, (LARGEUR // 2 - instructions.get_width() // 2, 530))
        
        pygame.display.flip()
        
        # Gérer les événements clavier
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                return None, None
            if evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_RETURN:
                    # Validation du nom
                    if nom.strip():
                        en_saisie = False
                elif evt.key == pygame.K_TAB:
                    # Accepter la suggestion avec TAB
                    if suggestion_active:
                        nom = suggestion_active
                        # Charger la couleur précédente du joueur
                        couleur_selectionnee = obtenir_couleur_joueur(joueurs_existants, nom, couleurs_disponibles)
                elif evt.key == pygame.K_BACKSPACE:
                    # Supprimer un caractère du nom
                    nom = nom[:-1]
                elif evt.key == pygame.K_LEFT:
                    # Couleur précédente
                    couleur_selectionnee = (couleur_selectionnee - 1) % len(couleurs_disponibles)
                elif evt.key == pygame.K_RIGHT:
                    # Couleur suivante
                    couleur_selectionnee = (couleur_selectionnee + 1) % len(couleurs_disponibles)
                else:
                    # Ajouter un caractère (seulement les caractères alphanumériques)
                    if len(nom) < 20:  # Limite de 20 caractères
                        if evt.unicode.isalnum() or evt.unicode.isspace():
                            nom += evt.unicode
        
        horloge.tick(30)
    
    # Charger la couleur précédente du joueur si c'est un joueur existant
    nom_final = nom.strip() if nom.strip() else "Joueur"
    couleur_selectionnee = obtenir_couleur_joueur(joueurs_existants, nom_final, couleurs_disponibles)
    
    couleur_choisie = couleurs_disponibles[couleur_selectionnee][1]
    return (nom_final, couleur_choisie)

# FONCTION : Afficher un écran de transition avec compte à rebours
def afficher_transition_compte_a_rebours(ecran, titre, duree_secondes=3):
    """
    Affiche un écran de transition avec un compte à rebours
    """
    debut = pygame.time.get_ticks()
    duree_ms = duree_secondes * 1000
    
    while (pygame.time.get_ticks() - debut) < duree_ms:
        ecran.fill(NOIR)
        
        # Afficher le titre
        texte_titre = pygame.font.Font(None, 60).render(titre, True, (100, 255, 100))
        ecran.blit(texte_titre, (LARGEUR // 2 - texte_titre.get_width() // 2, 200))
        
        # Afficher "Préparez-vous..."
        texte_prep = pygame.font.Font(None, 35).render("Préparez-vous...", True, BLANC)
        ecran.blit(texte_prep, (LARGEUR // 2 - texte_prep.get_width() // 2, 330))
        
        # Calculer et afficher le compte à rebours
        temps_restant_ms = duree_ms - (pygame.time.get_ticks() - debut)
        secondes_restantes = max(1, int(temps_restant_ms / 1000) + 1)
        
        texte_compte = pygame.font.Font(None, 120).render(str(secondes_restantes), True, (255, 215, 0))
        ecran.blit(texte_compte, (LARGEUR // 2 - texte_compte.get_width() // 2, 420))
        
        pygame.display.flip()
        
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                return False
        
        horloge.tick(60)
    
    return True

# FONCTION : Afficher un écran de pause
# FONCTION : Afficher un effet de feu d'artifice
def afficher_feu_artifice(ecran, duree_secondes=2):
    """
    Affiche un effet de feu d'artifice (petits carrés colorés tombants)
    """
    import random
    
    # Créer des "étincelles" (petits carrés colorés)
    etincelles = []
    for _ in range(50):
        x = random.randint(0, LARGEUR)
        y = random.randint(0, HAUTEUR // 2)
        couleur = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)])
        vitesse_y = random.randint(2, 8)
        etincelles.append({'x': x, 'y': y, 'couleur': couleur, 'vy': vitesse_y})
    
    debut = pygame.time.get_ticks()
    duree_ms = duree_secondes * 1000
    
    while (pygame.time.get_ticks() - debut) < duree_ms:
        ecran.fill(NOIR)
        
        # Mettre à jour et dessiner les étincelles
        for etincelle in etincelles:
            etincelle['y'] += etincelle['vy']
            if etincelle['y'] < HAUTEUR:
                pygame.draw.rect(ecran, etincelle['couleur'], 
                               (etincelle['x'], etincelle['y'], 8, 8))
        
        # Afficher le message
        texte = pygame.font.Font(None, 80).render("🎉 RECORD! 🎉", True, (255, 215, 0))
        ecran.blit(texte, (LARGEUR // 2 - texte.get_width() // 2, 150))
        
        pygame.display.flip()
        horloge.tick(60)
    
    return True

# FONCTION : Afficher l'écran de pause
def afficher_ecran_pause(ecran, nom_joueur, score_actuel):
    """
    Affiche un écran de pause avec le message "PAUSE" en gros
    L'utilisateur peut appuyer sur ESPACE pour reprendre ou ESC pour quitter
    """
    while True:
        ecran.fill(NOIR)
        
        # Afficher "PAUSE" en gros
        titre_pause = pygame.font.Font(None, 100).render("PAUSE", True, ROUGE)
        ecran.blit(titre_pause, (LARGEUR // 2 - titre_pause.get_width() // 2, 150))
        
        # Afficher les infos du joueur et du score
        texte_joueur = pygame.font.Font(None, 40).render(f"Joueur: {nom_joueur}", True, BLANC)
        texte_score = pygame.font.Font(None, 40).render(f"Score: {score_actuel}", True, BLEU)
        
        ecran.blit(texte_joueur, (LARGEUR // 2 - texte_joueur.get_width() // 2, 300))
        ecran.blit(texte_score, (LARGEUR // 2 - texte_score.get_width() // 2, 360))
        
        # Instructions pour reprendre
        instructions = pygame.font.Font(None, 30).render("Appuyez sur ESPACE pour reprendre | ESC pour quitter", True, (100, 255, 100))
        ecran.blit(instructions, (LARGEUR // 2 - instructions.get_width() // 2, 550))
        
        pygame.display.flip()
        
        # Attendre l'entrée de l'utilisateur
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                return "quitter"
            if evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_SPACE:
                    return "reprendre"
                elif evt.key == pygame.K_ESCAPE:
                    return "quitter"
        
        horloge.tick(30)

# FONCTION : Afficher le menu de démarrage
def afficher_menu(ecran, scores):
    """
    Affiche un menu avec le classement et un bouton "Démarrer le jeu"
    """
    en_menu = True
    
    # Dimensions du bouton
    bouton_largeur = 200
    bouton_hauteur = 60
    bouton_x = LARGEUR // 2 - bouton_largeur // 2
    bouton_y = HAUTEUR - 120
    
    while en_menu:
        ecran.fill(NOIR)
        
        # Titre
        titre = pygame.font.Font(None, 70).render("🐍 SNAKE 🐍", True, VERT)
        ecran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, 30))
        
        # Afficher le classement
        petite_police = pygame.font.Font(None, 25)
        texte_classement = petite_police.render("MEILLEURS SCORES", True, BLEU)
        ecran.blit(texte_classement, (LARGEUR // 2 - texte_classement.get_width() // 2, 120))
        
        # Créer et afficher le classement
        if scores:
            classement = []
            for nom, liste_scores in scores.items():
                if liste_scores:
                    meilleur = max(liste_scores)
                    classement.append((nom, meilleur))
            
            classement.sort(key=lambda x: x[1], reverse=True)
            
            y_pos = 160
            for i, (nom, score) in enumerate(classement[:5], 1):
                texte = petite_police.render(f"{i}. {nom:20} - {score}", True, BLANC)
                ecran.blit(texte, (LARGEUR // 2 - texte.get_width() // 2, y_pos))
                y_pos += 35
        else:
            texte_vide = petite_police.render("Aucun score pour le moment", True, (100, 100, 100))
            ecran.blit(texte_vide, (LARGEUR // 2 - texte_vide.get_width() // 2, 160))
        
        # Dessiner le bouton "Démarrer le jeu"
        souris = pygame.mouse.get_pos()
        souris_sur_bouton = (bouton_x < souris[0] < bouton_x + bouton_largeur and 
                             bouton_y < souris[1] < bouton_y + bouton_hauteur)
        
        couleur_bouton = (100, 255, 100) if souris_sur_bouton else VERT
        pygame.draw.rect(ecran, couleur_bouton, (bouton_x, bouton_y, bouton_largeur, bouton_hauteur))
        pygame.draw.rect(ecran, BLANC, (bouton_x, bouton_y, bouton_largeur, bouton_hauteur), 3)
        
        texte_bouton = pygame.font.Font(None, 35).render("DÉMARRER", True, NOIR)
        ecran.blit(texte_bouton, (bouton_x + bouton_largeur // 2 - texte_bouton.get_width() // 2,
                                  bouton_y + bouton_hauteur // 2 - texte_bouton.get_height() // 2))
        
        pygame.display.flip()
        
        # Gérer les événements
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                return False
            if evt.type == pygame.MOUSEBUTTONDOWN:
                if souris_sur_bouton:
                    en_menu = False
        
        horloge.tick(30)
    
    return True

# FONCTION : Afficher l'écran de fin
def afficher_ecran_fin(ecran, nom, score_final, meilleur):
    """
    Affiche un écran de fin de jeu avec le score et un message
    Retourne le choix du joueur : "rejouer", "autre_joueur", ou "quitter"
    """
    # Si c'est un nouveau record, afficher le feu d'artifice
    if score_final > meilleur:
        afficher_feu_artifice(ecran, 2)
    
    choix = None
    
    while choix is None:
        ecran.fill(NOIR)
        
        # Titre
        titre = pygame.font.Font(None, 60).render("GAME OVER!", True, ROUGE)
        ecran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, 50))
        
        # Nom du joueur
        texte_nom = police.render(f"Joueur: {nom}", True, BLANC)
        ecran.blit(texte_nom, (LARGEUR // 2 - texte_nom.get_width() // 2, 150))
        
        # Score final
        texte_score = police.render(f"Score: {score_final}", True, BLEU)
        ecran.blit(texte_score, (LARGEUR // 2 - texte_score.get_width() // 2, 220))
        
        # Message de félicitation si nouveau record
        if score_final > meilleur:
            texte_record = pygame.font.Font(None, 50).render("🎉 NOUVEAU RECORD! 🎉", True, (255, 215, 0))
            ecran.blit(texte_record, (LARGEUR // 2 - texte_record.get_width() // 2, 300))
        else:
            texte_meilleur = police.render(f"Meilleur score: {meilleur}", True, (100, 255, 100))
            ecran.blit(texte_meilleur, (LARGEUR // 2 - texte_meilleur.get_width() // 2, 300))
        
        # Options
        petite_police = pygame.font.Font(None, 30)
        texte_option1 = petite_police.render("[R] Rejouer avec le même nom", True, BLANC)
        texte_option2 = petite_police.render("[A] Autre joueur", True, BLANC)
        texte_option3 = petite_police.render("[Q] Quitter", True, BLANC)
        
        ecran.blit(texte_option1, (LARGEUR // 2 - texte_option1.get_width() // 2, 380))
        ecran.blit(texte_option2, (LARGEUR // 2 - texte_option2.get_width() // 2, 420))
        ecran.blit(texte_option3, (LARGEUR // 2 - texte_option3.get_width() // 2, 460))
        
        pygame.display.flip()
        
        # Attendre un choix
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                return "quitter"
            if evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_r:
                    choix = "rejouer"
                elif evt.key == pygame.K_a:
                    choix = "autre_joueur"
                elif evt.key == pygame.K_q:
                    choix = "quitter"
        
        horloge.tick(30)
    
    # Retourner le choix du joueur
    return choix

# Score
score = 0

# Charger tous les scores enregistrés
tous_les_scores = charger_scores()

# Charger les informations des joueurs (couleurs préférées, etc.)
tous_les_joueurs = charger_joueurs()

# ===================================================================
# BOUCLE DE JEU PRINCIPALE (gère plusieurs parties)
# ===================================================================

continuer_jeu = True
nom_joueur = ""
meilleur_score = 0
couleur_serpent = VERT  # Couleur par défaut
demander_nouveau_nom = True

# Afficher le menu de démarrage avec le classement
if not afficher_menu(ecran, tous_les_scores):
    continuer_jeu = False

# Vider la file d'événements
pygame.event.clear()

while continuer_jeu:
    # Demander le nom du joueur que s'il faut (pas au redémarrage)
    if demander_nouveau_nom:
        # Vider la file d'événements avant de demander le nom
        pygame.event.clear()
        resultat = demander_nom_joueur(ecran, tous_les_scores, tous_les_joueurs)
        
        if resultat is None or resultat[0] is None:
            # L'utilisateur a fermé la fenêtre
            continuer_jeu = False
            break
        
        nom_joueur, couleur_serpent = resultat
        
        # Sauvegarder la couleur choisie du joueur
        sauvegarder_couleur_joueur(tous_les_joueurs, nom_joueur, couleur_serpent)
        
        # Récupérer le meilleur score du joueur
        meilleur_score = obtenir_meilleur_score(tous_les_scores, nom_joueur)
        
        # Afficher un message de bienvenue dans le terminal
        print(f"\n🎮 Bon jeu {nom_joueur} ! 🐍")
        print(f"Ton meilleur score précédent : {meilleur_score}\n")
        
        # Afficher un écran de transition avec compte à rebours
        afficher_transition_compte_a_rebours(ecran, f"Bienvenue {nom_joueur}!", 3)
        
        # Prochain tour, on ne demandera pas le nom à moins que l'utilisateur choisisse "autre_joueur"
        demander_nouveau_nom = False
    
    if not continuer_jeu:
        break
    
    # ===================================================================
    # ÉTAPE 5 : BOUCLE PRINCIPALE DU JEU (une seule partie)
    # ===================================================================
    """
    CONCEPT : BOUCLE
    Une boucle répète le même code indéfiniment (while True).
    Ici, on répète FPS fois par seconde :
      1. Vérifier les événements (touches du clavier)
      2. Mettre à jour la position
      3. Vérifier les collisions
      4. Dessiner l'écran
    """
    
    # Réinitialiser les variables pour la nouvelle partie
    score = 0
    jeu_actif = True
    jeu_pause = False
    
    # Réinitialiser la position du serpent
    start_x = (LARGEUR // 2) // TAILLE_CASE * TAILLE_CASE
    start_y = (HAUTEUR // 2) // TAILLE_CASE * TAILLE_CASE
    
    serpent = [
        (start_x, start_y),                          # La tête
        (start_x - TAILLE_CASE, start_y),            # Le corps
        (start_x - 2 * TAILLE_CASE, start_y)        # La queue
    ]
    
    # Réinitialiser la direction
    direction = Direction.DROITE
    direction_demandee = Direction.DROITE
    
    # Générer les pommes initiales (1 au début)
    pommes = initialiser_pommes(1, serpent)
    
    while jeu_actif:
        
        # --- GESTION DE LA PAUSE ---
        while jeu_pause:
            resultat_pause = afficher_ecran_pause(ecran, nom_joueur, score)
            if resultat_pause == "reprendre":
                jeu_pause = False
            elif resultat_pause == "quitter":
                jeu_actif = False
                break
        
        if not jeu_actif:
            break
        
        # --- ÉVÉNEMENTS (Que fait l'utilisateur ?) ---
        for evenement in pygame.event.get():
            """
            Les événements sont les actions de l'utilisateur :
            - Appuyer sur une touche
            - Fermer la fenêtre
            - Cliquer avec la souris (non utilisé ici)
            """
            
            if evenement.type == pygame.QUIT:
                # L'utilisateur a cliqué sur la croix pour fermer
                print("⚠️ pygame.QUIT EVENT - Setting jeu_actif = False")
                jeu_actif = False
            
            # Événement KEYDOWN = une touche est appuyée
            if evenement.type == pygame.KEYDOWN:
                
                # FLÈCHE HAUT
                if evenement.key == pygame.K_UP:
                    # On ne peut pas aller vers le haut si on va vers le bas
                    if direction != Direction.BAS:
                        direction_demandee = Direction.HAUT
                
                # FLÈCHE BAS
                elif evenement.key == pygame.K_DOWN:
                    if direction != Direction.HAUT:
                        direction_demandee = Direction.BAS
                
                # FLÈCHE GAUCHE
                elif evenement.key == pygame.K_LEFT:
                    if direction != Direction.DROITE:
                        direction_demandee = Direction.GAUCHE
                
                # FLÈCHE DROITE
                elif evenement.key == pygame.K_RIGHT:
                    if direction != Direction.GAUCHE:
                        direction_demandee = Direction.DROITE
                
                # ESPACE pour mettre en pause
                elif evenement.key == pygame.K_SPACE:
                    jeu_pause = not jeu_pause
                
                # ESC pour quitter
                elif evenement.key == pygame.K_ESCAPE:
                    jeu_actif = False
        
        # --- MISE À JOUR (Que se passe-t-il dans le jeu ?) ---
        
        # Mettre à jour la direction
        direction = direction_demandee
        
        # Calculer la nouvelle position de la tête
        # La tête est à l'index 0 de la liste
        tete_x, tete_y = serpent[0]
        dx, dy = direction.value  # .value donne (x, y) de la direction
        
        nouvelle_tete = (tete_x + dx * TAILLE_CASE, tete_y + dy * TAILLE_CASE)
        
        # Vérifier les COLLISIONS avec les murs
        if (nouvelle_tete[0] < 0 or nouvelle_tete[0] >= LARGEUR or
            nouvelle_tete[1] < 0 or nouvelle_tete[1] >= HAUTEUR):
            print(f"\n💥 Collision avec un mur! Score: {score}")
            # Mettre à jour le meilleur score
            if score > meilleur_score:
                meilleur_score = score
            jeu_actif = False
            break
        
        # Vérifier la collision avec soi-même
        if nouvelle_tete in serpent:
            print(f"\n💥 Vous avez touché vous-même! Score: {score}")
            # Mettre à jour le meilleur score
            if score > meilleur_score:
                meilleur_score = score
            jeu_actif = False
            break
        
        # Ajouter la nouvelle tête au début du serpent
        serpent.insert(0, nouvelle_tete)
        
        # Vérifier si le serpent a mangé une pomme
        pomme_mangee = False
        for i, pomme in enumerate(pommes):
            if nouvelle_tete == pomme:
                # On a mangé une pomme !
                score += 10
                pomme_mangee = True
                pommes.pop(i)  # Enlever la pomme mangée
                # Ajouter une nouvelle pomme
                pommes.append(generer_pomme())
                print(f"Miam! Pomme mangée. Score: {score}")
                
                # Vérifier si on doit ajouter une pomme supplémentaire
                nombre_pommes_attendues = calculer_nombre_pommes(score)
                if len(pommes) < nombre_pommes_attendues:
                    pommes.append(generer_pomme())
                break
        
        # Si on n'a pas mangé, on retire la queue (sinon le serpent grandit)
        if not pomme_mangee:
            serpent.pop()
        
        # --- DESSINER (Afficher l'écran) ---
        
        # Remplir le fond avec du noir
        ecran.fill(NOIR)
        
        # Dessiner le serpent
        for i, (x, y) in enumerate(serpent):
            # La tête est plus brillante (on augmente la luminosité)
            if i == 0:
                # La tête a une couleur plus claire
                couleur = tuple(min(c + 100, 255) for c in couleur_serpent)
            else:
                # Le corps utilise la couleur choisie
                couleur = couleur_serpent
            # Dessiner un carré (rect = rectangle)
            pygame.draw.rect(ecran, couleur, (x, y, TAILLE_CASE, TAILLE_CASE))
            # Ajouter une bordure noire
            pygame.draw.rect(ecran, NOIR, (x, y, TAILLE_CASE, TAILLE_CASE), 1)
        
        # Dessiner toutes les pommes (en rouge)
        for pomme in pommes:
            pygame.draw.rect(ecran, ROUGE, (pomme[0], pomme[1], TAILLE_CASE, TAILLE_CASE))
        
        # Dessiner le nom du joueur et le score en haut à gauche
        texte_nom = police.render(f"Joueur: {nom_joueur}", True, (100, 255, 100))
        ecran.blit(texte_nom, (10, 10))
        
        texte_score = police.render(f"Score: {score}", True, BLEU)
        ecran.blit(texte_score, (10, 50))
        
        # Mettre à jour l'affichage
        pygame.display.flip()
        
        # Contrôler la vitesse (FPS fois par seconde)
        horloge.tick(FPS)
    
    # ===================================================================
    # FIN DE LA PARTIE : AFFICHER LE RÉSULTAT ET DEMANDER LA SUITE
    # ===================================================================
    
    # Sauvegarder le score du joueur
    ajouter_score(tous_les_scores, nom_joueur, score)
    
    # Afficher l'écran de fin avec le score et demander le choix
    choix = afficher_ecran_fin(ecran, nom_joueur, score, meilleur_score)
    
    # IMPORTANT : Vider la file d'événements Pygame pour éviter les conflits
    # Cela empêche les touches pressées précédemment de rester en mémoire
    pygame.event.clear()
    
    # Traiter le choix du joueur
    if choix == "quitter":
        continuer_jeu = False
    elif choix == "autre_joueur":
        # Afficher le classement avant la nouvelle partie
        afficher_classement(tous_les_scores)
        
        # Demander un nouveau nom au prochain tour
        demander_nouveau_nom = True
        # Vider complètement la file d'événements
        pygame.event.clear()
        continue
    elif choix == "rejouer":
        # Afficher la transition avec compte à rebours pour "Rejouer"
        afficher_transition_compte_a_rebours(ecran, f"Bon jeu {nom_joueur}!", 3)
    # Si choix == "rejouer", la boucle continue automatiquement avec le même joueur (demander_nouveau_nom reste False)
    
# ===================================================================
# FERMER LE JEU
# ===================================================================

# Afficher le classement final
afficher_classement(tous_les_scores)

pygame.quit()
print("Merci d'avoir joué! À bientôt!")


