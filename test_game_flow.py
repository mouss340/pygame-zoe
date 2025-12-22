#!/usr/bin/env python3
"""
Test script pour simuler le flux complet du jeu
"""
import subprocess
import time
import sys

# Start the game in a subprocess
print("🎮 Lancement du jeu Snake...")
proc = subprocess.Popen(
    ['python3', 'snake_game.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

try:
    # Simulate:
    # 1. Wait for menu and click "DÉMARRER"
    print("⏳ En attente du menu...")
    time.sleep(2)
    proc.stdin.write('\n')  # Simulate ENTER
    proc.stdin.flush()
    
    # 2. Wait for name request and type a name
    print("⏳ En attente de la demande de nom...")
    time.sleep(1)
    proc.stdin.write('TestJoueur\n')  # Type name
    proc.stdin.flush()
    
    # 3. Wait for color selection
    print("⏳ En attente de la sélection de couleur...")
    time.sleep(1)
    proc.stdin.write('\n')  # Press ENTER to confirm color
    proc.stdin.flush()
    
    # 4. Play for a bit (the game auto-crashes after 2 seconds due to collision)
    print("⏳ Partie en cours...")
    time.sleep(3)
    
    # 5. Try to press 'A' for "Autre joueur"
    print("⏳ Appui sur [A] pour 'Autre joueur'...")
    proc.stdin.write('a\n')  # Lowercase to simulate user input
    proc.stdin.flush()
    
    # 6. Wait for name request again
    print("⏳ En attente de nouveau joueur...")
    time.sleep(2)
    proc.stdin.write('Joueur2\n')
    proc.stdin.flush()
    
    # 7. Wait and finish
    print("⏳ Fin du test...")
    time.sleep(1)
    
except Exception as e:
    print(f"❌ Erreur: {e}")
finally:
    proc.terminate()
    output, _ = proc.communicate()
    
    print("\n" + "="*60)
    print("📋 OUTPUT DU JEU:")
    print("="*60)
    # Print last 50 lines
    lines = output.split('\n')
    for line in lines[-50:]:
        if line.strip():
            print(line)
