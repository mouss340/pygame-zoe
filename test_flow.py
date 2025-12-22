#!/usr/bin/env python3
"""Test script to debug the 'autre_joueur' flow"""

# Simulate the game loop
continuer_jeu = True
demander_nouveau_nom = True
nom_joueur = ""

iteration = 0

while continuer_jeu:
    iteration += 1
    print(f"\n=== ITERATION {iteration} ===")
    print(f"demander_nouveau_nom = {demander_nouveau_nom}")
    
    # Check if we need to ask for a new player name
    if demander_nouveau_nom:
        print("✓ Entering name request block")
        # Simulate asking for name
        if iteration == 1:
            nom_joueur = "Alice"
        elif iteration == 2:
            nom_joueur = "Bob"
        print(f"✓ Got name: {nom_joueur}")
        demander_nouveau_nom = False
        print(f"✓ Set demander_nouveau_nom to False")
    
    if not continuer_jeu:
        print("Breaking out because continuer_jeu is False")
        break
    
    print(f"Playing game for {nom_joueur}...")
    
    # Simulate game play and then show end screen
    # Simulate the user choosing an option
    if iteration == 1:
        choix = "autre_joueur"
    elif iteration == 2:
        choix = "quitter"
    else:
        choix = "quitter"
    
    print(f"\nUser chose: {choix}")
    
    # Handle the choice
    if choix == "quitter":
        print("Setting continuer_jeu = False")
        continuer_jeu = False
    elif choix == "autre_joueur":
        print("User wants another player")
        print("Setting demander_nouveau_nom = True")
        demander_nouveau_nom = True
        print("Executing continue...")
        continue
    
    print("End of iteration")

print("\n=== GAME ENDED ===")
