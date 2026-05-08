import os
from typing import Annotated, Dict, List, Optional, Union
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END, START
from app.rag.retriever import Retriever
from app.services.mistral_client import MistralChatClient
from app.rag.semantic_cache import SemanticCache
from app.security.input_validation import InputValidator
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class GraphState(TypedDict):
    """État du graphe pour le chatbot de l'Ambassade."""
    query: str
    chat_history: List[Dict[str, str]]
    rewritten_query: Optional[str]
    context: str
    sources: List[str]
    response: Optional[str]
    is_conversational: bool
    is_cached: bool

class EmbassyGraph:
    def __init__(self, retriever: Retriever, chat_client: MistralChatClient, semantic_cache: SemanticCache, store):
        self.retriever = retriever
        self.chat_client = chat_client
        self.semantic_cache = semantic_cache
        self.store = store
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()

    def _create_workflow(self):
        workflow = StateGraph(GraphState)

        # Ajout des nœuds
        workflow.add_node("router", self.router_node)
        workflow.add_node("cache_checker", self.cache_checker_node)
        workflow.add_node("conversational", self.conversational_node)
        workflow.add_node("rewriter", self.rewriter_node)
        workflow.add_node("retriever", self.retriever_node)
        workflow.add_node("generator", self.generator_node)

        # Définition des connexions
        workflow.add_edge(START, "router")
        
        # Logique conditionnelle pour le routeur
        workflow.add_conditional_edges(
            "router",
            self.decide_after_router,
            {
                "conversational": "conversational",
                "cache_checker": "cache_checker"
            }
        )

        # Logique conditionnelle pour le cache
        workflow.add_conditional_edges(
            "cache_checker",
            self.decide_after_cache,
            {
                "hit": END,
                "miss": "rewriter"
            }
        )

        workflow.add_edge("conversational", END)
        workflow.add_edge("rewriter", "retriever")
        workflow.add_edge("retriever", "generator")
        workflow.add_edge("generator", END)

        return workflow

    # --- NOEUDS ---

    def router_node(self, state: GraphState) -> Dict:
        """Détermine si la requête est purement conversationnelle."""
        query = state["query"]
        is_conv = InputValidator.is_conversational(query)
        return {"is_conversational": is_conv}

    def decide_after_router(self, state: GraphState) -> str:
        if state["is_conversational"]:
            return "conversational"
        return "cache_checker"

    def cache_checker_node(self, state: GraphState) -> Dict:
        """Vérifie le cache sémantique (uniquement pour le premier message)."""
        if state["chat_history"]:
            return {"is_cached": False}
        
        query_emb = self.store.get_embedding(state["query"])
        cached_response = self.semantic_cache.check_cache(query_emb)
        
        if cached_response:
            return {
                "response": "⚡ *(Réponse optimisée : Cache Sémantique)*\n\n" + cached_response,
                "is_cached": True
            }
        return {"is_cached": False}

    def decide_after_cache(self, state: GraphState) -> str:
        if state.get("is_cached"):
            return "hit"
        return "miss"

    def conversational_node(self, state: GraphState) -> Dict:
        """Gère les salutations et politesses localement."""
        response = InputValidator.get_conversational_response(state["query"])
        return {"response": response}

    def rewriter_node(self, state: GraphState) -> Dict:
        """Reformule la requête en fonction de l'historique."""
        rewritten = self.chat_client.rewrite_query(state["query"], state["chat_history"])
        return {"rewritten_query": rewritten}

    def retriever_node(self, state: GraphState) -> Dict:
        """Récupère le contexte depuis FAISS."""
        search_query = state.get("rewritten_query") or state["query"]
        context, sources = self.retriever.retrieve_context(search_query)
        return {"context": context, "sources": sources}

    def generator_node(self, state: GraphState) -> Dict:
        """Génère la réponse finale via Mistral."""
        # Note: On n'utilise pas le streaming ici car LangGraph retourne l'état final.
        # Pour le streaming dans Streamlit, on utilisera une approche différente si besoin,
        # mais ici on implémente la logique de base.
        sources_found = len(state["sources"]) > 0
        response = self.chat_client.generate_response(
            state["query"], 
            state["context"], 
            sources_found
        )
        
        # Mise à jour du cache si nécessaire
        if not state["chat_history"] and sources_found:
            query_emb = self.store.get_embedding(state["query"])
            self.semantic_cache.add_to_cache(query_emb, state["query"], response)
            
        return {"response": response}

    def run(self, query: str, chat_history: List[Dict[str, str]] = None) -> Dict:
        """Exécute le graphe de manière synchrone."""
        initial_state = {
            "query": query,
            "chat_history": chat_history or [],
            "rewritten_query": None,
            "context": "",
            "sources": [],
            "response": None,
            "is_conversational": False,
            "is_cached": False
        }
        return self.app.invoke(initial_state)
