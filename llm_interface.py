import json
import os
import yaml
from typing import Dict, List, Optional, Union, Any

from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from loguru import logger


class LLMInterface:
    """
    The LLMInterface class provides an interface for interacting with a Language Model (LLM).
    It allows setting the role, configuring the LLM, sending input to the LLM, and retrieving the LLM's response.

    Attributes:
        prompt_manager (PromptManager): The PromptManager instance for managing prompt configurations.
        role (Optional[str]): The current role set for the LLM interface.
        llm (Optional[ChatOpenAI]): The ChatOpenAI instance for interacting with the LLM.
        system_prompt (Optional[str]): The system prompt template for the current role.
        conversation_history (List[Union[HumanMessage, AIMessage]]): The conversation history.
        verbose (bool): Flag to enable verbose logging.

    Methods:
        __init__(self, json_file_path: str, verbose: bool = False)

        set_role(self, role: str) -> bool:

        interact(self, input_text: str, **kwargs) -> Optional[str]:

        get_current_role(self) -> Optional[str]:

        get_available_roles(self) -> List[str]:

        get_conversation_history(self) -> List[Dict[str, str]]:

        clear_memory(self) -> None:
    """

    def __init__(self, config_file_path: str, verbose: bool = False):
        """
        Initialize the LLMInterface with configurations from a JSON file.

        Args:
            config_file_path (str): Path to the JSON file containing prompt and LLM configurations.
            verbose (bool): Flag to enable verbose logging. Defaults to False.
        """
        self.config_file_path = config_file_path
        self.prompts: Dict[str, Dict[str, Any]] = {}
        self.load_prompts()
        self.role: Optional[str] = None
        self.llm: Optional[ChatOpenAI] = None
        self.system_prompt: Optional[str] = None
        self.conversation_history: List[Union[HumanMessage, AIMessage]] = []
        self.verbose: bool = verbose
        self.interaction_string = None

    def load_prompts(self):
        with open(self.config_file_path, "r") as file:
            data = yaml.safe_load(file)
            self.prompts = data.get("prompts", {})

    def get_prompt_config(self, role: str) -> Optional[Dict[str, Any]]:
        return self.prompts.get(role)

    def get_prompt_template(self, role: str) -> Optional[str]:
        prompt_config = self.get_prompt_config(role)
        if prompt_config:
            return prompt_config.get("template")
        return None

    def get_llm_config(self, role: str) -> Optional[Dict[str, Any]]:
        with open(self.config_file_path, "r") as file:
            data = yaml.safe_load(file)
            llms = data.get("llms", {})
            return llms.get(role)

    def get_interaction_template(self, role: str) -> Optional[List[Dict[str, Any]]]:
        with open(self.config_file_path, "r") as file:
            data = yaml.safe_load(file)
            interactions = data.get("interaction_templates", {})
            role_interactions = interactions.get(role)
            if role_interactions:
                return role_interactions.get("templates")
        return None

    def get_available_roles(self) -> List[str]:
        return list(self.prompts.keys())

    def set_role(self, role: str) -> bool:
        """
        Set the current role and configure the LLM accordingly.

        This method sets up the LLM and prompt template for the specified role.
        It uses the configurations from the JSON file loaded by the PromptManager.

        Args:
            role (str): The role to set for the LLM interface.

        Returns:
            bool: True if the role was successfully set, False otherwise.
        """
        self.role = role
        self.system_prompt = self.get_prompt_template(role)
        self.interaction_template = self.get_interaction_template(role)
        llm_config = self.get_llm_config(role)

        if llm_config["local"]:
            os.environ["OPENAI_API_KEY"] = "local_key"
            os.environ["OPENAI_API_BASE"] = "http://localhost:1234/v1"

        if self.system_prompt and llm_config:
            callbacks = [StdOutCallbackHandler()] if self.verbose else None
            self.llm = ChatOpenAI(
                model_name=llm_config["model_name"],
                callbacks=callbacks,
                **llm_config["params"],
            )
            self.conversation_history = []  # Clear history when changing roles
            return True
        else:
            logger.opt(exception=True).error(
                f"Role '{role}' not found in the configuration file."
            )
            return False

    def interact(self, **kwargs) -> Optional[str]:
        """
        Interact with the LLM using the current role and configuration.

        This method sends the input to the LLM and returns its response. It handles
        the necessary formatting of inputs based on the current prompt template and
        includes the conversation history.

        Args:

            **kwargs: Additional keyword arguments required by the prompt template.

        Returns:
            Optional[str]: The LLM's response, or None if an error occurred.
        """

        if not self.llm or not self.system_prompt:
            logger.opt(exception=True).error("LLM or system prompt not configured.")
            return None

        try:
            for template in self.interaction_template:
                if all(key in kwargs.keys() for key in template["required_keys"]):
                    self.interaction_string = template["template"]
                    input_text = self.interaction_string.format(**kwargs)
                    break
        except KeyError:
            logger.opt(exception=True).error(
                f"Template not found for the given arguments: {kwargs}"
            )

        try:
            messages = (
                [SystemMessage(content=self.system_prompt)]
                + self.conversation_history
                + [HumanMessage(content=input_text)]
            )

            if self.verbose:
                logger.info("\n--- Sending to LLM ---")
                logger.info(json.dumps([m.dict() for m in messages], indent=2))

            # Get the response from the LLM
            ai_message = self.llm.invoke(messages)

            if self.verbose:
                logger.info("\n--- Received from LLM ---")
                logger.info(json.dumps(ai_message.dict(), indent=2))

            # Update the conversation history
            self.conversation_history.extend(
                [HumanMessage(content=input_text), ai_message]
            )

            return ai_message.content
        except Exception as e:
            logger.opt(exception=True).error(f"Error interacting with LLM: {e}.")
            return None

    def get_current_role(self) -> Optional[str]:
        """
        Get the current role of the LLM interface.

        Returns:
            Optional[str]: The current role, or None if no role is set.
        """
        return self.role

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Retrieve the conversation history.

        Returns:
            List[Dict[str, str]]: A list of dictionaries representing the conversation history.
            Each dictionary contains 'role' (either 'human' or 'ai') and 'content' keys.
        """
        return [
            {
                "role": "human" if isinstance(msg, HumanMessage) else "ai",
                "content": msg.content,
            }
            for msg in self.conversation_history
        ]

    def clear_memory(self) -> None:
        """
        Clear the conversation history.
        """
        self.conversation_history = []
        logger.info("Conversation history cleared.")


# Usage example
if __name__ == "__main__":
    # Set up environment variables for the OpenAI API
    from dotenv import load_dotenv

    load_dotenv()

    # Initialize the LLMInterface with the configuration file and verbose logging
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
