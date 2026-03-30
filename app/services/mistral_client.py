# Imports différés de Mistral pour l'optimisation extrême des temps de chargement
MistralClientClass = None

def get_mistral_class():
    global MistralClientClass
    if MistralClientClass is not None:
        return MistralClientClass
    try:
        from mistralai import Mistral
        MistralClientClass = Mistral
    except ImportError:
        try:
            from mistralai.client import Mistral
            MistralClientClass = Mistral
        except ImportError:
            from mistralai.client import MistralClient
            MistralClientClass = MistralClient
    return MistralClientClass

def create_messages(sys_content, user_content):
    cls = get_mistral_class()
    if cls.__name__ == "MistralClient":
        from mistralai.models.chat_completion import ChatMessage
        return [
            ChatMessage(role="system", content=sys_content),
            ChatMessage(role="user", content=user_content)
        ]
    else:
        return [
            {"role": "system", "content": sys_content},
            {"role": "user", "content": user_content}
        ]

def create_messages_with_history(sys_content, history, user_content):
    cls = get_mistral_class()
    if cls.__name__ == "MistralClient":
        from mistralai.models.chat_completion import ChatMessage
        msgs = [ChatMessage(role="system", content=sys_content)]
        for msg in history:
            msgs.append(ChatMessage(role=msg["role"], content=msg["content"]))
        msgs.append(ChatMessage(role="user", content=user_content))
        return msgs
    else:
        msgs = [{"role": "system", "content": sys_content}]
        for msg in history:
            msgs.append({"role": msg["role"], "content": msg["content"]})
        msgs.append({"role": "user", "content": user_content})
        return msgs


from app.prompts.system_prompt import SYSTEM_PROMPT
from app.security.secrets_manager import SecretsManager
from app.security.output_validation import OutputValidator
from app.security.audit_logger import AuditLogger
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class MistralChatClient:
    """Client pour interagir avec l'API de chat Mistral."""
    
    def __init__(self):
        # Initialisation du client natif Mistral de façon paresseuse
        try:
            cls = get_mistral_class()
            self.api_key = SecretsManager.get_mistral_api_key()
            self.model = SecretsManager.get_chat_model()
            self.client = cls(api_key=self.api_key)
            self.is_mock = False
        except Exception as e:
            logger.warning(f"Impossible d'initialiser Mistral Client ({e}). Utilisation du mode mock.")
            self.api_key = "mock_key"
            self.model = "mock_model"
            self.is_mock = True

    def generate_response(self, query: str, context: str, sources_found: bool) -> str:
        """
        Génère une réponse factuelle stricte à partir du contexte fourni.
        """
        logger.info(f"Génération de réponse avec {self.model}")
        
        # 1. Vérification stricte: Si aucune source n'a été trouvée et que le système
        # est configuré pour exiger des sources (cas de l'Ambassade).
        from app.security.input_validation import InputValidator
        is_conversational = InputValidator.is_conversational(query)
        
        if not sources_found and not is_conversational:
            msg = OutputValidator.get_rejection_message()
            AuditLogger.log_interaction(query, False, len(msg), blocked=True, flag="NO_SOURCES", response_text=msg)
            return msg

        # 2. Préparation du prompt système conditionné
        system_content = SYSTEM_PROMPT.format(context=context, question=query)
        
        if self.is_mock:
            # Mode mock pour développement local sans API payante
            response_text = f"Ceci est une réponse simulée (MOCK) basée sur le contexte : {context[:50]}..."
            AuditLogger.log_interaction(query, True, len(response_text), blocked=False, flag="MOCK", response_text=response_text)
            return response_text

        # 3. Appel à l'API Mistral
        try:
            messages = create_messages(system_content, query)
            
            chat_response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=0.0, # Température à 0 pour maximiser le factuel
                max_tokens=1000,
            )
            
            response_text = chat_response.choices[0].message.content
            
            # 4. Validation post-génération
            if not OutputValidator.validate_response(response_text, sources_found):
                logger.warning("La réponse a échoué à la validation de sortie.")
                msg = OutputValidator.get_rejection_message()
                AuditLogger.log_interaction(query, True, len(msg), blocked=True, flag="BAD_OUTPUT", response_text=msg)
                return msg
                
            # Log successful response with correct token usage
            token_count = 0
            if hasattr(chat_response, 'usage') and chat_response.usage:
                token_count = chat_response.usage.total_tokens
                
            AuditLogger.log_interaction(query, True, len(response_text), blocked=False, flag="SUCCESS", token_used=token_count, response_text=response_text)
            return response_text
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API Mistral: {e}")
            msg = "Une erreur technique est survenue lors de la génération de la réponse. Veuillez réessayer plus tard."
            AuditLogger.log_interaction(query, True, len(msg), blocked=True, flag="API_ERROR", response_text=msg)
            return msg

    def rewrite_query(self, query: str, history: list) -> str:
        """
        Réécrit la requête en utilisant l'historique pour résoudre les coréférences 
        (ex: 'Et pour un enfant ?' -> 'Quels sont les documents pour le visa d'un enfant ?')
        Utilisé pour le système RAG, avec un coût API très faible.
        """
        if not history: 
            return query
            
        logger.info("Reformulation de la requête avec prise en compte de l'historique...")
        
        hist_text = ""
        # On limite aux 4 derniers messages (2 interactions Q/A) pour maîtriser le coût
        for msg in history[-4:]: 
            role = "Usager" if msg["role"] == "user" else "Assistant"
            content_snippet = msg['content'][:300] + "..." if len(msg['content']) > 300 else msg['content']
            hist_text += f"{role}: {content_snippet}\n"
            
        system_msg = "Tu es un spécialiste de la reformulation factuelle. Ton rôle est de lire l'historique court de la conversation et de réécrire l'ultime question de l'usager sans jamais y répondre. La nouvelle question doit se comprendre 100% seule, en y réintégrant le sujet dont vous parliez (ex: passeport, visa, tarif). Si la question est déjà claire et indépendante, recopie-la à l'identique. Ne dis JAMAIS 'Voici la reformulation', renvoie uniquement la phrase interrogative finale."
        user_prompt = f"Historique:\n{hist_text}\nQuestion actuelle à reformuler : {query}\n\nReformulation directe :"
        
        messages = create_messages(system_msg, user_prompt)
        
        try:
            # On utilise de préférence mistral-small-latest si un modèle lourd est configuré, pour baisser le coût de cette mini-étape
            rewrite_model = "mistral-small-latest" if "large" in self.model.lower() else self.model
                
            response = self.client.chat.complete(
                model=rewrite_model,
                messages=messages,
                temperature=0.0,
                max_tokens=60
            )
            rewritten = response.choices[0].message.content.strip(" \"'\n")
            logger.info(f"Requête reformulée : '{query}' -> '{rewritten}'")
            return rewritten
        except Exception as e:
            logger.error(f"Erreur de reformulation (RAG fallback activé): {e}")
            return query

    def generate_response_stream(self, query: str, context: str, sources_found: bool, history: list = None):
        """
        Génère une réponse factuelle stricte avec un rendu en streaming (optimisation des performances perçues).
        """
        logger.info(f"Génération de réponse en streaming avec {self.model}")
        
        from app.security.input_validation import InputValidator
        is_conversational = InputValidator.is_conversational(query)
        
        if not sources_found and not is_conversational:
            msg = OutputValidator.get_rejection_message()
            AuditLogger.log_interaction(query, False, len(msg), blocked=True, flag="NO_SOURCES", response_text=msg)
            yield msg
            return

        system_content = SYSTEM_PROMPT.format(context=context, question=query)
        
        if self.is_mock:
            response_text = f"Ceci est une réponse simulée (MOCK) en streaming basée sur le contexte fourni..."
            import time
            for word in response_text.split():
                yield word + " "
                time.sleep(0.05)
            AuditLogger.log_interaction(query, True, len(response_text), blocked=False, flag="MOCK", response_text=response_text)
            return

        try:
            if history and len(history) > 0:
                # Injecter les 4 derniers messages originaux pour que l'IA ait le contexte sans surcharger les tokens
                recent_history = history[-4:]
                messages = create_messages_with_history(system_content, recent_history, query)
            else:
                messages = create_messages(system_content, query)
            
            chat_stream = self.client.chat.stream(
                model=self.model,
                messages=messages,
                temperature=0.0,
                max_tokens=1000,
            )
            
            full_response = ""
            for chunk in chat_stream:
                delta = None
                if hasattr(chunk, 'data') and hasattr(chunk.data, 'choices'):
                    delta = chunk.data.choices[0].delta
                elif hasattr(chunk, 'choices'):
                    delta = chunk.choices[0].delta
                    
                if delta and delta.content:
                    full_response += delta.content
                    yield delta.content
                    
            if not OutputValidator.validate_response(full_response, sources_found):
                logger.warning("La réponse générée a échoué à la validation a posteriori.")
                AuditLogger.log_interaction(query, True, len(full_response), blocked=True, flag="BAD_OUTPUT_STREAM", response_text=full_response)
            else:
                AuditLogger.log_interaction(query, True, len(full_response), blocked=False, flag="SUCCESS_STREAM", response_text=full_response)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API Mistral (streaming): {e}")
            msg = "Une erreur technique est survenue lors de la génération de la réponse. Veuillez réessayer plus tard."
            AuditLogger.log_interaction(query, True, len(msg), blocked=True, flag="API_ERROR", response_text=msg)
            yield msg
