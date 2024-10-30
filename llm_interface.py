import json
import os
from typing import Any, Dict, List, Optional, Union

import yaml
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from loguru import logger


class LLMInterface:
    """
    Provides an interface for interacting with a Language Model (LLM).
    Allows setting the role, configuring the LLM, sending input, and retrieving responses.

    Attributes:
        config_file_path (str): Path to the YAML configuration file.
        config_data (Dict[str, Any]): Loaded configuration data.
        role (Optional[str]): Current role set for the interface.
        llm (Optional[ChatOpenAI]): ChatOpenAI instance for LLM interaction.
        system_prompt (Optional[str]): System prompt template for the current role.
        interaction_template (Optional[List[Dict[str, Any]]]): Interaction templates for the current role.
        conversation_history (List[Union[HumanMessage, AIMessage]]): Conversation history.
        verbose (bool): Flag to enable verbose logging.
        interaction_string (Optional[str]): Formatted interaction string.
    """

    def __init__(self, config_file_path: str, verbose: bool = False):
        with open(config_file_path, "r") as file:
            self.config_data = yaml.safe_load(file)
        self.prompts = self.config_data.get("prompts", {})
        self.role: Optional[str] = None
        self.llm: Optional[ChatOpenAI] = None
        self.system_prompt: Optional[str] = None
        self.interaction_template: Optional[List[Dict[str, Any]]] = None
        self.conversation_history: List[Union[HumanMessage, AIMessage]] = []
        self.verbose: bool = verbose
        self.interaction_string: Optional[str] = None

    def get_prompt_config(self, role: str) -> Optional[Dict[str, Any]]:
        return self.prompts.get(role)

    def get_prompt_template(self, role: str) -> Optional[str]:
        prompt_config = self.get_prompt_config(role)
        if prompt_config:
            return prompt_config.get("template")
        return None

    def get_llm_config(self, role: str) -> Optional[Dict[str, Any]]:
        llms = self.config_data.get("llms", {})
        return llms.get(role)

    def get_interaction_template(self, role: str) -> Optional[List[Dict[str, Any]]]:
        interactions = self.config_data.get("interaction_templates", {})
        role_interactions = interactions.get(role)
        if role_interactions:
            return role_interactions.get("templates")
        return None

    def get_available_roles(self) -> List[str]:
        return list(self.prompts.keys())

    def set_role(self, role: str) -> bool:
        self.role = role
        self.system_prompt = self.get_prompt_template(role)
        self.interaction_template = self.get_interaction_template(role)
        llm_config = self.get_llm_config(role)

        if not llm_config:
            logger.error(f"LLM configuration for role '{role}' not found.")
            return False

        if llm_config.get("local"):
            os.environ["OPENAI_API_KEY"] = "local_key"
            os.environ["OPENAI_API_BASE"] = "http://localhost:1234/v1"

        if self.system_prompt:
            callbacks = [StdOutCallbackHandler()] if self.verbose else None
            self.llm = ChatOpenAI(
                model_name=llm_config["model_name"],
                callbacks=callbacks,
                **llm_config["params"],
            )
            self.conversation_history = []
            return True
        else:
            logger.error(f"System prompt for role '{role}' not found.")
            return False

    def interact(self, **kwargs) -> Optional[str]:
        if not self.llm or not self.system_prompt:
            logger.error("LLM or system prompt not configured.")
            return None

        try:
            for template in self.interaction_template:
                if all(key in kwargs for key in template["required_keys"]):
                    self.interaction_string = template["template"]
                    input_text = self.interaction_string.format(**kwargs)
                    break
            else:
                logger.error(
                    "No matching interaction template found for the given arguments."
                )
                return None
        except KeyError as e:
            logger.exception(f"Missing required key in interaction template: {e}")
            return None

        messages = (
            [SystemMessage(content=self.system_prompt)]
            + self.conversation_history
            + [HumanMessage(content=input_text)]
        )

        if self.verbose:
            logger.info("\n--- Sending to LLM ---")
            logger.info(json.dumps([m.dict() for m in messages], indent=2))

        try:
            ai_message = self.llm.invoke(messages)
            if self.verbose:
                logger.info("\n--- Received from LLM ---")
                logger.info(json.dumps(ai_message.dict(), indent=2))

            self.conversation_history.extend(
                [HumanMessage(content=input_text), ai_message]
            )
            return ai_message.content
        except Exception as e:
            logger.exception(f"Error interacting with LLM: {e}")
            return None

    def get_current_role(self) -> Optional[str]:
        return self.role

    def get_conversation_history(self) -> List[Dict[str, str]]:
        return [
            {
                "role": "human" if isinstance(msg, HumanMessage) else "ai",
                "content": msg.content,
            }
            for msg in self.conversation_history
        ]

    def clear_memory(self) -> None:
        self.conversation_history = []
        logger.info("Conversation history cleared.")


# Usage example
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    json_file_path = "agent_config.yml"
    agent = LLMInterface(json_file_path, verbose=False)

    logger.info(f"Available roles: {agent.get_available_roles()}")

    if agent.set_role("mutator"):
        response = agent.interact(
            concepts="two sum",
            difficulty_level="easy",
        )
        logger.info(f"Question Designer response: {response}")

        print(agent.get_conversation_history())
