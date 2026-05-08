import os
import sys
from unittest.mock import MagicMock

# Ajouter le chemin racine au sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.graph import EmbassyGraph

def test_graph_logic():
    # Mock des services pour tester la structure du graphe sans appels API
    mock_retriever = MagicMock()
    mock_retriever.retrieve_context.return_value = ("Contenu de test", ["source1.pdf"])
    
    mock_chat = MagicMock()
    mock_chat.rewrite_query.return_value = "Requête reformulée"
    mock_chat.generate_response.return_value = "Ceci est une réponse de test."
    
    mock_cache = MagicMock()
    mock_cache.check_cache.return_value = None
    
    mock_store = MagicMock()
    mock_store.get_embedding.return_value = None

    # Initialisation du graphe
    embassy_graph = EmbassyGraph(mock_retriever, mock_chat, mock_cache, mock_store)
    
    # Test d'une requête RAG
    print("--- Test Requête RAG ---")
    result = embassy_graph.run("Comment faire un passeport ?", [])
    print(f"Réponse : {result['response']}")
    assert result['response'] == "Ceci est une réponse de test."
    assert "source1.pdf" in result['sources']
    print("Succès RAG !")

    # Test d'une requête conversationnelle
    print("\n--- Test Requête Conversationnelle ---")
    result = embassy_graph.run("Bonjour", [])
    print(f"Réponse : {result['response']}")
    assert "bonjour" in result['response'].lower() or "salut" in result['response'].lower() or "aider" in result['response'].lower()
    print("Succès Conversationnel !")

if __name__ == "__main__":
    try:
        test_graph_logic()
        print("\nTous les tests du graphe sont passés avec succès !")
    except Exception as e:
        print(f"\nErreur lors des tests : {e}")
        import traceback
        traceback.print_exc()
