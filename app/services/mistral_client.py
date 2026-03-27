try:
    # Mistral >= 1.0.0 (top level export)
    from mistralai import Mistral as MistralClientClass
except ImportError:
    try:
        # Mistral >= 1.0.0 (internal speakeasy structure, e.g. 2.1.3)
        from mistralai.client import Mistral as MistralClientClass
    except ImportError:
        # Mistral < 1.0.0
        from mistralai.client import MistralClient as MistralClientClass

def create_messages(sys_content, user_content):
    if MistralClientClass.__name__ == "MistralClient":
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


from app.prompts.system_prompt import SYSTEM_PROMPT
from app.security.secrets_manager import SecretsManager
from app.security.output_validation import OutputValidator
from app.security.audit_logger import AuditLogger
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class MistralChatClient:
    """Client pour interagir avec l'API de chat Mistral."""
    
    def __init__(self):
        # Initialisation du client natif Mistral
        try:
            self.api_key = SecretsManager.get_mistral_api_key()
            self.model = SecretsManager.get_chat_model()
            self.client = MistralClientClass(api_key=self.api_key)
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
